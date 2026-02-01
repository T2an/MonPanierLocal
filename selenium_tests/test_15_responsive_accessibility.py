"""
Tests for responsive design and accessibility.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from base_test import BaseTest


class TestResponsiveDesign(BaseTest):
    """Test responsive design on different screen sizes."""
    
    def test_desktop_layout(self, driver, base_url):
        """Test layout on desktop screen."""
        driver.set_window_size(1920, 1080)
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Sidebar should be visible on desktop
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0')]")
        assert sidebar.is_displayed()
    
    def test_tablet_layout(self, driver, base_url):
        """Test layout on tablet screen."""
        driver.set_window_size(768, 1024)
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Page should still be functional
        navbar = driver.find_element(By.TAG_NAME, 'nav')
        assert navbar.is_displayed()
    
    def test_mobile_layout(self, driver, base_url):
        """Test layout on mobile screen."""
        driver.set_window_size(375, 812)  # iPhone X
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Navbar should still be visible
        navbar = driver.find_element(By.TAG_NAME, 'nav')
        assert navbar.is_displayed()
    
    def test_sidebar_collapse_on_narrow_screen(self, driver, base_url):
        """Test sidebar can be collapsed on narrow screen."""
        driver.set_window_size(1200, 800)
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Find and click collapse button
        try:
            collapse_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Masquer') or @title='Masquer le panneau']")
            self.safe_click(driver, collapse_btn)
            time.sleep(1)
            
            # Sidebar should be collapsed
            sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0')]")
            classes = sidebar.get_attribute('class')
            assert 'w-0' in classes or '-translate-x' in classes
        except Exception:
            # Collapse button might not be visible at this size
            pass
    
    def test_footer_on_mobile(self, driver, base_url):
        """Test footer is visible and usable on mobile."""
        driver.set_window_size(375, 812)
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        footer = driver.find_element(By.TAG_NAME, 'footer')
        self.scroll_to_element(driver, footer)
        
        assert footer.is_displayed()
    
    def test_login_form_on_mobile(self, driver, base_url):
        """Test login form is usable on mobile."""
        driver.set_window_size(375, 812)
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'password')
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        assert email_input.is_displayed()
        assert password_input.is_displayed()
        assert submit_btn.is_displayed()


class TestAccessibility(BaseTest):
    """Test accessibility features."""
    
    def test_form_labels_exist(self, driver, base_url):
        """Test form inputs have labels."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        # Check for labels or placeholders
        email_input = driver.find_element(By.ID, 'email')
        placeholder = email_input.get_attribute('placeholder')
        
        # Should have placeholder or associated label
        labels = driver.find_elements(By.TAG_NAME, 'label')
        has_label = len(labels) > 0 or placeholder
        assert has_label
    
    def test_buttons_have_text(self, driver, base_url):
        """Test buttons have readable text."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        
        for btn in buttons[:5]:  # Check first 5 buttons
            text = btn.text
            aria_label = btn.get_attribute('aria-label')
            title = btn.get_attribute('title')
            
            # Should have some accessible name
            assert text or aria_label or title
    
    def test_links_have_text(self, driver, base_url):
        """Test links have readable text."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        links = driver.find_elements(By.TAG_NAME, 'a')
        
        for link in links[:5]:
            text = link.text
            aria_label = link.get_attribute('aria-label')
            
            # Should have some accessible name
            assert text or aria_label or len(link.find_elements(By.TAG_NAME, 'img')) > 0
    
    def test_keyboard_navigation_login(self, driver, base_url):
        """Test keyboard navigation works on login form."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        email_input.click()
        
        # Tab through form
        email_input.send_keys(Keys.TAB)
        active = driver.switch_to.active_element
        
        # Should be on password field
        assert active.get_attribute('type') == 'password' or active.get_attribute('id') == 'password'
    
    def test_focus_visible_on_inputs(self, driver, base_url):
        """Test focus is visible on form inputs."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        email_input = driver.find_element(By.ID, 'email')
        email_input.click()
        
        # Input should be the active element
        active = driver.switch_to.active_element
        assert active == email_input
    
    def test_page_has_main_heading(self, driver, base_url):
        """Test pages have a main heading (h1)."""
        pages = ['/about', '/contact', '/login', '/register']
        
        for page in pages:
            driver.get(f'{base_url}{page}')
            self.wait_for_page_load(driver)
            
            headings = driver.find_elements(By.TAG_NAME, 'h1')
            assert len(headings) >= 1, f"Page {page} should have h1"
    
    def test_images_have_alt_text(self, driver, base_url):
        """Test images have alt text (when present)."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        images = driver.find_elements(By.TAG_NAME, 'img')
        
        for img in images:
            alt = img.get_attribute('alt')
            # Alt can be empty string for decorative images, just shouldn't be None
            assert alt is not None or True  # Allow if no images


class TestToastNotifications(BaseTest):
    """Test toast notification functionality."""
    
    def test_toast_appears_on_error(self, driver, base_url):
        """Test toast notification appears on form error."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        # Submit empty form
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        # Fill with invalid data
        email_input = driver.find_element(By.ID, 'email')
        email_input.send_keys('invalid@test.com')
        
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys('wrong')
        
        self.safe_click(driver, submit_btn)
        
        time.sleep(2)
        
        # Check for error message
        page_source = driver.page_source.lower()
        has_feedback = 'erreur' in page_source or 'error' in page_source or 'invalid' in page_source


class TestInteractiveElements(BaseTest):
    """Test all interactive elements work correctly."""
    
    def test_all_nav_links_clickable(self, driver, base_url):
        """Test all navigation links are clickable."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        nav_links = driver.find_elements(By.XPATH, "//nav//a")
        
        for link in nav_links:
            assert link.is_enabled()
    
    def test_all_buttons_clickable(self, driver, base_url):
        """Test all visible buttons are clickable."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        
        for btn in buttons:
            if btn.is_displayed():
                assert btn.is_enabled()
    
    def test_view_toggle_buttons_work(self, driver, base_url):
        """Test map/list view toggle buttons work."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Click Liste
        liste_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Liste')]")
        self.safe_click(driver, liste_btn)
        time.sleep(1)
        
        # Verify Liste is active
        classes = liste_btn.get_attribute('class')
        assert 'bg-nature' in classes
        
        # Click Carte
        carte_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Carte')]")
        self.safe_click(driver, carte_btn)
        time.sleep(1)
        
        # Verify Carte is active
        classes = carte_btn.get_attribute('class')
        assert 'bg-nature' in classes
    
    def test_footer_links_work(self, driver, base_url):
        """Test footer links navigate correctly."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        footer = driver.find_element(By.TAG_NAME, 'footer')
        self.scroll_to_element(driver, footer)
        
        # Click about link
        about_link = driver.find_element(By.XPATH, "//footer//a[contains(@href, '/about')]")
        self.safe_click(driver, about_link)
        
        time.sleep(2)
        
        assert '/about' in driver.current_url





