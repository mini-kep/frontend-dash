import pytest
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


@pytest.yield_fixture(scope='session')
def local_url():
    return 'http://127.0.0.1:8000/'


@pytest.yield_fixture(scope='session', name='driver')
def driver_factory(local_url):
    _driver = webdriver.Chrome(ChromeDriverManager().install())
    _driver.get(local_url)
    yield _driver
    _driver.quit()
