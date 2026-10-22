
#!/usr/bin/env python3

import os
import sys
import time
import logging
from pathlib import Path

# Configure storage before importing huggingface_hub.
os.environ["HF_HOME"] = "/mnt/models/huggingface"
os.environ["HF_HUB_CACHE"] = "/mnt/models/huggingface/hub"

from huggingface_hub import snapshot_download
from huggingface_hub.errors import HfHubHTTPError

# Download one repository at a time.
# Existing cached files are reused by huggingface_hub.
MODELS = [
    "BAAI/bge-m3",
    "BAAI/bge-reranker-v2-m3",
    "black-forest-labs/FLUX.1",
    "inclusionAI/LLaDA2.2-mini",
    "inclusionAI/LLaDA-Image",
    "Tongyi-MAI/Z-Image-Turbo",
    "unsloth/Z-Image-GGUF",
    "openai/clip-vit-base-patch32",
    "sentence-transformers/all-MiniLM-L6-v2",
    "urchade/gliner_small-v2.1",
    "RapidAI/RapidOCR",
]

MAX_RETRIES = 5
BASE_DELAY = 15
MAX_DELAY = 300

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger("model-downloader")


def download_model(repo_id: str) -> bool:
    """Download one model, retrying temporary Hub failures."""

    for attempt in range(MAX_RETRIES + 1):
        try:
            log.info("Downloading: %s", repo_id)

            path = snapshot_download(
                repo_id=repo_id,
                repo_type="model",
                max_workers=1,
                etag_timeout=30,
            )

            log.info("Ready: %s -> %s", repo_id, path)
            return True

        except HfHubHTTPError as exc:
            response = getattr(exc, "response", None)
            status = getattr(response, "status_code", None)

            # Authentication, permissions, and invalid repository IDs
            # will not be fixed by retrying.
            if status in (400, 401, 403, 404, 422):
                log.error(
                    "Permanent Hub error for %s (HTTP %s): %s",
                    repo_id, status, exc,
                )
                return False

            if attempt == MAX_RETRIES:
                log.error("Retries exhausted for %s: %s", repo_id, exc)
                return False

            retry_after = None
            if response is not None:
                retry_after = response.headers.get("Retry-After")

            delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)

            if retry_after:
                try:
                    delay = min(float(retry_after), MAX_DELAY)
                except ValueError:
                    pass

            log.warning(
                "Hub error for %s (HTTP %s). Retry %d/%d in %.0f seconds.",
                repo_id, status, attempt + 1, MAX_RETRIES, delay,
            )
            time.sleep(delay)

        except Exception as exc:
            if attempt == MAX_RETRIES:
                log.exception("Failed: %s", repo_id)
                return False

            delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
            log.warning(
                "%s failed: %s. Retry in %d seconds.",
                repo_id, exc, delay,
            )
            time.sleep(delay)

    return False


def main():
    Path("/mnt/models/huggingface/hub").mkdir(
        parents=True, exist_ok=True
    )

    log.info("Hugging Face cache: %s", os.environ["HF_HUB_CACHE"])
    log.info("Models queued: %d", len(MODELS))

    failed = []

    for index, repo_id in enumerate(MODELS, start=1):
        log.info("========== [%d/%d] ==========", index, len(MODELS))

        if not download_model(repo_id):
            failed.append(repo_id)

        # Small pause between repositories to avoid request bursts.
        if index < len(MODELS):
            time.sleep(3)

    print("\n========== SUMMARY ==========")
    print(f"Total: {len(MODELS)}")
    print(f"Successful: {len(MODELS) - len(failed)}")
    print(f"Failed: {len(failed)}")

    for repo_id in failed:
        print(f"  - {repo_id}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
