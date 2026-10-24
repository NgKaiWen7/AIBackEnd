"""Gemini Memory Card Image Service.

A single-process FastAPI service that starts one persistent visible Playwright
browser during application startup. It accepts a JSON upload at POST /upload,
returns HTTP 202 after queueing the job, then generates and saves images in a
background worker.

Expected JSON schema:
{
    "topic": "...",
    "concepts": [
        {
            "title": "...",
            "content": "...",
            "image_prompt": "..."
        }
    ]
}

Run:
    uv run uvicorn app:app --host 127.0.0.1 --port 8000 --workers 1

The first startup opens a visible browser. Complete sign-in there, then press
Enter in the terminal. Set GEMINI_WAIT_FOR_LOGIN=0 to skip the terminal wait
when the persistent browser profile is already authenticated.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import queue
import re
import threading
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from playwright.sync_api import Page, Playwright, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gemini_memory_card_service")

URL = os.getenv(
    "GEMINI_CARD_URL",
    "https://gemini.rakyatdigital.gov.my/",
)
PROFILE = Path(os.getenv("GEMINI_PROFILE_DIR", "./my_profile"))
DATA_DIR = Path(os.getenv("GEMINI_CARD_DATA_DIR", "./browser_agent_output"))
MAX_JSON_BYTES = int(os.getenv("GEMINI_CARD_MAX_JSON_BYTES", str(10 * 1024 * 1024)))
PROMPT_TIMEOUT_SECONDS = int(os.getenv("GEMINI_PROMPT_TIMEOUT", "300"))
RETRY_TIMEOUT_SECONDS = int(os.getenv("GEMINI_RETRY_TIMEOUT", "600"))
WAIT_FOR_LOGIN = os.getenv("GEMINI_WAIT_FOR_LOGIN", "1").strip().lower() not in {
    "0",
    "false",
    "no",
    "off",
}

# Override this with GEMINI_DOWNLOAD_BUTTON_SELECTOR if the website's markup
# changes. The default targets controls whose accessible label/title contains
# "download" (case-insensitive).
DOWNLOAD_BUTTON_SELECTOR = 'md-icon-button.download-button[data-aria-label="Download image"]'

# Shared visual style for every card. Keep the card-specific teaching content
# and visual brief in each JSON concept's content and image_prompt fields.
STYLE_PROMPT = """
Create a polished, self-contained technical memory card for an experienced
software/AI engineer.

STYLE
- Professional technical editorial design.
- Clean background, restrained colors, and strong visual hierarchy.
- Large, readable title and clearly organized technical content.
- Use diagrams, annotated workflows, equations, tables, and code panels
  where they improve understanding.
- Prefer information-dense layouts with efficient use of space.
- Keep typography, spacing, colors, and visual language consistent across cards.
- Avoid decorative imagery, unrelated illustrations, clutter, and fake UI.

ACCURACY
- Preserve technical terminology, identifiers, code, SQL, operators,
  equations, and command syntax exactly.
