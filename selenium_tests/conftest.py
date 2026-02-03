"""
Pytest configuration for Selenium tests.
Utilise Chrome par defaut, Firefox en secours.
"""
import pytest
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:3500')
API_URL = os.getenv('TEST_API_URL', 'http://localhost:3500')
HEADLESS = os.getenv('TEST_HEADLESS', 'true').lower() == 'true'
SLOW_MODE = os.getenv('TEST_SLOW_MODE', 'false').lower() == 'true'
BROWSER = os.getenv('TEST_BROWSER', 'chrome').lower()


@pytest.fixture(scope='session')
def base_url():
    """Return base URL for frontend."""
    return BASE_URL


@pytest.fixture(scope='session')
def api_url():
    """Return base URL for API."""
    return API_URL


def _create_chrome_driver():
    """Cree un WebDriver Chrome."""
    try:
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        raise RuntimeError("Installez webdriver-manager pour Chrome: pip install webdriver-manager")
    options = ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _create_firefox_driver():
    """Cree un WebDriver Firefox."""
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from webdriver_manager.firefox import GeckoDriverManager
    options = FirefoxOptions()
    if HEADLESS:
        options.add_argument('--headless')
    options.add_argument('--width=1920')
    options.add_argument('--height=1080')
    service = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=options)


@pytest.fixture(scope='function')
def driver():
    """Create and configure WebDriver (Chrome or Firefox)."""
    try:
        if BROWSER == 'firefox':
            driver = _create_firefox_driver()
        else:
            driver = _create_chrome_driver()
    except Exception as e:
        if BROWSER == 'chrome':
            try:
                driver = _create_firefox_driver()
            except Exception as e2:
                raise RuntimeError(f"Impossible de creer le driver: {e}; {e2}") from e2
        else:
            raise
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture(scope='function')
def wait(driver):
    """Create WebDriverWait instance."""
    return WebDriverWait(driver, 15)


@pytest.fixture(scope='session')
def test_user():
    """Test user credentials."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        'email': f'selenium_test_{unique_id}@test.com',
        'username': f'selenium_test_{unique_id}',
        'password': 'TestPassword123!',
    }


@pytest.fixture(scope='session')
def test_producer_user():
    """Test producer user credentials."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        'email': f'selenium_producer_{unique_id}@test.com',
        'username': f'selenium_producer_{unique_id}',
        'password': 'TestPassword123!',
        'is_producer': True,
    }


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests that require authentication"
    )
    config.addinivalue_line(
        "markers", "producer: marks tests specific to producers"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Take screenshot on test failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == 'call' and rep.failed:
        driver = item.funcargs.get('driver')
        if driver:
            # Create screenshots directory
            screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Take screenshot
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(
                screenshots_dir, 
                f'{item.name}_{timestamp}.png'
            )
            driver.save_screenshot(screenshot_path)
            print(f"\nScreenshot saved: {screenshot_path}")

