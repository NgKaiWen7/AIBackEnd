from __future__ import annotations

import asyncio
import logging
import os
import queue
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


class MemoryCardRequest(BaseModel):
    concepts: list[MemoryConcept]


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gemini_memory_card_service")

URL = "https://gemini.rakyatdigital.gov.my/"
PROFILE = Path("./my_profile")
DATA_DIR = Path("./browser_agent_output")
PROMPT_TIMEOUT_SECONDS = int(os.getenv("GEMINI_PROMPT_TIMEOUT", "300"))
RETRY_TIMEOUT_SECONDS = int(os.getenv("GEMINI_RETRY_TIMEOUT", "600"))
DOWNLOAD_BUTTON_SELECTOR = (
    'md-icon-button.download-button[data-aria-label="Download image"]'
)
BACKEND_URL = "http://192.168.0.180:8000"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

job_queue: queue.Queue[list[MemoryConcept] | None] = queue.Queue()
worker_ready = threading.Event()
worker_start_error: BaseException | None = None
worker_thread: threading.Thread | None = None


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
    """Download an image and save it using the card UUID as its filename."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    buttons = page.locator(DOWNLOAD_BUTTON_SELECTOR)
    count = buttons.count()
    for button_index in range(count):
        button = buttons.nth(button_index)
        with page.expect_download() as download_info:
            button.evaluate("(el) => el.click()")
        download = download_info.value
        suffix = Path(download.suggested_filename).suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
            suffix = ".png"
        save_path = DATA_DIR / f"{card_id}{suffix}"
        download.save_as(save_path)
        if not save_path.is_file() or save_path.stat().st_size == 0:
            raise RuntimeError(f"Downloaded file is missing or empty: {save_path}")
        logger.info("Saved image for card %s: %s", card_id, save_path)
        return True
    return False


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


def playwright_worker() -> None:
    """Own the persistent browser and process queued concepts."""
    global worker_start_error

    try:
        PROFILE.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE.resolve()),
                headless=False,
                accept_downloads=True,
                args=["--disable-blink-features=AutomationControlled"],
            )

            try:
                page = context.pages[0] if context.pages else context.new_page()

                keepalive_page = context.new_page()
                keepalive_page.goto("about:blank")

                page.bring_to_front()
                page.goto(URL, wait_until="domcontentloaded")
                try:
                    page.get_by_text("NG KAI WEN").first.click(timeout=10000)
                except Exception:
                    logger.info("Account selection was not required")
                worker_ready.set()
                logger.info("Image generation worker ready")
                while True:
                    concepts = job_queue.get()
                    try:
                        if concepts is None:
                            break
                        for concept in concepts:
                            generate_image(page=page, concept=concept)
                    finally:
                        job_queue.task_done()
            finally:
                context.close()
    except BaseException as exc:
        worker_start_error = exc
        worker_ready.set()
        logger.exception("Playwright worker failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Do not accept HTTP requests until browser startup has completed."""
    global worker_thread

    worker_thread = threading.Thread(
        target=playwright_worker, name="playwright-generation-worker", daemon=True
    )
    worker_thread.start()

    await asyncio.to_thread(worker_ready.wait)

    if worker_start_error is not None:
        worker_thread.join(timeout=2)
        raise RuntimeError(
            "Could not initialize the Playwright browser. Check the terminal logs."
        ) from worker_start_error

    try:
        yield
    finally:
        # The single worker finishes any already-queued jobs before exiting.
        job_queue.put(None)
        await asyncio.to_thread(worker_thread.join, 30)
        if worker_thread.is_alive():
            logger.warning(
                "Playwright worker is still running during shutdown; "
                "an active generation may not finish before process exit."
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
    """Return the current image-generation queue size."""
    return {"queue_size": job_queue.qsize()}


@app.post("/generate", status_code=202)
async def generate_cards(request: MemoryCardRequest) -> dict[str, Any]:
    """Validate and queue concepts for background image generation."""

    if (
        worker_thread is None
        or not worker_thread.is_alive()
        or worker_start_error is not None
        or not worker_ready.is_set()
    ):
        raise HTTPException(
            status_code=503,
            detail="The Playwright generation worker is unavailable.",
        )

    concepts = request.concepts

    if not concepts:
        raise HTTPException(
            status_code=422,
            detail="At least one concept is required.",
        )

    job_queue.put(concepts)

    return {
        "accepted": True,
        "concepts": len(concepts),
        "card_ids": [str(concept.id) for concept in concepts],
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
                failed.append({
                    "file": str(image_path),
                    "error": str(exc),
                })

    return {
        "total_images": len(images),
        "uploaded_count": len(uploaded),
        "failed_count": len(failed),
        "uploaded": uploaded,
        "failed": failed,
    }
