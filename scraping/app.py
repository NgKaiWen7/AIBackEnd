from __future__ import annotations

import asyncio
import logging
import os
import queue
import shutil
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException
from playwright.sync_api import Page, sync_playwright
from pydantic import BaseModel


class MemoryConcept(BaseModel):
    id: UUID
    prompt: str


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
account_queues = {account["name"]: queue.Queue() for account in ACCOUNTS}
worker_ready = {account["name"]: threading.Event() for account in ACCOUNTS}
worker_errors = {}
DATA_DIR = Path("./browser_agent_output")
PROMPT_TIMEOUT_SECONDS = int(os.getenv("GEMINI_PROMPT_TIMEOUT", "300"))
RETRY_TIMEOUT_SECONDS = int(os.getenv("GEMINI_RETRY_TIMEOUT", "600"))
DOWNLOAD_BUTTON_SELECTOR = (
    'md-icon-button.download-button[data-aria-label="Download image"]'
)
BACKEND_URL = "http://192.168.0.180:8000"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SESSION_MAX_SECONDS = 3600

job_queue: queue.Queue[list[MemoryConcept] | None] = queue.Queue()
worker_start_error: BaseException | None = None
worker_thread: threading.Thread | None = None


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
        try:
            page.get_by_text(name).first.click(timeout=10_000)
        except Exception:
            logger.info("Account selection was not required")

        worker_ready[name].set()
        logger.info("[%s] Browser session started", name)

        while True:
            if time.monotonic() - started > session_seconds:
                logger.info("[%s] Session age limit reached, recycling browser", name)
                return False

            try:
                concepts = job_queue.get(timeout=5)
            except queue.Empty:
                continue

            try:
                if concepts is None:
                    return True
                for concept in concepts:
                    generate_image(page=page, concept=concept)
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

    for account in ACCOUNTS:
        thread = threading.Thread(
            target=playwright_worker,
            args=(account,),
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
        # Send a shutdown sentinel to each independent queue.
        for account in ACCOUNTS:
            account_queues[account["name"]].put(None)

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
    description="Upload JSON and generate images in the background.",
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
        "upload_endpoint": "POST /upload",
        "docs": "/docs",
    }


@app.get("/queue")
async def get_queue() -> dict[str, int]:
    """Return the current image-generation queue statistics."""

    with job_queue.mutex:
        jobs = list(job_queue.queue)

    return {
        "queue_size": len(jobs),
        "prompt_count": sum(len(job) for job in jobs),
    }


@app.post("/generate", status_code=202)
async def generate_cards(request: list[MemoryConcept]) -> dict[str, Any]:
    """Validate and queue concepts for background image generation."""
    if not request:
        raise HTTPException(
            status_code=422,
            detail="At least one concept is required.",
        )

    for req in request:
        job_queue.put([req])

    return {
        "accepted": True,
        "concepts": len(request),
        "card_ids": [str(req.id) for req in request],
    }


@app.post("/upload-generated-images")
async def upload_generated_images() -> dict:
    """Upload generated images and delete local files after successful upload."""

    if not DATA_DIR.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Image directory not found: {DATA_DIR.resolve()}",
        )

    images = [
        path
        for path in DATA_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    uploaded = []
    failed = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        for image_path in images:
            try:
                card_id = UUID(image_path.stem)

                with image_path.open("rb") as image_file:
                    response = await client.put(
                        f"{BACKEND_URL}/memory-card/cards/{card_id}/image",
                        files={
                            "file": (
                                image_path.name,
                                image_file,
                                "application/octet-stream",
                            )
                        },
                    )

                response.raise_for_status()

                # Delete only after the backend confirms success.
                image_path.unlink()
                uploaded.append(str(card_id))

            except Exception as exc:
                logger.exception("Failed to upload image: %s", image_path)
                failed.append(
                    {
                        "file": str(image_path),
                        "error": str(exc),
                    }
                )

    return {
        "total_images": len(images),
        "uploaded_count": len(uploaded),
        "failed_count": len(failed),
        "uploaded": uploaded,
        "failed": failed,
    }