- Do not invent APIs, results, examples, or technical claims.
- Explain only the supplied concept. Do not merge unrelated concepts.
- Make the card understandable independently of other cards.
""".strip()


# ---------------------------------------------------------------------------
# JSON schema validation and prompt construction
# ---------------------------------------------------------------------------


class CardSchemaError(ValueError):
    """Raised when an uploaded card JSON file does not match the expected schema."""


def validate_cards(data: Any) -> dict[str, Any]:
    """Validate the strict {topic, concepts[]} memory-card JSON schema."""
    if not isinstance(data, dict):
        raise CardSchemaError(
            "JSON root must be an object containing topic and concepts."
        )

    expected_root_keys = {"topic", "concepts"}
    actual_root_keys = set(data.keys())
    if actual_root_keys != expected_root_keys:
        missing = sorted(expected_root_keys - actual_root_keys)
        extra = sorted(actual_root_keys - expected_root_keys)
        details = []
        if missing:
            details.append(f"missing root keys: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected root keys: {', '.join(extra)}")
        raise CardSchemaError(
            "Root must contain only 'topic' and 'concepts' ("
            + "; ".join(details)
            + ")."
        )

    topic = data["topic"]
    if not isinstance(topic, str) or not topic.strip():
        raise CardSchemaError("'topic' must be a non-empty string.")

    concepts = data["concepts"]
    if not isinstance(concepts, list) or not concepts:
        raise CardSchemaError("'concepts' must be a non-empty array.")

    expected_concept_keys = {"title", "content", "image_prompt"}
    validated_concepts: list[dict[str, str]] = []

    for index, concept in enumerate(concepts, start=1):
        prefix = f"concepts[{index - 1}]"
        if not isinstance(concept, dict):
            raise CardSchemaError(f"{prefix} must be an object.")

        actual_keys = set(concept.keys())
        if actual_keys != expected_concept_keys:
            missing = sorted(expected_concept_keys - actual_keys)
            extra = sorted(actual_keys - expected_concept_keys)
            details = []
            if missing:
                details.append(f"missing keys: {', '.join(missing)}")
            if extra:
                details.append(f"unexpected keys: {', '.join(extra)}")
            raise CardSchemaError(
                f"{prefix} must contain only title, content, and image_prompt "
                f"(" + "; ".join(details) + ")."
            )

        validated: dict[str, str] = {}
        for field in ("title", "content", "image_prompt"):
            value = concept[field]
            if not isinstance(value, str) or not value.strip():
                raise CardSchemaError(f"{prefix}.{field} must be a non-empty string.")
            # Preserve the content as supplied; do not trim code or whitespace.
            validated[field] = value

        validated_concepts.append(validated)

    return {"topic": topic, "concepts": validated_concepts}

def build_prompts(data: dict) -> list[str]:
    """Build one standalone image-generation prompt per concept."""
    data = validate_cards(data)
    topic = data["topic"].strip()
    prompts = []

    for concept in data["concepts"]:
        prompt = f"""{STYLE_PROMPT}

TOPIC
{topic}

CARD TITLE
{concept["title"]}

CARD CONTENT
Preserve the technical information and code accurately.

{concept["content"]}

VISUAL EXPLANATION
Use this as the specific diagram or illustration brief.

{concept["image_prompt"]}

Render one finished technical memory card for this concept.
Use the supplied title, content, and visual explanation as the source of truth.
Make important technical details legible and ensure diagram labels match
the supplied content.

Return the finished image only, without accompanying text.
"""
        prompts.append(prompt)

    return prompts


# ---------------------------------------------------------------------------
# Gemini page interactions
# ---------------------------------------------------------------------------


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


def downloads(page: Page, output_dir: Path, prompt_index: int = 1) -> bool:
    """Click a visible download control and save its file to the job's images dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    buttons = page.locator(DOWNLOAD_BUTTON_SELECTOR)

    count = buttons.count()

    for button_index in range(count):
        button = buttons.nth(button_index)
        with page.expect_download() as download_info:
            button.evaluate("(el) => el.click()")
        download = download_info.value
        suggested_name = Path(download.suggested_filename).name
        filename = suggested_name or f"image_{button_index + 1}.png"
        # Ensure the output path stays a direct child of this job's directory.
        filename = re.sub(r"[^A-Za-z0-9._ -]+", "_", filename).strip(" .")
        if not filename:
            filename = f"image_{button_index + 1}.png"
        save_path = output_dir / (
            f"prompt_{prompt_index:03d}_download_{button_index + 1:02d}_{filename}"
        )
        download.save_as(save_path)
        if not save_path.is_file() or save_path.stat().st_size == 0:
            raise RuntimeError(f"Downloaded file is missing or empty: {save_path}")
        logger.info("Saved image: %s", save_path)
        return True

    return False


def start_new_chat(page: Page) -> None:
    """Leave the finished conversation and open a fresh chat."""
    page.keyboard.press("Escape")
    page.get_by_role("link", name="New chat").click(timeout=15000)


