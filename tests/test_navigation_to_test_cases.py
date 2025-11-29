import logging
import time
from colorama import Fore, Style, init
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from framework.logger import log_info, log_success, log_error, log_warning, log_test_start, log_test_end
import pytest

init(autoreset=True)


def test_navigate_to_test_cases(driver):
    """בדיקה של ניווט לכפתור Test Cases והפעלת כל מקרי הבדיקה"""
    test_name = "בדיקת ניווט לכפתור Test Cases"
    log_test_start(test_name)

    outcome = "passed"
    total_cases = 0
    cases_with_content = 0
    cases_with_instructions = 0

    try:
        url = "https://automationexercise.com/"
        start_time = time.time()
        log_info(f"🌐 Loading {url}")
        driver.get(url)

        # --- ניווט לכפתור Test Cases ---
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

        # --- בדיקה של מקרי הבדיקה ---
        test_cases = driver.find_elements(By.CLASS_NAME, "panel-group")
        log_info(f"נמצאו {len(test_cases)} מקרי בדיקה.")
        if len(test_cases) == 0:
            log_warning("לא נמצאו מקרי בדיקה בעמוד!")

        accordion_headers = driver.find_elements(By.XPATH, "//*[@id='form']//h4/a")
        total_cases = len(accordion_headers)

        for i, header in enumerate(accordion_headers, start=1):
            try:
                header_text = header.text.strip()
                driver.execute_script("arguments[0].scrollIntoView(true);", header)
                time.sleep(0.2)

                header.click()
                log_info(f"נפתח Test Case {i}: {header_text}")

                # המתן לתוכן להופיע
                content = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//*[@id='form']//div[@id='collapse{i}']")
                    )
                )

                if content.is_displayed():
                    cases_with_content += 1
                    log_success(f"✅ התוכן מוצג עבור Test Case {i}")

                    # 🔍 ספירת שורות הוראות
                    content_text = content.text.strip()

                    # ניסיון למצוא שורות ממוספרות (1. 2. 3. וכו')
                    numbered_lines = [line for line in content_text.split('\n') if
                                      line.strip() and any(line.strip().startswith(f"{num}.") for num in range(1, 100))]

                    # אם לא נמצאו שורות ממוספרות, ספור שורות לא ריקות
                    if not numbered_lines:
                        instruction_lines = [line for line in content_text.split('\n') if line.strip()]
                        line_count = len(instruction_lines)
                    else:
                        line_count = len(numbered_lines)

                    if line_count > 0:
                        cases_with_instructions += 1
                        log_success(f"📝 Test Case {i} מכיל {line_count} שורות הוראות")

                        # הצגת 3 השורות הראשונות (preview)
                        preview_lines = content_text.split('\n')[:3]
                        for idx, line in enumerate(preview_lines, 1):
                            if line.strip():
                                log_info(f"   שורה {idx}: {line.strip()[:80]}{'...' if len(line.strip()) > 80 else ''}")
                    else:
                        log_warning(f"⚠️ Test Case {i} לא מכיל הוראות ברורות")

                    # בדיקת התאמה בין כותרת לתוכן
                    if header_text.lower() in content_text.lower():
                        log_success(f"✅ הטקסט בתוכן תואם את הכותרת: '{header_text}'")
                    else:
                        log_warning(f"❌ הטקסט בתוכן לא תואם את הכותרת: '{header_text}'")
                else:
                    log_warning(f"❌ התוכן לא מוצג עבור Test Case {i}")

            except Exception as e:
                log_error(f"❌ שגיאה בבדיקת Test Case {i}: {e}")

    except Exception as e:
        log_error(f"שגיאה במהלך הבדיקה: {e}")
        outcome = "failed"

    finally:
        duration = time.time() - start_time

        # סיכום מפורט
        summary = (
            f"\n{'=' * 60}\n"
            f"📊 סיכום בדיקת Test Cases:\n"
            f"{'=' * 60}\n"
            f"🔢 סה״כ Test Cases: {total_cases}\n"
            f"✅ Cases עם תוכן גלוי: {cases_with_content}\n"
            f"📝 Cases עם הוראות: {cases_with_instructions}\n"
            f"⏱️  משך הבדיקה: {duration:.2f} שניות\n"
            f"{'=' * 60}\n"
        )
        log_info(summary)
        print(Fore.CYAN + summary + Style.RESET_ALL)

        log_test_end(test_name, outcome)


if __name__ == "__main__":
    print("יש להריץ בדיקה זו באמצעות Pytest: pytest tests/test_navigation_to_test_cases.py")
