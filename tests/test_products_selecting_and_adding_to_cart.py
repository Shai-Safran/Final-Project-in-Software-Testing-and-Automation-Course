import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# ייבוא פונקציות ה-Actions וה-Logger
from framework.actions import (
    remove_all_overlays,
    safe_click,
    wait_for_clickable,
    hover_over_element,
    retry_on_stale,
)
from framework.logger import log_info, log_warning, log_error, log_success, log_test_start, log_test_end

PRODUCTS_URL = "https://automationexercise.com/products"
PRODUCT_DETAILS_URL = "https://automationexercise.com/product_details/1"
CART_URL = "https://automationexercise.com/view_cart"


# ===================== Product & Cart Tests =====================

@pytest.mark.order(1)
def test_navigate_to_products(driver):
    test_name = "Navigate to Products"
    log_test_start(test_name)
    try:
        driver.get("https://automationexercise.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        remove_all_overlays(driver)

        products_link = wait_for_clickable(driver, By.XPATH, "//a[contains(text(),'Products')]")
        retry_on_stale(safe_click, driver, products_link)

        log_success("ניווט לעמוד Products הצליח")
        log_test_end(test_name, "passed")
    except Exception as e:
        log_error(f"שגיאה בניווט לעמוד Products: {e}")
        log_test_end(test_name, "failed")
        assert False


@pytest.mark.order(2)
def test_click_women_category(driver):
    test_name = "Click Women Category"
    log_test_start(test_name)
    try:
        driver.get(PRODUCTS_URL)
        remove_all_overlays(driver)

        women_menu = wait_for_clickable(driver, By.XPATH, "//a[@href='#Women']")
        retry_on_stale(safe_click, driver, women_menu)

        log_success("לחיצה על Women בוצעה בהצלחה")
        log_test_end(test_name, "passed")
    except Exception as e:
        log_error(f"שגיאה בלחיצה על Women: {e}")
        log_test_end(test_name, "failed")
        assert False


@pytest.mark.order(3)
def test_view_blue_top_product(driver):
    test_name = "View Product (Blue Top)"
    log_test_start(test_name)
    try:
        driver.get(PRODUCTS_URL)
        remove_all_overlays(driver)

        product_wrapper = wait_for_clickable(driver, By.XPATH,
                                             "//div[@class='product-image-wrapper']//p[text()='Blue Top']")
        retry_on_stale(hover_over_element, driver, product_wrapper)

        product_link = wait_for_clickable(driver, By.XPATH,
                                          "//div[@class='product-image-wrapper']//a[@href='/product_details/1']")
        retry_on_stale(safe_click, driver, product_link)

        log_success("ניווט ל-Product Details הצליח")
        log_test_end(test_name, "passed")
    except Exception as e:
        log_error(f"שגיאה בפתיחת Product Details: {e}")
        log_test_end(test_name, "failed")
        assert False


@pytest.mark.order(4)
def test_add_to_cart_in_details_page(driver):
    test_name = "Add to Cart (Details Page)"
    log_test_start(test_name)
    try:
        driver.get(PRODUCT_DETAILS_URL)
        remove_all_overlays(driver)

        # 💡 תיקון: שימוש ב-XPath לפי תכונה (type='button') בתוך ה-Div הנכון
        add_to_cart_button = wait_for_clickable(driver, By.XPATH,
                                                "//div[@class='product-information']/span/button[@type='button']")
        retry_on_stale(safe_click, driver, add_to_cart_button)

        time.sleep(2)

        log_success("מוצר נוסף בהצלחה לעגלת הקניות מעמוד Details")
        log_test_end(test_name, "passed")
    except Exception as e:
        log_error(f"שגיאה בהוספה לעגלת הקניות מעמוד Details: {e}")
        log_test_end(test_name, "failed")
        assert False


@pytest.mark.order(5)
def test_add_to_cart_via_popup(driver):
    test_name = "Add to Cart via Popup"
    log_test_start(test_name)
    try:
        driver.get(PRODUCTS_URL)
        remove_all_overlays(driver)

        # כפתור זה קיים ברשימת המוצרים (אינדקס 1)
        add_button = wait_for_clickable(driver, By.XPATH, "(//a[text()='Add to cart'])[1]")
        retry_on_stale(safe_click, driver, add_button)

        time.sleep(2)

        # 💡 ודא שהאלמנט מוכן
        popup_view_cart = wait_for_clickable(driver, By.XPATH,
                                             "//div[contains(@class, 'modal-content')]//a[@href='/view_cart']")
        retry_on_stale(safe_click, driver, popup_view_cart)

        # לוודא שהגענו לעגלה
        driver.get(CART_URL)

        # בדיקה שיש מוצר בעגלה
        cart_items = driver.find_elements(By.XPATH, "//tr[@id='product-1']")
        assert cart_items, "לא נוספו מוצרים לעגלה דרך ה-popup"

        log_success(f"מוצר נוסף בהצלחה לעגלה דרך ה-popup ({len(cart_items)} מוצר/ים)")
        log_test_end(test_name, "passed")
    except Exception as e:
        log_error(f"שגיאה בהוספה לעגלה דרך ה-popup: {e}")
        log_test_end(test_name, "failed")
        assert False


@pytest.mark.order(6)
def test_verify_cart_item_and_price(driver):
    test_name = "Verify Cart Item and Price"
    log_test_start(test_name)
    try:
        # 1. דגימת מחיר/שם המוצר מהעמוד הראשי
        driver.get(PRODUCTS_URL)
        remove_all_overlays(driver)

        product_name_element = driver.find_element(By.XPATH, "(//div[@class='productinfo text-center']/p)[1]")
        product_name = product_name_element.text

        product_price_element = driver.find_element(By.XPATH, "(//div[@class='productinfo text-center']/h2)[1]")
        product_price = product_price_element.text

        # 2. ניווט ישיר לעגלה
        driver.get(CART_URL)
        remove_all_overlays(driver)

        # 3. אימות בעמוד העגלה
        cart_product_element = driver.find_element(By.XPATH,
                                                   f"//td[@class='cart_description']/h4/a[text()='{product_name}']")
        assert cart_product_element, f"המוצר '{product_name}' לא נמצא בעגלה"

        cart_price_element = driver.find_element(By.XPATH, f"//td[@class='cart_price']/p[text()='{product_price}']")
        assert cart_price_element, f"המחיר של המוצר '{product_name}' בעגלה שונה מהמחיר בעמוד מוצר"

        log_success(f"המוצר '{product_name}' מופיע בעגלה והמחיר נכון: {product_price}")
        log_test_end(test_name, "passed")
    except Exception as e:
        log_error(f"שגיאה בבדיקת מוצר/מחיר בעגלה: {e}")
        log_test_end(test_name, "failed")
        assert False