def generate_images_in_session(
    page: Page,
    prompts: list[str],
    output_dir: Path,
) -> dict[str, Any]:
    """Run the prompt loop using the already-open page; never create a browser."""
    output_dir.mkdir(parents=True, exist_ok=True)
    failed_prompts: list[tuple[int, str]] = []
    succeeded: set[int] = set()

    for index, prompt in enumerate(prompts, start=1):
        logger.info("Generating prompt %s/%s", index, len(prompts))
        success = False

        try:
            submit_prompt(page, prompt)
            deadline = time.monotonic() + PROMPT_TIMEOUT_SECONDS
            while not success and time.monotonic() < deadline:
                success = downloads(page, output_dir, index)

        except Exception:
            logger.exception("Prompt %s failed during initial generation", index)

        if success:
            succeeded.add(index)
        else:
            logger.warning(
                "Prompt %s timed out or failed; it will be retried once", index
            )
            failed_prompts.append((index, prompt))
            try:
                page.reload(wait_until="domcontentloaded")
                page.bring_to_front()
            except Exception:
                logger.exception("Could not reload the page after prompt %s", index)

        try:
            start_new_chat(page)
        except Exception:
            logger.exception("Could not start a new chat after prompt %s", index)
            try:
                page.reload(wait_until="domcontentloaded")
                page.bring_to_front()
            except Exception:
                logger.exception("Could not recover the page after prompt %s", index)

    retry_succeeded: list[int] = []
    failed_after_retry: list[int] = []

    for index, prompt in failed_prompts:
        logger.info("Retrying prompt %s", index)
        success = False

        try:
            submit_prompt(page, prompt)
            deadline = time.monotonic() + PROMPT_TIMEOUT_SECONDS

            while not success and time.monotonic() < deadline:
                success = downloads(page, output_dir, index)


        except Exception:
            logger.exception("Retry failed for prompt %s", index)

        if success:
            retry_succeeded.append(index)
            succeeded.add(index)
            logger.info("Prompt %s succeeded on retry", index)
        else:
            failed_after_retry.append(index)
            logger.error("Prompt %s failed after retry", index)

        try:
            start_new_chat(page)
        except Exception:
            logger.exception("Could not reset the page after retry %s", index)
            try:
                page.reload(wait_until="domcontentloaded")
                page.bring_to_front()
            except Exception:
                logger.exception("Could not recover the page after retry %s", index)

    result = {
        "total_prompts": len(prompts),
        "successful_prompts": len(succeeded),
        "initial_failures": len(failed_prompts),
        "retry_successes": len(retry_succeeded),
        "failed_after_retry": failed_after_retry,
        "image_directory": str(output_dir.resolve()),
    }
    logger.info("Generation result: %s", result)
    return result


# ---------------------------------------------------------------------------
# Background worker: Playwright is created and used on this thread only
# ---------------------------------------------------------------------------

