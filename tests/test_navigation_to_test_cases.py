import logging
import time
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from framework.logger import log_info, log_success, log_error, log_warning

init(autoreset=True)


def test_navigate_to_test_cases():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    url = "https://automationexercise.com/"
    start_time = time.time()
    log_info(f"🌐 Loading {url}")

    driver.get(url)

    try:
        # ניווט לכפתור Test Cases
        button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//a[@href='/test_cases']"))
        )
        log_success("כפתור 'Test Cases' נמצא וגלוי לעין")

        if not button.is_enabled():
            log_warning("הכפתור מופיע אך אינו פעיל כרגע.")
        else:
            button.click()
            log_info("🖱️ בוצעה לחיצה על 'Test Cases'")

        WebDriverWait(driver, 10).until(EC.url_contains("/test_cases"))
        log_success("הניווט לעמוד Test Cases הצליח")

        # בדיקה של מקרי הבדיקה
        test_cases = driver.find_elements(By.CLASS_NAME, "panel-group")
        log_info(f"נמצאו {len(test_cases)} מקרי בדיקה.")

        if len(test_cases) == 0:
            log_warning("לא נמצאו מקרי בדיקה בעמוד!")

        # -------------------------------------------------------
        # ✅ בדיקה שכל Test Case לחיץ ומוביל לפתיחת התוכן עם כותרת תואמת
        # -------------------------------------------------------
        accordion_headers = driver.find_elements(By.XPATH, "//*[@id='form']//h4/a")

        for i, header in enumerate(accordion_headers, start=1):
            try:
                # שמירת הטקסט של הכותרת
                header_text = header.text.strip()

                # גלילה כדי להבטיח שהאלמנט נראה
                driver.execute_script("arguments[0].scrollIntoView(true);", header)
                time.sleep(0.2)

                header.click()
                log_info(f"נפתח Test Case {i}: {header_text}")

                # מחכים שהתוכן של ה-accordion יופיע
                content = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//*[@id='form']//div[@id='collapse{i}']")
                    )
                )

                if content.is_displayed():
                    log_success(f"✅ התוכן מוצג עבור Test Case {i}")

                    # בדיקה אם הטקסט שבתוכן מכיל את שם ה-Test Case
                    if header_text.lower() in content.text.lower():
                        log_success(f"✅ הטקסט בתוכן תואם את הכותרת: '{header_text}'")
                    else:
                        log_warning(f"❌ הטקסט בתוכן לא תואם את הכותרת: '{header_text}'")

                else:
                    log_warning(f"❌ התוכן לא מוצג עבור Test Case {i}")

            except Exception as e:
                log_error(f"❌ שגיאה בבדיקת Test Case {i}: {e}")

    except Exception as e:
        log_error(f"שגיאה במהלך הבדיקה: {e}")

    finally:
        duration = time.time() - start_time
        log_info(f"⏱️ משך הבדיקה: {duration:.2f} שניות")
        driver.quit()
