"""
Base test class with common utilities.
"""
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BaseTest:
    """Base class for all Selenium tests."""
    
    def wait_for_page_load(self, driver, timeout=10):
        """Wait for page to be fully loaded."""
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    
    def wait_for_element(self, driver, by, value, timeout=10):
        """Wait for element to be visible."""
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
    
    def wait_for_element_clickable(self, driver, by, value, timeout=10):
        """Wait for element to be clickable."""
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def wait_for_url_contains(self, driver, url_part, timeout=10):
        """Wait for URL to contain specific string."""
        return WebDriverWait(driver, timeout).until(
            EC.url_contains(url_part)
        )
    
    def wait_for_text(self, driver, by, value, text, timeout=10):
        """Wait for element to contain specific text."""
        return WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element((by, value), text)
        )
    
    def safe_click(self, driver, element):
        """Click element safely using JavaScript if needed."""
        try:
            element.click()
        except Exception:
            driver.execute_script("arguments[0].click();", element)
    
    def scroll_to_element(self, driver, element):
        """Scroll element into view."""
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        time.sleep(0.3)
    
    def fill_input(self, driver, by, value, text, clear=True):
        """Fill input field with text."""
        element = self.wait_for_element(driver, by, value)
        self.scroll_to_element(driver, element)
        if clear:
            element.clear()
        element.send_keys(text)
        return element
    
    def click_button(self, driver, by, value):
        """Click a button."""
        element = self.wait_for_element_clickable(driver, by, value)
        self.scroll_to_element(driver, element)
        self.safe_click(driver, element)
        return element
    
    def get_element_text(self, driver, by, value, timeout=10):
        """Get text content of element."""
        element = self.wait_for_element(driver, by, value, timeout)
        return element.text
    
    def element_exists(self, driver, by, value, timeout=5):
        """Check if element exists on page."""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False
    
    def count_elements(self, driver, by, value):
        """Count number of matching elements."""
        return len(driver.find_elements(by, value))
    
    def take_screenshot(self, driver, name):
        """Take screenshot with timestamp."""
        import os
        screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        path = os.path.join(screenshots_dir, f'{name}_{timestamp}.png')
        driver.save_screenshot(path)
        return path
    
    def register_user(self, driver, base_url, user_data, is_producer=False):
        """Register a new user via the UI."""
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        
        # Fill form
        self.fill_input(driver, By.ID, 'email', user_data['email'])
        self.fill_input(driver, By.ID, 'username', user_data['username'])
        self.fill_input(driver, By.ID, 'password', user_data['password'])
        self.fill_input(driver, By.ID, 'password_confirm', user_data['password'])
        
        # Check producer checkbox if needed
        if is_producer:
            checkbox = driver.find_element(By.ID, 'is_producer')
            if not checkbox.is_selected():
                self.safe_click(driver, checkbox)
        
        # Submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        self.safe_click(driver, submit_btn)
        
        # Wait for redirect to login
        time.sleep(2)
    
    def login_user(self, driver, base_url, email, password):
        """Login user via the UI."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        # Fill form
        self.fill_input(driver, By.ID, 'email', email)
        self.fill_input(driver, By.ID, 'password', password)
        
        # Submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        self.safe_click(driver, submit_btn)
        
        # Wait for redirect
        time.sleep(2)
    
    def logout_user(self, driver):
        """Logout current user."""
        try:
            logout_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Déconnexion')]")
            self.safe_click(driver, logout_btn)
            time.sleep(1)
        except NoSuchElementException:
            pass  # User not logged in
    
    def api_register_user(self, api_url, user_data):
        """Register user via API."""
        response = requests.post(
            f'{api_url}/api/auth/register/',
            json={
                'email': user_data['email'],
                'username': user_data['username'],
                'password': user_data['password'],
                'password_confirm': user_data['password'],
            }
        )
        return response
    
    def api_login_user(self, api_url, email, password):
        """Login user via API and return tokens."""
        response = requests.post(
            f'{api_url}/api/auth/login/',
            json={'email': email, 'password': password}
        )
        return response.json() if response.status_code == 200 else None
















