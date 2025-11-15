import logging
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

# יצירת תיקיית logs אם לא קיימת
os.makedirs("logs", exist_ok=True)

# יצירת שם קובץ עם תאריך ושעה
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join("logs", f"test_run_{timestamp}.log")

# הגדרת לוגר בסיסי
logging.basicConfig(
    level=logging.INFO,  # שים לב: INFO מופעל
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=log_file_path,
    filemode="a",
    encoding="utf-8"
)

logger = logging.getLogger()

# --- פונקציות לוג צבעוניות ---
def log_debug(message):
    print(f"{Fore.BLUE}🐞 DEBUG: {message}{Style.RESET_ALL}")
    logger.debug(message)

def log_info(message):
    print(f"{Fore.CYAN}ℹ️  INFO: {message}{Style.RESET_ALL}")
    logger.info(message)

def log_success(message):
    print(f"{Fore.GREEN}✅ SUCCESS: {message}{Style.RESET_ALL}")
    logger.info(f"SUCCESS: {message}")

def log_warning(message):
    print(f"{Fore.YELLOW}⚠️  WARNING: {message}{Style.RESET_ALL}")
    logger.warning(message)

def log_error(message):
    print(f"{Fore.RED}❌ ERROR: {message}{Style.RESET_ALL}")
    logger.error(message)

def log_test_start(test_name):
    print(f"{Fore.MAGENTA}🚀 STARTING TEST: {test_name}{Style.RESET_ALL}")
    logger.info(f"STARTING TEST: {test_name}")

def log_test_end(test_name, status):
    status_icon = "✅" if status.lower() == "passed" else "❌"
    color = Fore.GREEN if status.lower() == "passed" else Fore.RED
    print(f"{color}{status_icon} ENDING TEST: {test_name} - {status.upper()}{Style.RESET_ALL}")
    logger.info(f"ENDING TEST: {test_name} - {status.upper()}")
