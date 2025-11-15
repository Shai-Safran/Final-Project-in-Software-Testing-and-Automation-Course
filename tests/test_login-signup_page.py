import pytest
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# ❌ הוסר: from webdriver_manager.chrome import ChromeDriverManager
from framework.actions import (
    safe_click,
    wait_for_clickable,
    retry_on_stale,
    remove_all_overlays,
    logout_if_logged_in
)
from framework.logger import (
    log_info,
    log_success,
    log_error,
    log_warning,
    log_test_start,
    log_test_end
)

# ===================== Fixtures =====================
# 💡 הוסר הפיקסטור driver המקומי - נשתמש בזה מ-conftest.py
# @pytest.fixture
# def driver():
#     ...

@pytest.fixture
def registered_user(driver):
    username, email, password = register_user(driver)
    yield username, email, password
    logout_if_logged_in(driver)

# ===================== User actions =====================
def register_user(driver):
    driver.get("https://automationexercise.com/")
    signup_link = wait_for_clickable(driver, By.LINK_TEXT, "Signup / Login")
    retry_on_stale(safe_click, driver, signup_link)

    name = f"qauser_{random.randint(1000,9999)}"
    email = f"{name}_{random.randint(1000,9999)}@example.test"
    password = f"P@ssw{random.randint(1000,9999)}"

    name_input = wait_for_clickable(driver, By.NAME, "name")
    email_input = wait_for_clickable(driver, By.XPATH, "//input[@data-qa='signup-email']")
    signup_btn = wait_for_clickable(driver, By.XPATH, "//button[@data-qa='signup-button']")

    name_input.send_keys(name)
    email_input.send_keys(email)
    retry_on_stale(safe_click, driver, signup_btn)
    time.sleep(1)

    log_success(f"Registered user: {email}")
    return name, email, password

def login_user(driver, email, password):
    driver.get("https://automationexercise.com/")
    signup_link = wait_for_clickable(driver, By.LINK_TEXT, "Signup / Login")
    retry_on_stale(safe_click, driver, signup_link)
    time.sleep(1)

    login_email = wait_for_clickable(driver, By.XPATH, "//input[@data-qa='login-email']")
    login_password = wait_for_clickable(driver, By.XPATH, "//input[@data-qa='login-password']")
    login_btn = wait_for_clickable(driver, By.XPATH, "//button[@data-qa='login-button']")

    login_email.send_keys(email)
    login_password.send_keys(password)
    retry_on_stale(safe_click, driver, login_btn)
    time.sleep(1)

# ===================== Tests =====================
def test_register_user(driver):
    test_name = "test_register_user"
    log_test_start(test_name)
    try:
        register_user(driver)
        logout_if_logged_in(driver)
        log_test_end(test_name, "passed")
    except Exception as e:
        log_error(f"Error in {test_name}: {e}")
        log_test_end(test_name, "failed")
        raise

def test_login_wrong_user(driver):
    test_name = "test_login_wrong_user"
    log_test_start(test_name)
    try:
        login_user(driver, "wrong@example.test", "invalid123")
        error_elem = wait_for_clickable(driver, By.XPATH, "//p[contains(text(),'Your email or password is incorrect')]", timeout=5)
        if error_elem and error_elem.is_displayed():
            log_success("✅ זוהתה הודעת השגיאה – כניסה נכשלת כפי שצפוי")
            log_test_end(test_name, "passed")
        else:
            log_error("❌ לא זוהתה הודעת השגיאה – כניסה הצליחה עם פרטי שגוי")
            log_test_end(test_name, "failed")
            assert False
    except Exception as e:
        log_error(f"שגיאה כללית ב-{test_name}: {e}")
        log_test_end(test_name, "failed")
        raise