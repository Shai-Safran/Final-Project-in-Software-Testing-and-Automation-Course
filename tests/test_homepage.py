# --- התחלה של קובץ: tests/test_homepage.py ---

import time
import threading
import sys
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from framework.actions import safe_click, wait_for_clickable, retry_on_stale
from framework.logger import (
    log_info,
    log_success,
    log_error,
    log_warning,
    log_test_start,
    log_test_end
)

init(autoreset=True)


# ❌ פונקציית הטיימר הוסרה (אין צורך בהרצה איטית)
# def timer_thread(start_time, stop_event, current_btn_text, print_lock):
#     ...


def test_check_active_buttons_with_live_timer(driver):
    test_name = "בדיקת כפתורים פעילים וגלויים בדף הבית"
    log_test_start(test_name)

    url = "https://automationexercise.com/"
    start_time = time.time()
    log_info(f"🌐 טוען את האתר {url}")

    stats = {"success": 0, "warnings": 0, "errors": 0, "total": 0}
    outcome = "passed"

    try:
        driver.get(url)

        try:
            # 💡 נבחר אלמנטים שניתנים ללחיצה (קישורים וכפתורים)
            all_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a | //button"))
            )
        except TimeoutException:
            log_warning("⚠️ לא נמצאו אלמנטים ניתנים ללחיצה בדף")
            all_elements = []

        stats["total"] = len(all_elements)
        log_info(f"נמצאו {len(all_elements)} אלמנטים ניתנים לבדיקה.")

        # אין צורך ב-MAX_BUTTONS_TO_CHECK מאחר שאין ניווט שובר

        # 💡 רשימת מילים לדלג עליהן (אופציונלי, נשאר כדי לסנן קוד HTML מסוים אם יש צורך)
        SKIP_TEXTS = ["javascript", "features"]

        passed_count = 0

        for i, el in enumerate(all_elements, start=1):
            text = el.text.strip() or el.get_attribute("value") or el.get_attribute("href") or "ללא טקסט"

            try:
                # 1. בדיקת גלוי ופעיל
                is_displayed = el.is_displayed()
                is_enabled = el.is_enabled()

                if not is_displayed or not is_enabled:
                    log_warning(f"⚠️ אלמנט {i} '{text}' אינו גלוי או פעיל.")
                    stats["warnings"] += 1
                    continue

                # 2. סינון קריטיות (אם לא ניווט אמיתי, אישור שהוא תקין)
                if any(skip in text.lower() for skip in SKIP_TEXTS):
                    stats["warnings"] += 1
                    continue

                # 3. אימות ההצלחה
                log_success(f"✅ אלמנט {i} '{text}' גלוי ופעיל.")
                passed_count += 1
                stats["success"] += 1

            except StaleElementReferenceException:
                log_warning("⚠️ אלמנט השתנה במהלך הבדיקה (Stale Element).")
                stats["warnings"] += 1
            except Exception as e:
                log_error(f"❌ שגיאה בבדיקת אלמנט {i}: '{text}' – {e}")
                stats["errors"] += 1

    except Exception as e:
        log_error(f"שגיאה כללית במהלך הבדיקה: {e}")
        stats["errors"] += 1
        outcome = "failed"

    finally:
        duration = time.time() - start_time
        summary = (
            f"\n{'=' * 50}\n"
            f"📊 סיכום הבדיקה:\n"
            f"🔹 נבדקו: {stats['total']}\n"
            f"✅ הצלחות: {stats['success']}\n"
            f"⚠️ אזהרות: {stats['warnings']}\n"
            f"❌ שגיאות: {stats['errors']}\n"
            f"⏱️ משך כולל: {duration:.2f} שניות\n"
            f"{'=' * 50}\n"
        )
        log_info(summary)
        print(Fore.MAGENTA + summary + Style.RESET_ALL)

        if stats["errors"] > 0:
            outcome = "failed"

        log_test_end(test_name, outcome)