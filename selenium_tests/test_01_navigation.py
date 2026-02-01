"""
Tests for navigation and public pages.
Tests all links in navbar and footer, page titles, and basic content.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest


class TestNavigation(BaseTest):
    """Test navigation and public pages."""
    
    def test_homepage_loads(self, driver, base_url):
        """Test that homepage loads correctly."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        # Check title
        assert 'Mon Panier Local' in driver.title
        
        # Check navbar is present
        navbar = self.wait_for_element(driver, By.TAG_NAME, 'nav')
        assert navbar.is_displayed()
        
        # Check logo/brand link
        logo = driver.find_element(By.XPATH, "//a[contains(@href, '/')]//span[contains(text(), 'Mon Panier Local')]")
        assert logo.is_displayed()
    
    def test_navbar_links_anonymous(self, driver, base_url):
        """Test navbar links for anonymous users."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        # Check essential navbar links (À propos and Contact are now in footer)
        expected_links = [
            ('Connexion', '/login'),
            ('Inscription', '/register'),
        ]
        
        for text, href_part in expected_links:
            link = driver.find_element(By.XPATH, f"//nav//a[contains(text(), '{text}')]")
            assert link.is_displayed(), f"Link '{text}' should be visible"
            assert href_part in link.get_attribute('href'), f"Link '{text}' should point to {href_part}"
    
    def test_footer_exists(self, driver, base_url):
        """Test footer is present on page."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        footer = driver.find_element(By.TAG_NAME, 'footer')
        assert footer.is_displayed()
    
    def test_footer_has_about_link(self, driver, base_url):
        """Test footer contains About link."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        about_link = driver.find_element(By.XPATH, "//footer//a[contains(text(), 'propos')]")
        assert about_link.is_displayed()
        assert '/about' in about_link.get_attribute('href')
    
    def test_footer_has_contact_button(self, driver, base_url):
        """Test footer contains Contact button."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        contact_link = driver.find_element(By.XPATH, "//footer//a[contains(@href, '/contact')]")
        assert contact_link.is_displayed()
    
    def test_footer_has_register_producer_link(self, driver, base_url):
        """Test footer contains 'Devenir producteur' link."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        producer_link = driver.find_element(By.XPATH, "//footer//a[contains(text(), 'producteur')]")
        assert producer_link.is_displayed()
        assert '/register' in producer_link.get_attribute('href')
    
    def test_footer_has_copyright(self, driver, base_url):
        """Test footer contains copyright notice."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        
        footer = driver.find_element(By.TAG_NAME, 'footer')
        footer_text = footer.text.lower()
        assert 'droits réservés' in footer_text or '©' in footer.text
    
    def test_about_page(self, driver, base_url):
        """Test About page loads and has content."""
        driver.get(f'{base_url}/about')
        self.wait_for_page_load(driver)
        
        # Check page has heading
        heading = self.wait_for_element(driver, By.TAG_NAME, 'h1')
        assert heading.is_displayed()
        
        # Verify we're on the about page
        assert '/about' in driver.current_url
    
    def test_contact_page(self, driver, base_url):
        """Test Contact page loads and has content."""
        driver.get(f'{base_url}/contact')
        self.wait_for_page_load(driver)
        
        # Check page has heading
        heading = self.wait_for_element(driver, By.TAG_NAME, 'h1')
        assert heading.is_displayed()
        
        # Verify we're on the contact page
        assert '/contact' in driver.current_url
    
    def test_login_page_loads(self, driver, base_url):
        """Test Login page loads correctly."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        
        # Check form elements
        email_input = self.wait_for_element(driver, By.ID, 'email')
        password_input = self.wait_for_element(driver, By.ID, 'password')
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        assert email_input.is_displayed()
        assert password_input.is_displayed()
        assert submit_btn.is_displayed()
        
        # Check link to register
        register_link = driver.find_element(By.XPATH, "//a[contains(@href, '/register')]")
        assert register_link.is_displayed()
    
    def test_register_page_loads(self, driver, base_url):
        """Test Register page loads correctly."""
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        
        # Check form elements
        email_input = self.wait_for_element(driver, By.ID, 'email')
        username_input = self.wait_for_element(driver, By.ID, 'username')
        password_input = self.wait_for_element(driver, By.ID, 'password')
        password_confirm = self.wait_for_element(driver, By.ID, 'password_confirm')
        is_producer = driver.find_element(By.ID, 'is_producer')
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        assert email_input.is_displayed()
        assert username_input.is_displayed()
        assert password_input.is_displayed()
        assert password_confirm.is_displayed()
        assert is_producer.is_displayed()
        assert submit_btn.is_displayed()
        
        # Check link to login
        login_link = driver.find_element(By.XPATH, "//a[contains(@href, '/login')]")
        assert login_link.is_displayed()
    
    def test_logo_links_to_home(self, driver, base_url):
        """Test clicking logo returns to homepage."""
        driver.get(f'{base_url}/about')
        self.wait_for_page_load(driver)
        time.sleep(1)
        
        # Click logo link (contains Mon Panier Local text)
        logo = driver.find_element(By.XPATH, "//nav//a[contains(@href, '/') and contains(., 'Mon Panier Local')]")
        logo.click()
        
        time.sleep(2)
        self.wait_for_page_load(driver)
        
        # Should be back on homepage (either / or ends without path)
        current = driver.current_url.rstrip('/')
        expected = base_url.rstrip('/')
        assert current == expected, f"Expected {expected}, got {current}"
    
    def test_404_page(self, driver, base_url):
        """Test 404 page for non-existent routes."""
        driver.get(f'{base_url}/this-page-does-not-exist-12345')
        self.wait_for_page_load(driver)
        
        # Should show some 404 content (depends on implementation)
        page_source = driver.page_source.lower()
        assert '404' in page_source or 'not found' in page_source or 'introuvable' in page_source
    
    def test_homepage_has_sidebar(self, driver, base_url):
        """Test homepage has filter sidebar."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)  # Wait for dynamic content
        
        # Check for sidebar
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0')]")
        assert sidebar.is_displayed()
    
    def test_homepage_has_map_or_list_toggle(self, driver, base_url):
        """Test homepage has map/list view toggle."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Check for view toggle buttons
        carte_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Carte')]")
        liste_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Liste')]")
        
        assert carte_btn.is_displayed()
        assert liste_btn.is_displayed()
    
    def test_navigation_flow_footer_about(self, driver, base_url):
        """Test navigation from footer to about page."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(1)
        
        # Scroll to footer
        footer = driver.find_element(By.TAG_NAME, 'footer')
        self.scroll_to_element(driver, footer)
        
        # Click about link in footer
        about_link = driver.find_element(By.XPATH, "//footer//a[contains(text(), 'propos')]")
        about_link.click()
        
        time.sleep(2)
        self.wait_for_page_load(driver)
        assert '/about' in driver.current_url
    
    def test_navigation_flow_footer_contact(self, driver, base_url):
        """Test navigation from footer to contact page."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(1)
        
        # Scroll to footer
        footer = driver.find_element(By.TAG_NAME, 'footer')
        self.scroll_to_element(driver, footer)
        
        # Click contact link in footer
        contact_link = driver.find_element(By.XPATH, "//footer//a[contains(@href, '/contact')]")
        contact_link.click()
        
        time.sleep(2)
        self.wait_for_page_load(driver)
        assert '/contact' in driver.current_url
    
    def test_navigation_flow_login_to_register(self, driver, base_url):
        """Test navigation from login page to register page."""
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        time.sleep(1)
        
        # Click register link
        register_link = driver.find_element(By.XPATH, "//a[contains(@href, '/register')]")
        register_link.click()
        
        time.sleep(2)
        self.wait_for_page_load(driver)
        assert '/register' in driver.current_url
    
    def test_footer_on_all_pages(self, driver, base_url):
        """Test footer is present on all main pages."""
        pages = ['/', '/about', '/contact', '/login', '/register']
        
        for page in pages:
            driver.get(f'{base_url}{page}')
            self.wait_for_page_load(driver)
            
            footer = driver.find_element(By.TAG_NAME, 'footer')
            assert footer.is_displayed(), f"Footer should be visible on {page}"

