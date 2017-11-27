from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


def test_open_page():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("http://127.0.0.1:8000/")
    assert driver.find_element_by_id("frequency").is_displayed()
    driver.quit()
