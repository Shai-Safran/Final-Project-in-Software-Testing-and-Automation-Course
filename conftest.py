# --- התחלה של קובץ: conftest.py ---

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # ✅ החזרת webdriver_manager
from framework.logger import log_info, log_error
import pytest
import os
import time
from framework.actions import safe_click, remove_all_overlays

# 🚨 הגדרת Timeout קבוע גבוה
COMMAND_TIMEOUT_SECONDS = 300


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store",
        default="True",
        help="האם להריץ את הדפדפן במצב נסתר (True/False)."
    )


@pytest.fixture(scope="session")
def driver(request):
    log_info("🚀 מפעיל דפדפן Chrome...")

    # קריאת הערך שהועבר לדגל --headless
    headless_arg = request.config.getoption("--headless").lower()

    chrome_options = Options()

    if headless_arg == 'false' or headless_arg == 'no':
        is_headless = False
        log_info("💻 מריץ דפדפן במצב: גלוי (Non-Headless)")
    else:
        is_headless = True
        log_info("🤖 מריץ דפדפן במצב: נסתר (Headless)")

    if is_headless:
        chrome_options.add_argument("--headless=new")

    # 💡 דגלים ליציבות (עבור Chrome Options)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--disable-features=RendererCodeIntegrity")
    chrome_options.add_argument("--disable-site-isolation-trials")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        # ✅ שינוי קריטי: חזרה ל-ChromeDriverManager
        service = Service(
            ChromeDriverManager().install(),
            # 💡 תיקון Timeout: הגדרת command-timeout ב-Service Arguments
            service_args=["--verbose", f"--command-timeout={COMMAND_TIMEOUT_SECONDS}"],
            # 💡 תיקון Timeout: הגדרת timeout ישירות ב-Service (300 שניות)
            timeout=COMMAND_TIMEOUT_SECONDS
        )

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        driver.maximize_window()
        time.sleep(1)
        driver.get("https://automationexercise.com/")

        yield driver

    finally:
        log_info("🚪 סוגר את הדפדפן...")
        if 'driver' in locals() and driver:
            driver.quit()

# --- סוף קובץ: conftest.py ---