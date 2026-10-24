# Gemini Memory Card Image Service

A local FastAPI/Uvicorn service that accepts the reusable memory-card JSON format and generates one image per concept through the visible Gemini browser at `https://gemini.rakyatdigital.gov.my/`.

## JSON format

The root has **only** `topic` and `concepts`. Each concept has **only** `title`, `content`, and `image_prompt`. No `sections`, IDs, or per-card style fields are needed. Shared style and rendering rules live in `memory_card_runner.py`.

```json
{
  "topic": "Leaflet and Vue",
  "concepts": [
    {
      "title": "Create a map",
      "content": "L.map(...) creates a map instance bound to a DOM element.\n\nCode:\nconst map = L.map('map');",
      "image_prompt": "Show a DOM container connected to the Leaflet map instance. Label the element ID and map object."
    }
  ]
}
```

- `content`: the teaching content to preserve on the card, including code/equations where required.
- `image_prompt`: the visual explanation to draw; make it specific and technically accurate.
- Add more entries to `concepts` rather than mixing multiple concepts into one card.

## Install

Run inside the intended Python environment with `uv`:

```bash
uv add fastapi 'uvicorn[standard]' python-multipart playwright
uv run playwright install chromium
```

Or use `requirements.txt` with your preferred environment manager. The persistent browser profile is `./my_profile` by default.

## Start the API

```bash
uv run uvicorn app:app --host 127.0.0.1 --port 8000
```

This opens a **visible Chromium window**. The browser needs a working desktop/display session. On first use, complete any website login in that window. After the page is ready, signal the service:

```bash
curl -X POST http://127.0.0.1:8000/browser/ready
```

The persistent profile saves the browser session for later runs, subject to the site's authentication behavior.

## Submit a JSON file

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -F 'file=@cards.example.json;type=application/json'
```

The response includes `job_id` and `status_url`. Poll it:

```bash
curl http://127.0.0.1:8000/jobs/JOB_ID
```

List completed image files:

```bash
curl http://127.0.0.1:8000/jobs/JOB_ID/files
```

Images are written below `./browser_agent_output/JOB_ID/images/`. The uploaded JSON and built prompts are stored beside them. The service retries failed concepts once and records the errors in job status.

Interactive API documentation is at `http://127.0.0.1:8000/docs`.

## API endpoints

- `GET /health` — browser/service state.
- `POST /browser/ready` — mark the visible browser as signed in and ready.
- `POST /jobs` — multipart upload with form field `file`; returns HTTP 202.
- `GET /jobs` — list jobs known to the current process.
- `GET /jobs/{job_id}` — status, progress, output directory, and errors.
- `GET /jobs/{job_id}/files` — list generated images.
- `GET /jobs/{job_id}/files/{filename}` — download one image.

## Important details

- Keep this bound to `127.0.0.1` unless you add authentication. This example service has no API authentication.
- The Playwright browser is owned by one dedicated worker thread; request handlers do not share Playwright objects across threads.
- Do not run multiple Uvicorn workers: each worker would create a separate browser/profile and an independent in-memory job registry. Use one process (`--workers 1`, the default).
- If the site changes its editor or download-button markup, update the selectors near the top of `app.py`.
- Settings can be overridden with `GEMINI_CARD_URL`, `GEMINI_PROFILE_DIR`, `GEMINI_CARD_DATA_DIR`, `GEMINI_CARD_DOWNLOAD_DIR`, `GEMINI_ACCOUNT_LABEL`, `GEMINI_PROMPT_TIMEOUT`, and `GEMINI_RETRY_TIMEOUT`.
