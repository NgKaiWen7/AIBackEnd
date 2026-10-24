from __future__ import annotations

import json
import os
import queue
import re
import threading
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from memory_card_runner import CardSchemaError, build_prompts, validate_cards
from playwright.sync_api import (
    Error as PlaywrightError,
)
from playwright.sync_api import Page, Playwright, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Configuration can be changed through environment variables.
URL = os.getenv("GEMINI_CARD_URL", "https://gemini.rakyatdigital.gov.my/")
PROFILE_DIR = Path(os.getenv("GEMINI_PROFILE_DIR", "./my_profile"))
DATA_DIR = Path(os.getenv("GEMINI_CARD_DATA_DIR", "./browser_agent_output"))
DOWNLOAD_ROOT = Path(os.getenv("GEMINI_CARD_DOWNLOAD_DIR", "./new"))
DOWNLOAD_BUTTON_SELECTOR = (
    'md-icon-button.download-button[data-aria-label="Download image"]:visible'
)
EDITOR_SELECTOR = "ucs-prosemirror-editor#agent-search-prosemirror-editor"
ACCOUNT_LABEL = os.getenv("GEMINI_ACCOUNT_LABEL", "NG KAI WEN")
FIRST_PROMPT_TIMEOUT = int(os.getenv("GEMINI_PROMPT_TIMEOUT", "300"))
RETRY_PROMPT_TIMEOUT = int(os.getenv("GEMINI_RETRY_TIMEOUT", "600"))
MAX_JSON_BYTES = 20 * 1024 * 1024

for directory in (PROFILE_DIR.parent, DATA_DIR, DOWNLOAD_ROOT):
    directory.mkdir(parents=True, exist_ok=True)

JobQueue = queue.Queue[dict[str, Any] | None]
job_queue: JobQueue = queue.Queue()
stop_event = threading.Event()
state_lock = threading.RLock()
jobs: dict[str, dict[str, Any]] = {}
service_state: dict[str, Any] = {
    "browser_status": "starting",
    "browser_error": None,
    "browser_ready": False,
    "browser_started_at": None,
}
worker_thread: threading.Thread | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str, max_length: int = 48) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip()).strip("._-")
    return (value[:max_length] or "card").lower()


def update_job(job_id: str, **values: Any) -> None:
    with state_lock:
        if job_id in jobs:
            jobs[job_id].update(values)
            jobs[job_id]["updated_at"] = utc_now()


def visible_download_count(page: Page) -> int:
    try:
        return page.locator(DOWNLOAD_BUTTON_SELECTOR).count()
    except PlaywrightError:
        return 0


def submit_prompt(page: Page, prompt: str) -> None:
    editor = page.locator(EDITOR_SELECTOR)
    editor.wait_for(state="visible", timeout=30_000)
    editor.click()
    try:
        editor.fill(prompt, timeout=10_000)
    except PlaywrightError:
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(prompt)
    page.keyboard.press("Enter")


def start_new_chat(page: Page) -> None:
    if page.is_closed():
        raise RuntimeError("The Gemini browser tab was closed")
    try:
        page.keyboard.press("Escape")
    except PlaywrightError:
        pass
    page.get_by_role("link", name="New chat").click(timeout=15_000)
    page.wait_for_timeout(500)


def save_latest_download(
    page: Page, output_dir: Path, index: int, title: str
) -> Path | None:
    buttons = page.locator(DOWNLOAD_BUTTON_SELECTOR)
    count = buttons.count()
    if count < 1:
        return None

    button = buttons.nth(count - 1)
    with page.expect_download(timeout=10_000) as download_info:
        button.evaluate("(el) => el.click()")
    download = download_info.value
    suggested = Path(download.suggested_filename).name
    suffix = Path(suggested).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        suffix = ".png"
    save_path = output_dir / f"prompt_{index:03d}_{slug(title)}{suffix}"
    download.save_as(save_path)
    if not save_path.is_file() or save_path.stat().st_size == 0:
        raise RuntimeError("Downloaded image is missing or empty")
    return save_path


def generate_one(
    page: Page,
    prompt: str,
    index: int,
    title: str,
    output_dir: Path,
    timeout_seconds: int,
) -> tuple[bool, str | None, str | None]:
    """Submit one prompt and wait for a newly rendered image download button."""
    start_new_chat(page)
    page.wait_for_timeout(500)
    baseline_count = visible_download_count(page)
    submit_prompt(page, prompt)

    deadline = time.monotonic() + timeout_seconds
    last_download_error: str | None = None
    while time.monotonic() < deadline:
        if page.is_closed():
            return False, None, "The Gemini tab closed while waiting for generation"

        current_count = visible_download_count(page)
        if current_count > baseline_count:
            try:
                path = save_latest_download(page, output_dir, index, title)
                if path is not None:
                    return True, str(path), None
            except PlaywrightTimeoutError as exc:
                last_download_error = f"Download event timeout: {exc}"
            except (PlaywrightError, OSError, RuntimeError) as exc:
                last_download_error = f"{type(exc).__name__}: {exc}"
        page.wait_for_timeout(1000)

    message = f"No downloadable image appeared within {timeout_seconds} seconds"
    if last_download_error:
        message += f"; last download issue: {last_download_error}"
    return False, None, message


