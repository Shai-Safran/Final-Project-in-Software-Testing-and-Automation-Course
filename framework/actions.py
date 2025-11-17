# --- התחלה של קובץ: C:\Users\Owner\PycharmProjects\automationexercise_web_project\framework\actions.py ---

import time
import random
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, \
    StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from typing import Union
from .logger import log_info, log_warning, log_error, log_success

DEFAULT_TIMEOUT = 10


# ===================== Core Selenium Actions =====================

def safe_click(driver: WebDriver, element: WebElement):
    """מבצע לחיצה בטוחה לאחר גלילה והמתנה ללחיצות."""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(element))
        element.click()
        log_success("לחיצה בוצעה בהצלחה")
    except Exception as e:
        log_error(f"שגיאה ב-safe_click: {e}")
        raise


def wait_for_clickable(driver: WebDriver, by_type: str, locator: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
    """ממתין עד שאלמנט יהיה לחיץ, ומחזיר אותו."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by_type, locator))
        )
        return element
    except Exception as e:
        log_error(f"לא ניתן למצוא אלמנט לחיץ: {locator}")
        raise


def hover_over_element(driver: WebDriver, element: WebElement):
    """מבצע ריחוף עכבר מעל אלמנט."""
    try:
        ActionChains(driver).move_to_element(element).perform()
        log_info("Hover over element executed")
    except Exception as e:
        log_error(f"שגיאה ב-hover_over_element: {e}")
        raise


def remove_all_overlays(driver: WebDriver):
    """מנסה להסיר מודאלים ו-overlays מהדף באמצעות JS (כולל פרסומות ו-iframes)."""
    try:
        # 💡 לוגיקה משופרת להסרת פרסומות ואלמנטים קופצים שאינם מנוקים
        js = """
        let overlays = document.querySelectorAll('div[style*="position: fixed"], .overlay, .modal-backdrop, iframe[src*="google"], .google-auto-placed');
        overlays.forEach(o => o.remove());
        return overlays.length;
        """
        removed = driver.execute_script(js)

        if removed > 0:
            log_info(f"✅ הסרתי {removed} overlays/מודלים באמצעות JS.")
        else:
            log_info("אין overlays להורדה.")

    except Exception as e:
        log_warning(f"אזהרה בהסרת overlays: {e}")


# ===================== Generic Find Helpers =====================

def safe_find(driver: WebDriver, by: str, value: str, timeout: int = DEFAULT_TIMEOUT) -> Union[WebElement, None]:
    """מחפש אלמנט בבטחה ומחזיר None אם לא נמצא."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except:
        return None


def scroll_click(driver: WebDriver, el: WebElement):
    """גולל למיקום האלמנט ולוחץ עליו."""
    driver.execute_script("arguments[0].scrollIntoView(true);", el)
    time.sleep(0.3)
    el.click()


def close_popup(driver: WebDriver):
    """מנסה לסגור חלון קופץ של הדפדפן (alert)."""
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except:
        pass


# ===================== Retry Utility =====================

def retry_on_stale(func, *args, retries=3, delay=0.5, **kwargs):
    """Retry פונקציה במקרה של StaleElementReferenceException"""
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except StaleElementReferenceException:
            log_warning(f"StaleElementReferenceException, ניסיון {attempt + 1}/{retries}")
            time.sleep(delay)
    raise


# ===================== logout if logged in Utility =====================

def logout_if_logged_in(driver):
    """מבצע התנתקות אם המשתמש מחובר."""
    logout_link = safe_find(driver, By.LINK_TEXT, "Logout")
    if logout_link:
        safe_click(driver, logout_link)
        log_info("Logged out user")
        time.sleep(1)

# --- סוף קובץ: C:\Users\Owner\PycharmProjects\automationexercise_web_project\framework\actions.py ---