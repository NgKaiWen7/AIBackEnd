from playwright.sync_api import Playwright, sync_playwright
PROFILE = "./ys_profile"
URL = "https://gemini.rakyatdigital.gov.my/"


def run(playwright: Playwright):
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=PROFILE,
        headless=False,  # Show browser for login
        accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"],
    )

    page = context.pages[0] if context.pages else context.new_page()

    try:
        page.goto(URL, wait_until="domcontentloaded")
        input("Log in and finish setup in the browser, then press Enter...")

        # Your automation continues here

    finally:
        context.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