def recover_page(page: Page) -> None:
    try:
        if page.is_closed():
            return
        page.reload(wait_until="domcontentloaded", timeout=60_000)
        page.bring_to_front()
        page.wait_for_timeout(1500)
    except PlaywrightError:
        pass


def process_job(page: Page, task: dict[str, Any]) -> None:
    job_id = task["id"]
    prompts = task["prompts"]
    cards = task["cards"]
    output_dir = Path(task["output_dir"])
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    update_job(
        job_id,
        status="running",
        started_at=utc_now(),
        total=len(prompts),
        current_index=0,
        completed=0,
        failed=0,
        image_files=[],
        errors=[],
    )

    prompt_output = [
        {"index": i, "title": c["title"], "prompt": p}
        for i, (c, p) in enumerate(zip(cards["concepts"], prompts), start=1)
    ]
    (output_dir / "prompts.json").write_text(
        json.dumps(prompt_output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    failures: list[dict[str, Any]] = []
    successful_files: list[str] = []
    errors: list[dict[str, Any]] = []

    for index, (concept, prompt) in enumerate(zip(cards["concepts"], prompts), start=1):
        title = concept["title"]
        update_job(job_id, current_index=index, current_title=title)
        try:
            ok, path, error = generate_one(
                page, prompt, index, title, images_dir, FIRST_PROMPT_TIMEOUT
            )
        except Exception as exc:
            ok, path, error = False, None, f"{type(exc).__name__}: {exc}"

        if ok and path:
            successful_files.append(path)
            update_job(
                job_id,
                completed=len(successful_files),
                image_files=successful_files.copy(),
            )
        else:
            failures.append({"index": index, "title": title, "prompt": prompt})
            errors.append(
                {"index": index, "title": title, "attempt": 1, "error": error}
            )
            recover_page(page)

    # Retry failed concepts once, retaining their original prompt indices and names.
    for failed in failures:
        index = failed["index"]
        title = failed["title"]
        update_job(job_id, current_index=index, current_title=title, retrying=True)
        try:
            ok, path, error = generate_one(
                page, failed["prompt"], index, title, images_dir, RETRY_PROMPT_TIMEOUT
            )
        except Exception as exc:
            ok, path, error = False, None, f"{type(exc).__name__}: {exc}"

        if ok and path:
            successful_files.append(path)
            errors = [e for e in errors if e["index"] != index]
            update_job(
                job_id,
                completed=len(successful_files),
                image_files=successful_files.copy(),
            )
        else:
            errors.append(
                {"index": index, "title": title, "attempt": 2, "error": error}
            )
        recover_page(page)

    failed_indices = {e["index"] for e in errors}
    status = (
        "completed"
        if not failed_indices
        else ("completed_with_errors" if successful_files else "failed")
    )
    update_job(
        job_id,
        status=status,
        failed=len(failed_indices),
        errors=errors,
        image_files=successful_files,
        finished_at=utc_now(),
        output_dir=str(output_dir.resolve()),
        retrying=False,
    )


def browser_worker() -> None:
    """Own all Playwright objects in this thread; API handlers never touch them."""
    try:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR.resolve()),
                headless=False,
                accept_downloads=True,
                viewport={"width": 1280, "height": 720},
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.pages[0] if context.pages else context.new_page()
            # Keep a second tab alive, matching the original workflow.
            keepalive_page = context.new_page()
            keepalive_page.goto("about:blank")
            page.bring_to_front()
            page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
            if ACCOUNT_LABEL:
                try:
                    page.get_by_text(ACCOUNT_LABEL).first.click(timeout=3_000)
                except PlaywrightError:
                    pass

            with state_lock:
                service_state.update(
                    browser_status="awaiting_manual_ready",
                    browser_error=None,
                    browser_started_at=utc_now(),
                )

            while not stop_event.is_set():
                try:
                    task = job_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                if task is None:
                    job_queue.task_done()
                    break
                try:
                    process_job(page, task)
                except Exception as exc:
                    update_job(
                        task["id"],
                        status="failed",
                        finished_at=utc_now(),
                        errors=[{"error": f"{type(exc).__name__}: {exc}"}],
                    )
                finally:
                    job_queue.task_done()
            try:
                context.close()
            except PlaywrightError:
                pass
    except Exception as exc:
        with state_lock:
            service_state.update(
                browser_status="error",
                browser_error=f"{type(exc).__name__}: {exc}",
            )
        # Jobs already accepted should not remain queued indefinitely.
        while True:
            try:
                task = job_queue.get_nowait()
            except queue.Empty:
                break
            if task:
                update_job(
                    task["id"],
                    status="failed",
                    finished_at=utc_now(),
                    errors=[{"error": service_state["browser_error"]}],
                )
            job_queue.task_done()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_thread
    stop_event.clear()
    worker_thread = threading.Thread(
        target=browser_worker, name="playwright-worker", daemon=True
    )
    worker_thread.start()
    yield
    stop_event.set()
    job_queue.put(None)
    if worker_thread:
        worker_thread.join(timeout=15)


app = FastAPI(
    title="Gemini Memory Card Image Service",
    version="1.0.0",
    description="Accept a topic/concepts JSON file and generate one image per concept using a persistent Playwright browser.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, Any]:
    with state_lock:
        return {"ok": service_state["browser_status"] != "error", **service_state}


@app.post("/browser/ready")
def mark_browser_ready() -> dict[str, Any]:
    """Call after manually completing sign-in in the visible browser window."""
    with state_lock:
        status = service_state["browser_status"]
        if status == "error":
            raise HTTPException(status_code=503, detail=service_state["browser_error"])
        if status != "awaiting_manual_ready" and status != "ready":
            raise HTTPException(
                status_code=503,
                detail=f"Browser is not initialized yet (status={status})",
            )
        service_state["browser_ready"] = True
        service_state["browser_status"] = "ready"
    return {
        "browser_ready": True,
        "message": "Browser marked ready. You can submit a JSON card file.",
    }


@app.post("/jobs", status_code=202)
async def create_job(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a JSON file with root keys `topic` and `concepts`."""
    with state_lock:
        if service_state["browser_status"] == "error":
            raise HTTPException(status_code=503, detail=service_state["browser_error"])
        if not service_state["browser_ready"]:
            raise HTTPException(
                status_code=409,
                detail="Open the visible browser, finish sign-in if needed, then POST /browser/ready.",
            )
        if any(j.get("status") in {"queued", "running"} for j in jobs.values()):
            raise HTTPException(
                status_code=409, detail="A generation job is already queued or running."
            )

    raw = await file.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise HTTPException(
            status_code=413, detail=f"JSON file exceeds {MAX_JSON_BYTES} bytes"
        )
    try:
        cards = validate_cards(json.loads(raw.decode("utf-8-sig")))
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400, detail="File must be UTF-8 encoded JSON"
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        ) from exc
    except CardSchemaError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        await file.close()

    prompts = build_prompts(cards)
    job_id = str(uuid.uuid4())
    output_dir = DATA_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "input.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    record = {
        "id": job_id,
        "topic": cards["topic"],
        "status": "queued",
        "total": len(prompts),
        "current_index": 0,
        "current_title": None,
        "completed": 0,
        "failed": 0,
        "created_at": utc_now(),
        "started_at": None,
        "finished_at": None,
        "updated_at": utc_now(),
        "image_files": [],
        "errors": [],
        "output_dir": str(output_dir.resolve()),
    }
    with state_lock:
        # Re-check under the same lock used for job registration so two concurrent
        # uploads cannot both pass the initial busy check and queue overlapping jobs.
        if any(j.get("status") in {"queued", "running"} for j in jobs.values()):
            raise HTTPException(
                status_code=409, detail="A generation job is already queued or running."
            )
        jobs[job_id] = record
        job_queue.put(
            {
                "id": job_id,
                "cards": cards,
                "prompts": prompts,
                "output_dir": str(output_dir),
            }
        )
    return {
        "job_id": job_id,
        "status": "queued",
        "topic": cards["topic"],
        "concepts": len(prompts),
        "status_url": f"/jobs/{job_id}",
        "files_url": f"/jobs/{job_id}/files",
    }


@app.get("/jobs")
def list_jobs() -> list[dict[str, Any]]:
    with state_lock:
        return [
            dict(record)
            for record in sorted(
                jobs.values(), key=lambda x: x["created_at"], reverse=True
            )
        ]


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    with state_lock:
        record = jobs.get(job_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return dict(record)


@app.get("/jobs/{job_id}/files")
def list_job_files(job_id: str) -> dict[str, Any]:
    with state_lock:
        record = jobs.get(job_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Job not found")
        output_dir = Path(record["output_dir"])
    image_dir = output_dir / "images"
    files = []
    if image_dir.exists():
        for path in sorted(image_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in {
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
            }:
                files.append(
                    {
                        "filename": path.name,
                        "size_bytes": path.stat().st_size,
                        "url": f"/jobs/{job_id}/files/{path.name}",
                    }
                )
    return {"job_id": job_id, "files": files}


@app.get("/jobs/{job_id}/files/{filename}")
def download_job_file(job_id: str, filename: str) -> FileResponse:
    with state_lock:
        record = jobs.get(job_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Job not found")
        image_dir = Path(record["output_dir"]) / "images"
    # Restrict path traversal: only serve a direct child filename.
    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = image_dir / filename
    if not path.is_file() or path.suffix.lower() not in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }:
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(path, filename=path.name)
