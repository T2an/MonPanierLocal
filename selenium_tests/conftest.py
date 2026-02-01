"""
Pytest configuration for Selenium tests.
"""
import pytest
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Configuration
# Default to port 3500 (Nginx in production setup)
BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:3500')
API_URL = os.getenv('TEST_API_URL', 'http://localhost:3500')
HEADLESS = os.getenv('TEST_HEADLESS', 'true').lower() == 'true'
SLOW_MODE = os.getenv('TEST_SLOW_MODE', 'false').lower() == 'true'


@pytest.fixture(scope='session')
def base_url():
    """Return base URL for frontend."""
    return BASE_URL


@pytest.fixture(scope='session')
def api_url():
    """Return base URL for API."""
    return API_URL


# Cache geckodriver path at module level
_geckodriver_path = None

def get_geckodriver_path():
    """Get geckodriver path, downloading only once."""
    global _geckodriver_path
    
    if _geckodriver_path is not None:
        return _geckodriver_path
    
    # First try system path
    system_path = shutil.which('geckodriver')
    if system_path:
        _geckodriver_path = system_path
        return _geckodriver_path
    
    # Check if already in webdriver manager cache
    import glob
    home = os.path.expanduser('~')
    cached = glob.glob(f'{home}/.wdm/drivers/geckodriver/**/geckodriver', recursive=True)
    if cached:
        _geckodriver_path = cached[0]
        return _geckodriver_path
    
    # Download with webdriver-manager
    try:
        _geckodriver_path = GeckoDriverManager().install()
    except Exception as e:
        print(f"Warning: Could not download geckodriver: {e}")
        # Try to find any existing geckodriver
        cached = glob.glob(f'{home}/.wdm/**/geckodriver', recursive=True)
        if cached:
            _geckodriver_path = cached[0]
        else:
            raise
    
    return _geckodriver_path


@pytest.fixture(scope='function')
def driver():
    """Create and configure Firefox WebDriver."""
    options = FirefoxOptions()
    
    if HEADLESS:
        options.add_argument('--headless')
    
    options.add_argument('--width=1920')
    options.add_argument('--height=1080')
    
    geckodriver_path = get_geckodriver_path()
    service = FirefoxService(geckodriver_path)
    
    driver = webdriver.Firefox(service=service, options=options)
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

