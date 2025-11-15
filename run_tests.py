# run_tests.py
import pytest
from datetime import datetime
import os
import sys
import time

# ==============================================================================
#                 הגדרות קונפיגורציה (Configuration Settings)
# ==============================================================================

# 💡 1. קביעת מצב Headless:
#    True: הדפדפן ירוץ ברקע (מומלץ ל-CI).
#    False: הדפדפן יופיע על המסך (מומלץ לניפוי שגיאות).
RUN_HEADLESS_MODE = False  # 💡 שינוי: ברירת מחדל לגלוי

# 💡 2. קביעת מצב הרצה:
#    True: מריץ במקביל באמצעות pytest-xdist (-n auto).
#    False: מריץ בטור (Sequential) (מומלץ לפרויקטים תלויי-סדר).
RUN_PARALLEL_MODE = False  # 💡 ברירת מחדל: טור


# ==============================================================================
#                           Utilities Functions
# ==============================================================================


def generate_report_name():
    """יוצר שם קובץ דוח עם חותמת זמן ומבטיח שתיקיית reports קיימת."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = "reports"
    os.makedirs(report_path, exist_ok=True)
    report_file_name = f"{report_path}/report_{timestamp}.html"
    return report_file_name


def get_run_options():
    """מגדיר דגלי Pytest לפי הקונפיגורציה שנקבעה למעלה."""

    options = [
        '-v',
        'tests/',
        '--self-contained-html',
        '-s',  # מונע קונפליקטים ב-I/O
    ]

    # --- 1. קביעת מצב Headless ---
    if RUN_HEADLESS_MODE:
        options.append("--headless=True")
        print("🤖 הדפדפן ירוץ במצב: נסתר (Headless).")
    else:
        options.append("--headless=False")
        print("💻 הדפדפן ירוץ במצב: גלוי (Non-Headless).")

    # --- 2. קביעת מצב הרצה (Parallel/Sequential) ---
    if RUN_PARALLEL_MODE:
        options.append("--dist=loadfile")
        options.append("-n")
        options.append("auto")
        print("🚀 מריץ מבחנים במצב: מקביל (Parallel).")
    else:
        print("⏩ מריץ מבחנים במצב: טור (Sequential).")

    return options


# ==============================================================================
#                             הרצה ראשית
# ==============================================================================

if __name__ == "__main__":
    # 💡 מדידת זמן התחלה
    start_time = time.time()

    # א. איסוף האופציות הקבועות
    pytest_options = get_run_options()

    # ב. יצירת שם קובץ דינמי
    report_path = generate_report_name()

    # ג. הוספת דגל הדוח לרשימת האופציות
    pytest_options.append(f'--html={report_path}')

    print("-" * 50)
    print(f"✅ הדוח יישמר ב: {report_path}")
    print(f"⚙️ פקודת Pytest: pytest {' '.join(pytest_options)}")
    print("-" * 50)

    # ד. הרצת Pytest
    exit_code = pytest.main(pytest_options)

    # 💡 מדידת זמן סיום וחישוב משך הריצה
    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "=" * 50)
    print(f"⏱️ זמן ריצה כולל (סשן Pytest): {duration:.2f} שניות")
    print("=" * 50)

    # משאיר את קוד היציאה של Pytest (אם לא 0, הייתה כשלון)
    sys.exit(exit_code)