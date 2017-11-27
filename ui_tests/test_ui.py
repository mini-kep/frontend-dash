from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def test_page_load(driver, local_url):
    driver.get(local_url)
    assert wait_until(driver, 30, By.ID, 'frequency').is_displayed(), 'Frequency not show!'


def test_header_page(driver, local_url):
    driver.get(local_url)
    text = wait_until(driver, 30, By.XPATH, '//h1').text
    assert text == 'Explore mini-kep dataset', 'Wrong header text'


def test_graph_load(driver, local_url):
    driver.get(local_url)
    assert wait_until(driver, 30, By.ID, 'time-series-graph').is_displayed(), 'Graph not show!'


def test_table1_load(driver, local_url):
    driver.get(local_url)
    assert wait_until(driver, 30, By.ID, 'var1-info').is_displayed(), 'First table not show!'


def test_table2_load(driver, local_url):
    driver.get(local_url)
    assert wait_until(driver, 30, By.ID, 'var2-info').is_displayed(), 'Second table not show!'


def wait_until(driver, timeout, by, locator):
    element_visible = EC.visibility_of_element_located((by, locator))
    return WebDriverWait(driver, timeout).until(element_visible)


