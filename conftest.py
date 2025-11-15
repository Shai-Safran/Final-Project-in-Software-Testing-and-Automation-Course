# --- conftest.py (Stable Selenium Manager Version) ---

import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from framework.logger import log_info, log_error

from framework.actions import safe_click, remove_all_overlays

# Timeout for Chrome session stability
COMMAND_TIMEOUT_SECONDS = 300


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store",
        default="True",
        help="True/False האם להריץ כרום במצב Headless"
    )


@pytest.fixture(scope="session")
def driver(request):
    log_info("🚀 מפעיל דפדפן Chrome באמצעות Selenium Manager...")

    # האם להריץ גלוי או headless
    headless_arg = request.config.getoption("--headless").lower()
    is_headless = not (headless_arg == "false" or headless_arg == "no")

    chrome_options = Options()

    # מצב Headless חדש
    if is_headless:
        chrome_options.add_argument("--headless=new")
        log_info("🤖 מצב הדפדפן: Headless")
    else:
        log_info("💻 מצב הדפדפן: גלוי")

    # יציבות גבוהה
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-features=RendererCodeIntegrity")
    chrome_options.add_argument("--remote-allow-origins=*")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        # 🚀 **Selenium Manager עושה הכל — אין צורך בנתיב ל־chromedriver**
        driver = webdriver.Chrome(options=chrome_options)

        log_info("✅ Chrome הופעל בהצלחה (Selenium Manager)")

        driver.set_page_load_timeout(COMMAND_TIMEOUT_SECONDS)
        driver.maximize_window()
        time.sleep(1)

        log_info("🌐 טוען את האתר הראשי: automationexercise.com")
        driver.get("https://automationexercise.com/")

        yield driver

    except Exception as e:
        log_error(f"❌ שגיאה בהפעלת הדפדפן: {e}")
        raise e

    finally:
        log_info("🚪 סוגר דפדפן...")
        try:
            driver.quit()
        except Exception:
            pass