job_queue: queue.Queue[dict[str, Any] | None] = queue.Queue()
worker_ready = threading.Event()
worker_start_error: BaseException | None = None
worker_thread: threading.Thread | None = None


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def playwright_worker() -> None:
    """Start the persistent browser, then consume upload jobs sequentially."""
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

                # Keep a second tab open as in the original runner.
                keepalive_page = context.new_page()
                keepalive_page.goto("about:blank")
                page.bring_to_front()
                page.goto(URL, wait_until="domcontentloaded")

                # Preserve the account-selection interaction from the original code.
                try:
                    page.get_by_text("NG KAI WEN").first.click(timeout=10000)
                except Exception:
                    logger.info(
                        "Account-selection text was not found/clickable; "
                        "continue with the page currently open."
                    )

                if WAIT_FOR_LOGIN:
                    input(
                        "\nWhen the Gemini website is ready, press Enter here "
                        "to start accepting uploads...\n"
                    )

                # Preload/warm the prompt construction code before FastAPI becomes ready.
                build_prompts(
                    {
                        "topic": "Startup warmup",
                        "concepts": [
                            {
                                "title": "Warmup",
                                "content": "Warmup example content.",
                                "image_prompt": "A simple technical diagram for warmup.",
                            }
                        ],
                    }
                )

                logger.info("Playwright initialized; background worker is ready.")
                worker_ready.set()

                while True:
                    job = job_queue.get()
                    try:
                        if job is None:
                            break

                        job_id = job["id"]
                        cards = job["cards"]
                        job_dir = Path(job["job_dir"])
                        image_dir = job_dir / "images"
                        image_dir.mkdir(parents=True, exist_ok=True)
                        job_state = {
                            "job_id": job_id,
                            "topic": cards["topic"],
                            "concepts": len(cards["concepts"]),
                            "status": "running",
                        }
                        _write_json(job_dir / "job.json", job_state)

                        logger.info(
                            "Starting job %s: topic=%r concepts=%s",
                            job_id,
                            cards["topic"],
                            len(cards["concepts"]),
                        )

                        try:
                            prompts = build_prompts(cards)
                            _write_json(job_dir / "prompts.json", prompts)

                            result = generate_images_in_session(
                                page=page,
                                prompts=prompts,
                                output_dir=image_dir,
                            )
                            status = (
                                "completed_with_failures"
                                if result["failed_after_retry"]
                                else "completed"
                            )
                            result.update(
                                {
                                    "job_id": job_id,
                                    "topic": cards["topic"],
                                    "status": status,
                                }
                            )
                            _write_json(job_dir / "result.json", result)
                            job_state.update({"status": status})
                            _write_json(job_dir / "job.json", job_state)

                        except Exception:
                            error_text = traceback.format_exc()
                            (job_dir / "error.txt").write_text(
                                error_text,
                                encoding="utf-8",
                            )
                            job_state.update({"status": "failed"})
                            _write_json(job_dir / "job.json", job_state)
                            logger.exception("Background job %s failed", job_id)

                    finally:
                        job_queue.task_done()

            finally:
                context.close()

    except BaseException as exc:
        worker_start_error = exc
        logger.exception("Playwright worker failed to initialize or continue")
        # Unblock FastAPI startup so it can fail immediately rather than hang.
        worker_ready.set()


# ---------------------------------------------------------------------------
# FastAPI lifecycle and the single upload endpoint
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Do not accept HTTP requests until browser startup has completed."""
    global worker_thread

    worker_thread = threading.Thread(
        target=playwright_worker,
        name="playwright-generation-worker",
        daemon=True,
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

@app.post("/upload", status_code=202)
async def upload_json(file: UploadFile = File(...)) -> dict[str, Any]:
    """Validate, persist, and queue a JSON file for background image generation."""
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

    try:
        raw = await file.read(MAX_JSON_BYTES + 1)
        if len(raw) > MAX_JSON_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"JSON file exceeds the {MAX_JSON_BYTES}-byte limit.",
            )

        try:
            data = json.loads(raw.decode("utf-8-sig"))
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail="File must be UTF-8 encoded JSON.",
            ) from exc
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
                ),
            ) from exc

        try:
            cards = validate_cards(data)
        except CardSchemaError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    finally:
        await file.close()

    job_id = str(uuid.uuid4())
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=False)

    # Save the validated source JSON for repeatability/debugging.
    _write_json(job_dir / "input.json", cards)
    _write_json(
        job_dir / "job.json",
        {
            "job_id": job_id,
            "topic": cards["topic"],
            "concepts": len(cards["concepts"]),
            "status": "queued",
        },
    )

    job_queue.put(
        {
            "id": job_id,
            "cards": cards,
            "job_dir": str(job_dir.resolve()),
        }
    )

    # No prompt generation or browser interaction runs in this request handler.
    return {
        "accepted": True,
        "job_id": job_id,
        "topic": cards["topic"],
        "concepts": len(cards["concepts"]),
    }
