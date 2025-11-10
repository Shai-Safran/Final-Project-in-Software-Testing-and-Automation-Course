import logging
import time
from colorama import Fore, Style, init
import os

init(autoreset=True)

# יצירת תיקיית לוגים אם לא קיימת
os.makedirs("logs", exist_ok=True)

# הגדרת קובץ לוג עם תאריך ושעה
log_file = f"logs/run_{time.strftime("%Y%m%d-%H-%M-%S")}.log"

# הגדרה בסיסית של logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'  # <--- הוספת פרמטר הקידוד
)

# פונקציות עזר ללוגים צבעוניים
def log_info(msg):
    print(Fore.CYAN + msg)
    logging.info(msg)

def log_success(msg):
    print(Fore.GREEN + "✅ " + msg)
    logging.info(msg)

def log_warning(msg):
    print(Fore.YELLOW + "⚠️ " + msg)
    logging.warning(msg)

def log_error(msg):
    print(Fore.RED + "❌ " + msg)
    logging.error(msg)

def log_title(title):
    line = "=" * 60
    print(Fore.MAGENTA + f"\n{line}\n{title}\n{line}")
    logging.info(f"===== {title} =====")
