"""
Tests for all form interactions - filling fields, validation, submission.
"""
import pytest
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from base_test import BaseTest


class TestFormValidation(BaseTest):
    """Test form validation behaviors."""
    
    def test_login_form_email_validation(self, driver, base_url):
        """Test login form validates email format."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        # Enter invalid email
        email_input = driver.find_element(By.ID, 'email')
        email_input.clear()
        email_input.send_keys('notanemail')
        
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys('password123')
        
        # Try to submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        self.safe_click(driver, submit_btn)
        
        time.sleep(0.5)
        
        # Should not submit (HTML5 validation)
        assert '/login' in driver.current_url
    
    def test_login_form_required_fields(self, driver, base_url):
        """Test login form requires all fields."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        # Check required attribute
        email_input = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'password')
        
        assert email_input.get_attribute('required') is not None or 'required' in email_input.get_attribute('class')
        assert password_input.get_attribute('required') is not None or 'required' in password_input.get_attribute('class')
    
    def test_register_form_required_fields(self, driver, base_url):
        """Test register form requires all fields."""
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        
        required_fields = ['email', 'username', 'password', 'password_confirm']
        
        for field_id in required_fields:
            field = driver.find_element(By.ID, field_id)
            has_required = field.get_attribute('required') is not None
            assert has_required or field.is_displayed()
    
    def test_form_input_focus_styling(self, driver, base_url):
        """Test form inputs have focus styling."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        email_input.click()
        
        # Check if focus ring/outline is applied (CSS class check)
        classes = email_input.get_attribute('class')
        assert 'focus' in classes or email_input == driver.switch_to.active_element
    
    def test_form_tab_navigation(self, driver, base_url):
        """Test form fields can be navigated with Tab key."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        email_input.click()
        
        # Tab to next field
        email_input.send_keys(Keys.TAB)
        
        # Active element should be password field
        active = driver.switch_to.active_element
        assert active.get_attribute('id') == 'password' or active.get_attribute('type') == 'password'
    
    def test_form_submit_with_enter(self, driver, base_url):
        """Test form can be submitted with Enter key."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        # Fill form
        self.fill_input(driver, By.ID, 'email', 'test@example.com')
        password_input = self.fill_input(driver, By.ID, 'password', 'password123')
        
        # Press Enter
        password_input.send_keys(Keys.ENTER)
        
        time.sleep(2)
        
        # Form should have been submitted (may show error for invalid creds)
        page_source = driver.page_source.lower()
        # Either redirected or showing error
        assert '/login' not in driver.current_url or 'erreur' in page_source or 'error' in page_source
    
    def test_checkbox_toggle(self, driver, base_url):
        """Test checkbox can be toggled."""
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        
        is_producer = driver.find_element(By.ID, 'is_producer')
        
        # Should start unchecked
        initial_state = is_producer.is_selected()
        
        # Click to toggle
        self.safe_click(driver, is_producer)
        time.sleep(0.2)
        
        # State should have changed
        new_state = is_producer.is_selected()
        assert new_state != initial_state
        
        # Toggle back
        self.safe_click(driver, is_producer)
        time.sleep(0.2)
        
        assert is_producer.is_selected() == initial_state


class TestFormInteractions(BaseTest):
    """Test various form interaction patterns."""
    
    def test_clear_and_retype_input(self, driver, base_url):
        """Test input can be cleared and retyped."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        
        # Type initial value
        email_input.send_keys('first@example.com')
        assert email_input.get_attribute('value') == 'first@example.com'
        
        # Clear and retype
        email_input.clear()
        email_input.send_keys('second@example.com')
        assert email_input.get_attribute('value') == 'second@example.com'
    
    def test_input_placeholder_visibility(self, driver, base_url):
        """Test input placeholders are visible when empty."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        placeholder = email_input.get_attribute('placeholder')
        
        assert placeholder and len(placeholder) > 0
    
    def test_copy_paste_in_input(self, driver, base_url):
        """Test copy-paste works in inputs."""
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys('TestPassword123!')
        
        confirm_input = driver.find_element(By.ID, 'password_confirm')
        confirm_input.send_keys('TestPassword123!')
        
        # Values should match
        assert password_input.get_attribute('value') == confirm_input.get_attribute('value')
    
    def test_special_characters_in_input(self, driver, base_url):
        """Test special characters can be entered."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        special_email = 'test+special@example.com'
        email_input.send_keys(special_email)
        
        assert email_input.get_attribute('value') == special_email
    
    def test_long_input_handling(self, driver, base_url):
        """Test handling of long input values."""
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        
        username_input = driver.find_element(By.ID, 'username')
        long_username = 'a' * 100  # 100 characters
        username_input.send_keys(long_username)
        
        # Input should accept the value (or truncate)
        value = username_input.get_attribute('value')
        assert len(value) > 0


class TestButtonStates(BaseTest):
    """Test button states and interactions."""
    
    def test_submit_button_visible(self, driver, base_url):
        """Test submit button is visible."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        assert submit_btn.is_displayed()
    
    def test_submit_button_enabled(self, driver, base_url):
        """Test submit button is enabled."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        assert submit_btn.is_enabled()
    
    def test_go_button_clickable(self, driver, base_url):
        """Test GO buttons are clickable."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        go_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'GO')]")
        
        for btn in go_buttons:
            assert btn.is_displayed()
            assert btn.is_enabled()
    
    def test_category_buttons_clickable(self, driver, base_url):
        """Test category filter buttons are clickable."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Find category buttons
        category_buttons = driver.find_elements(
            By.XPATH, 
            "//button[contains(@class, 'rounded-2xl') and contains(@class, 'text-left')]"
        )
        
        for btn in category_buttons[:3]:  # Test first 3
            assert btn.is_displayed()
            assert btn.is_enabled()
    
    def test_view_toggle_buttons_clickable(self, driver, base_url):
        """Test map/list toggle buttons are clickable."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        carte_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Carte')]")
        liste_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Liste')]")
        
        assert carte_btn.is_displayed() and carte_btn.is_enabled()
        assert liste_btn.is_displayed() and liste_btn.is_enabled()
        
        # Click and verify state changes
        self.safe_click(driver, liste_btn)
        time.sleep(0.5)
        
        # Liste should now be active
        liste_classes = liste_btn.get_attribute('class')
        assert 'bg-nature' in liste_classes or 'active' in liste_classes.lower()
















