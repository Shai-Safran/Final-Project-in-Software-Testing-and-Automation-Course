import time
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from framework.logger import log_info, log_success, log_error, log_warning
import threading
import sys

init(autoreset=True)


def timer_thread(start_time, stop_event, current_btn_text):
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        mins, secs = divmod(int(elapsed), 60)
        btn_display = current_btn_text[0] if current_btn_text[0] else "ממתין לכפתור..."
        sys.stdout.write(f"\r⏱️ זמן ריצה: {mins:02d}:{secs:02d} | בודק עכשיו: '{btn_display}'")
        sys.stdout.flush()
        time.sleep(1)
    print()  # שורה חדשה בסיום


def test_check_active_buttons_with_live_timer():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"{Fore.RED}❌ שגיאה ביצירת ChromeDriver: {e}{Style.RESET_ALL}")
        return

    driver.maximize_window()
    url = "https://automationexercise.com/"
    start_time = time.time()
    log_info(f"{Fore.CYAN}🌐 Loading {url}{Style.RESET_ALL}")

    # ---------------------------
    # התחלת TIMER חי עם הצגת הכפתור הנוכחי
    # ---------------------------
    stop_event = threading.Event()
    current_btn_text = [""]  # רשימה כדי שניתן יהיה לשנות מתוך thread
    t = threading.Thread(target=timer_thread, args=(start_time, stop_event, current_btn_text))
    t.start()

    try:
        driver.get(url)

        try:
            all_buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a | //button"))
            )
        except TimeoutException:
            log_warning(f"{Fore.YELLOW}⚠️ לא נמצאו כפתורים או קישורים בדף{Style.RESET_ALL}")
            all_buttons = []

        log_info(f"{Fore.CYAN}נמצאו {len(all_buttons)} כפתורים/קישורים בדף.{Style.RESET_ALL}")

        for i in range(len(all_buttons)):
            try:
                all_buttons = driver.find_elements(By.XPATH, "//a | //button")
                btn = all_buttons[i]
                text = btn.text.strip() or btn.get_attribute("value") or "ללא טקסט"

                # עדכון הכפתור הנוכחי ל-TIMER
                current_btn_text[0] = text

                if not btn.is_displayed():
                    log_info(f"{Fore.YELLOW}ℹ️ כפתור {i + 1} '{text}' – לא גלוי, כנראה קישוט או anchor פנימי{Style.RESET_ALL}")
                    continue

                if not btn.is_enabled():
                    log_info(f"{Fore.YELLOW}ℹ️ כפתור {i + 1} '{text}' – לא לחיץ, כנראה קישוט או anchor פנימי{Style.RESET_ALL}")
                    continue

                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.2)
                log_info(f"{Fore.CYAN}בודק כפתור פעיל {i + 1}: '{text}'{Style.RESET_ALL}")

                href = btn.get_attribute("href")
                btn.click()
                log_info(f"{Fore.CYAN}🖱️ בוצעה לחיצה על '{text}'{Style.RESET_ALL}")
                time.sleep(1)

                new_url = driver.current_url
                if href:
                    if href in new_url:
                        log_success(f"{Fore.GREEN}✅ הניווט הצליח: {new_url}{Style.RESET_ALL}")
                    else:
                        log_warning(f"{Fore.YELLOW}❌ הניווט שונה מהצפוי: {new_url}{Style.RESET_ALL}")
                else:
                    log_info(f"{Fore.CYAN}⏳ אין href – בדוק אם התוכן השתנה בדף{Style.RESET_ALL}")

            except StaleElementReferenceException:
                log_warning(f"{Fore.YELLOW}⚠️ StaleElementReferenceException – הכפתור השתנה בזמן הבדיקה{Style.RESET_ALL}")
            except Exception as e:
                log_error(f"{Fore.RED}❌ שגיאה בכפתור {i + 1}: {text} – {e}{Style.RESET_ALL}")
            finally:
                driver.get(url)
                WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//a | //button")))

    except Exception as e:
        log_error(f"{Fore.RED}שגיאה כללית במהלך בדיקה: {e}{Style.RESET_ALL}")

    finally:
        stop_event.set()  # עצירת ה-TIMER
        t.join()
        duration = time.time() - start_time
        log_info(f"{Fore.CYAN}⏱️ משך הבדיקה הכולל: {duration:.2f} שניות{Style.RESET_ALL}")
        driver.quit()
