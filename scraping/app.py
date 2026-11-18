from __future__ import annotations

import asyncio
import logging
import os
import queue
import shutil
import threading
import time
from concurrent.futures import Future
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from playwright.sync_api import Page, sync_playwright
from pydantic import BaseModel


class MemoryConcept(BaseModel):
    id: UUID
    prompt: str


@dataclass(slots=True)
class GenerationTask:
    concept: MemoryConcept
    completion: Future[bool]


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gemini_memory_card_service")

URL = "https://gemini.rakyatdigital.gov.my/"
ACCOUNTS = [
    {"name": "NG KAI WEN", "profile_dir": Path("./my_profile")},
    {"name": "NG YONG SHENG", "profile_dir": Path("./ys_profile")},
]
worker_ready = {account["name"]: threading.Event() for account in ACCOUNTS}
worker_errors = {}
DATA_DIR = Path(__file__).resolve().parent / "browser_agent_output"
PROMPT_TIMEOUT_SECONDS = int(os.getenv("GEMINI_PROMPT_TIMEOUT", "300"))
DOWNLOAD_BUTTON_SELECTOR = (
    'md-icon-button.download-button[data-aria-label="Download image"]'
)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SESSION_MAX_SECONDS = 60 * 60

job_queue: queue.Queue[GenerationTask | None] = queue.Queue()


def clear_profile_cache(profile_dir: Path) -> None:
    """Delete regenerable caches only (keeps cookies/login). Browser must be closed."""
    for rel in (
        "Default/Cache",
        "Default/Code Cache",
        "Default/GPUCache",
        "Default/Service Worker/CacheStorage",
        "ShaderCache",
        "GrShaderCache",
    ):
        shutil.rmtree(profile_dir / rel, ignore_errors=True)


def submit_prompt(page: Page, prompt: str) -> None:
    """Submit a prompt through the existing Gemini ProseMirror editor."""
    editor = page.locator("ucs-prosemirror-editor#agent-search-prosemirror-editor")
    editor.click()
    try:
        editor.fill(prompt)
    except Exception:
        # Some ProseMirror editors do not expose a fill-compatible surface.
        page.keyboard.insert_text(prompt)
    page.keyboard.press("Enter")


def downloads(page: Page, card_id: UUID) -> bool:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    buttons = page.locator(DOWNLOAD_BUTTON_SELECTOR)
    if buttons.count() == 0:
        return False

    with page.expect_download(timeout=60_000) as download_info:
        buttons.first.evaluate("(el) => el.click()")
    download = download_info.value

    suffix = Path(download.suggested_filename).suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        suffix = ".png"

    tmp_path = DATA_DIR / f"{card_id}{suffix}.part"
    final_path = DATA_DIR / f"{card_id}{suffix}"
    try:
        download.save_as(tmp_path)  # raises if the download was cancelled
        if tmp_path.stat().st_size == 0:
            raise RuntimeError(f"Empty download: {tmp_path}")
        tmp_path.replace(final_path)  # atomic, so the uploader never sees partial files
    finally:
        download.delete()  # frees Playwright's temp copy
        tmp_path.unlink(missing_ok=True)
    return True


def start_new_chat(page: Page) -> None:
    """Leave the finished conversation and open a fresh chat."""
    page.keyboard.press("Escape")
    page.get_by_role("link", name="New chat").click(timeout=15000)


def generate_image(page: Page, concept: MemoryConcept) -> bool:
    """Generate and save one card image, retrying once on failure."""
    for attempt in range(1, 3):
        start_new_chat(page)
        try:
            logger.info("Generating card %s (attempt %s/2)", concept.id, attempt)
            submit_prompt(page, concept.prompt)
            deadline = time.monotonic() + PROMPT_TIMEOUT_SECONDS
            while time.monotonic() < deadline:
                if downloads(page, concept.id):
                    return True
                page.wait_for_timeout(1000)
            logger.warning("Timed out generating card %s", concept.id)
        except Exception:
            logger.exception(
                "Generation attempt %s failed for card %s", attempt, concept.id
            )
        if attempt == 1:
            try:
                page.reload(wait_until="domcontentloaded")
                page.bring_to_front()
            except Exception:
                logger.exception("Could not reload the generation page")
        try:
            start_new_chat(page)
        except Exception:
            logger.exception("Could not reset the generation chat")
    logger.error("Card %s failed after retry", concept.id)
    start_new_chat(page)
    return False


def log_visible_page_text(page: Page, account_name: str) -> None:
    """Log the text Playwright can see when account selection fails."""
    try:
        visible_text = page.locator("body").inner_text(timeout=5_000).strip()
        logger.error(
            "[%s] Account selector failed at %s. Visible page text:\n%s",
            account_name,
            page.url,
            visible_text[:10_000] or "<no visible text>",
        )
    except Exception:
        logger.exception("[%s] Could not collect visible page text", account_name)


