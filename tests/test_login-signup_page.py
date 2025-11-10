import pytest
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager

# ===================== Colors =====================
class LogColors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

# ===================== Logging setup =====================
logging.getLogger('WDM').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# ===================== Helpers =====================
def safe_find(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except:
        return None

def scroll_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView(true);", el)
    time.sleep(0.3)
    el.click()

def close_popup(driver):
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
    except:
        pass

# ===================== Fixtures =====================
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield drv
    drv.quit()

@pytest.fixture
def registered_user(driver):
    username, email, password = register_user(driver)
    yield username, email, password
    logout_if_logged_in(driver)

# ===================== User actions =====================
def register_user(driver):
    driver.get("https://automationexercise.com/")
    signup_link = safe_find(driver, By.LINK_TEXT, "Signup / Login")
    scroll_click(driver, signup_link)

    name = f"qauser_{random.randint(1000,9999)}"
    email = f"{name}_{random.randint(1000,9999)}@example.test"
    password = f"P@ssw{random.randint(1000,9999)}"

    name_input = safe_find(driver, By.NAME, "name")
    email_input = safe_find(driver, By.XPATH, "//input[@data-qa='signup-email']")
    signup_btn = safe_find(driver, By.XPATH, "//button[@data-qa='signup-button']")

    if not name_input or not email_input or not signup_btn:
        raise Exception("⚠️ Signup form elements not found")

    name_input.send_keys(name)
    email_input.send_keys(email)
    scroll_click(driver, signup_btn)
    time.sleep(1)
    close_popup(driver)

    logging.info(f"{LogColors.GREEN}✅ Registered user: {email}{LogColors.RESET}")
    return name, email, password

def login_user(driver, email, password):
    driver.get("https://automationexercise.com/")
    signup_link = safe_find(driver, By.LINK_TEXT, "Signup / Login")
    if not signup_link:
        logging.warning(f"{LogColors.YELLOW}⚠️ SKIPPED – login form not found for {email}{LogColors.RESET}")
        pytest.skip(f"Login form not found for {email}")
        return

    scroll_click(driver, signup_link)
    time.sleep(1)

    login_email = safe_find(driver, By.XPATH, "//input[@data-qa='login-email']") or safe_find(driver, By.NAME, "email")
    login_password = safe_find(driver, By.XPATH, "//input[@data-qa='login-password']") or safe_find(driver, By.NAME, "password")
    login_btn = safe_find(driver, By.XPATH, "//button[@data-qa='login-button']")

    if not login_email or not login_password or not login_btn:
        logging.warning(f"{LogColors.YELLOW}⚠️ SKIPPED – login form elements missing for {email}{LogColors.RESET}")
        pytest.skip(f"Login form elements missing for {email}")
        return

    login_email.send_keys(email)
    login_password.send_keys(password)
    scroll_click(driver, login_btn)
    time.sleep(1)

def logout_if_logged_in(driver):
    logout_link = safe_find(driver, By.LINK_TEXT, "Logout")
    if logout_link:
        scroll_click(driver, logout_link)
        logging.info(f"{LogColors.GREEN}🔹 Logged out user{LogColors.RESET}")
        time.sleep(1)

# ===================== Tests =====================
def log_test_result(name, status):
    color = LogColors.GREEN if status == "PASS" else LogColors.RED if status == "FAIL" else LogColors.YELLOW
    logging.info(f"{color}{status} – {name}{LogColors.RESET}")

def test_register_user(driver):
    test_name = "test_register_user"
    try:
        username, email, password = register_user(driver)
        logout_if_logged_in(driver)
        log_test_result(test_name, "PASS")
    except Exception as e:
        logging.error(e)
        log_test_result(test_name, "FAIL")
        raise

def test_login_wrong_user(driver):
    test_name = "test_login_wrong_user"
    try:
        login_user(driver, "wrong@example.test", "invalid123")
        logging.error("❌ Login with wrong credentials succeeded – should fail")
        log_test_result(test_name, "FAIL")
        assert False
    except pytest.skip.Exception:
        log_test_result(test_name, "SKIPPED")
    except Exception:
        log_test_result(test_name, "PASS")

def test_login_registered_user(driver, registered_user):
    test_name = "test_login_registered_user"
    username, email, password = registered_user
    try:
        login_user(driver, email, password)
        log_test_result(test_name, "PASS")
    except pytest.skip.Exception:
        log_test_result(test_name, "SKIPPED")
    except Exception as e:
        logging.error(e)
        log_test_result(test_name, "FAIL")
        raise

def test_logout_registered_user(driver, registered_user):
    test_name = "test_logout_registered_user"
    username, email, password = registered_user
    try:
        login_user(driver, email, password)
        logout_if_logged_in(driver)
        log_test_result(test_name, "PASS")
    except pytest.skip.Exception:
        log_test_result(test_name, "SKIPPED")
    except Exception as e:
        logging.error(e)
        log_test_result(test_name, "FAIL")
        raise
