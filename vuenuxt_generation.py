import time
from pathlib import Path

from playwright.sync_api import Page, Playwright, sync_playwright

DOWNLOAD_DIR = Path("./new")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL = "qwen3.5:9b"
URL = "https://gemini.rakyatdigital.gov.my/"
PROFILE = "./my_profile"
OUTPUT = Path("./browser_agent_output")
VIEWPORT = {"width": 1280, "height": 720}
OUTPUT.mkdir(exist_ok=True)
DOWNLOAD_BUTTON_SELECTOR = (
    'md-icon-button.download-button[data-aria-label="Download image"]'
)


def submit_prompt(page: Page, prompt: str) -> None:
    editor = page.locator("ucs-prosemirror-editor#agent-search-prosemirror-editor")
    editor.click()

    try:
        editor.fill(prompt)
    except Exception:
        page.keyboard.insert_text(prompt)

    page.keyboard.press("Enter")


def downloads(page, prompt_index: int = 1):
    """Click visible download buttons and save downloads."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    buttons = page.locator(DOWNLOAD_BUTTON_SELECTOR)
    count = buttons.count()

    for button_index in range(count):
        button = buttons.nth(button_index)

        with page.expect_download() as download_info:
            button.evaluate("(el) => el.click()")

        download = download_info.value
        filename = (
            Path(download.suggested_filename).name or f"image_{button_index + 1}.png"
        )

        save_path = DOWNLOAD_DIR / (
            f"prompt_{prompt_index:03d}_download_{button_index + 1:02d}_{filename}"
        )

        download.save_as(save_path)

        if not save_path.is_file() or save_path.stat().st_size == 0:
            raise RuntimeError("Downloaded file is missing or empty.")

        return True

    return False


def run(playwright: Playwright, prompts: list[str]):
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # Use Playwright's bundled Chromium rather than the installed branded Chrome.
    # This avoids the branded-browser download/context crash seen in some versions.
    # A separate profile is intentional because the existing profile was used by Chrome.
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=PROFILE,
        headless=False,
        accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"],
    )

    page = context.pages[0] if context.pages else context.new_page()
    # Keep another tab open so a source page closing alone does not end the session.
    keepalive_page = context.new_page()
    keepalive_page.goto("about:blank")
    page.bring_to_front()

    page.goto(URL, wait_until="domcontentloaded")
    page.get_by_text("NG KAI WEN").first.click()
    input("When the website is ready, press Enter...")
    failed_prompts = []

    for index, prompt in enumerate(prompts, start=1):
        submit_prompt(page, prompt)

        download_status = False
        start_time = time.time()
        timeout = 300  # 5 minutes per prompt

        while not download_status and time.time() - start_time < timeout:
            download_status = downloads(page, index)

        if not download_status:
            page.reload(wait_until="domcontentloaded")
            page.bring_to_front()

        page.keyboard.press("Escape")
        page.get_by_role("link", name="New chat").click()

    # Retry failed prompts once
    for index, prompt in failed_prompts:
        print(f"Retrying prompt {index}...")

        page.keyboard.press("Escape")
        page.get_by_role("link", name="New chat").click()

        submit_prompt(page, prompt)

        download_status = False
        start_time = time.time()
        timeout = 600  # 5 minutes per retry

        while not download_status and time.time() - start_time < timeout:
            download_status = downloads(page, index)

        if not download_status:
            print(f"Prompt {index} failed again.")
            continue

        print(f"Prompt {index} succeeded on retry.")
        page.keyboard.press("Escape")
        page.get_by_role("link", name="New chat").click()


if __name__ == "__main__":
    from ai_image_generation_cards import build_prompts as ai_image_prompts
    from playwright_memory_cards import build_prompts as playwright_prompts
    from vue_practical_card_prompts import PROMPTS

    prompts = []
    # prompts += linux_prompts()[126:]
    # prompts += math_prompts()
    # prompts += PROMPTS
    prompts += playwright_prompts()
    prompts += ai_image_prompts()

    with sync_playwright() as playwright:
        run(playwright, prompts)