def run_session(playwright, account: dict, session_seconds: int) -> bool:
    """Run one browser lifetime. Returns True to shut down, False to restart the browser."""
    name = account["name"]
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=account["profile_dir"],
        headless=False,
        accept_downloads=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",  # matters a lot on Linux/Docker
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-session-crashed-bubble",
            "--disk-cache-size=104857600",  # cap HTTP cache at ~100MB],
        ],
    )
    started = time.monotonic()
    try:
        page = context.pages[0] if context.pages else context.new_page()
        page.bring_to_front()
        page.goto(URL, wait_until="domcontentloaded")
        account_selector = page.get_by_text(name).first
        try:
            account_selector.hover(timeout=20_000)
            account_selector.click(timeout=20_000)
        except Exception:
            log_visible_page_text(page, name)
            raise

        worker_ready[name].set()
        logger.info("[%s] Browser session started", name)

        while True:
            if time.monotonic() - started > session_seconds:
                logger.info("[%s] Session age limit reached, recycling browser", name)
                return False

            try:
                task = job_queue.get(timeout=5)
            except queue.Empty:
                continue

            try:
                if task is None:
                    return True
                success = generate_image(page=page, concept=task.concept)
                task.completion.set_result(success)
            except BaseException as exc:
                if task is not None and not task.completion.done():
                    task.completion.set_exception(exc)
                raise
            finally:
                job_queue.task_done()
    finally:
        context.close()  # kills Chromium and frees Playwright's temp downloads


def playwright_worker(account: dict, index: int = 0) -> None:
    name = account["name"]
    account["profile_dir"].mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Stagger accounts so both browsers never restart at the same moment
    session_seconds = SESSION_MAX_SECONDS + index * 900
    while True:
        try:
            with sync_playwright() as playwright:
                shutdown = run_session(playwright, account, session_seconds)
            if shutdown:
                return
        except Exception as exc:
            logger.exception("[%s] Browser session failed", name)
            if not worker_ready[name].is_set():      # failed on first start: report it
                worker_errors[name] = exc
                worker_ready[name].set()
                return
            time.sleep(10)                           # crashed later: back off and relaunch

        clear_profile_cache(account["profile_dir"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start one persistent Playwright worker per account."""
    workers = []

    for index, account in enumerate(ACCOUNTS):
        thread = threading.Thread(
            target=playwright_worker,
            args=(account, index),
            name=f"image-worker-{account['name']}",
            daemon=True,
        )
        thread.start()
        workers.append(thread)

    try:
        # Wait until every worker reports startup success or failure.
        await asyncio.gather(
            *[
                asyncio.to_thread(worker_ready[account["name"]].wait)
                for account in ACCOUNTS
            ]
        )

        failed = {name: error for name, error in worker_errors.items()}

        if failed:
            raise RuntimeError(
                f"Failed to initialize account workers: {', '.join(failed)}"
            ) from next(iter(failed.values()))

        logger.info("All account workers are ready")
        yield

    finally:
        # Send one shutdown sentinel for each worker consuming the shared queue.
        for _ in workers:
            job_queue.put(None)

        # Wait for workers without blocking the FastAPI event loop.
        await asyncio.gather(
            *[asyncio.to_thread(thread.join, 30) for thread in workers]
        )

        for thread in workers:
            if thread.is_alive():
                logger.warning(
                    "%s is still running during shutdown",
                    thread.name,
                )


app = FastAPI(
    title="Gemini Memory Card Image Service",
    version="1.0.0",
    description="Generate images and wait for every requested file to finish.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/")
def root():
    return {
        "service": "Gemini Memory Card Image Service",
        "status": "running",
        "generation_endpoint": "POST /generate",
        "image_endpoint": "GET /generated-images/{image_id}",
        "docs": "/docs",
    }


@app.post("/generate")
async def generate_cards(request: list[MemoryConcept]) -> dict[str, Any]:
    """Wait until every requested image has been written to disk."""
    if not request:
        raise HTTPException(
            status_code=422,
            detail="At least one concept is required.",
        )

    tasks = [
        GenerationTask(concept=concept, completion=Future())
        for concept in request
    ]
    for task in tasks:
        job_queue.put(task)

    results = await asyncio.gather(
        *(asyncio.wrap_future(task.completion) for task in tasks),
        return_exceptions=True,
    )
    generated = [
        str(task.concept.id)
        for task, result in zip(tasks, results)
        if result is True
    ]
    failed = [
        str(task.concept.id)
        for task, result in zip(tasks, results)
        if result is not True
    ]

    return {
        "completed": True,
        "requested_count": len(request),
        "generated_count": len(generated),
        "failed_count": len(failed),
        "generated": generated,
        "failed": failed,
    }


def find_generated_images(image_id: UUID) -> list[Path]:
    """Find completed files for an exact card or chunk UUID."""
    if not DATA_DIR.is_dir():
        return []

    return sorted(
        (
            path
            for path in DATA_DIR.rglob(f"{image_id}.*")
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


@app.get("/generated-images/{image_id}", response_class=FileResponse)
async def get_generated_image(image_id: UUID) -> FileResponse:
    """Return the newest completed image matching the requested UUID."""
    images = await asyncio.to_thread(find_generated_images, image_id)
    if not images:
        raise HTTPException(status_code=404, detail="Generated image not found")

    image_path = images[0]
    return FileResponse(
        image_path,
        filename=image_path.name,
        headers={"X-Image-Extension": image_path.suffix.lower()},
    )


@app.delete("/generated-images/{image_id}")
async def delete_generated_image(image_id: UUID) -> dict[str, int | str]:
    """Delete an image only after the backend confirms it was stored."""
    images = await asyncio.to_thread(find_generated_images, image_id)
    if not images:
        raise HTTPException(status_code=404, detail="Generated image not found")

    for image_path in images:
        await asyncio.to_thread(image_path.unlink)

    return {"image_id": str(image_id), "deleted_count": len(images)}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
