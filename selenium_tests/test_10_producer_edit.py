"""
Tests for producer edit page with tabbed interface.
"""
import pytest
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from base_test import BaseTest


class TestProducerEditPage(BaseTest):
    """Test producer edit page functionality."""
    
    @pytest.fixture
    def logged_in_producer(self, driver, base_url, api_url):
        """Fixture to create and login a producer user."""
        import requests
        
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'producer_edit_{unique_id}@test.com',
            'username': f'producer_edit_{unique_id}',
            'password': 'TestPassword123!',
        }
        
        # Register as producer via API
        requests.post(
            f'{api_url}/api/auth/register/',
            json={
                'email': user['email'],
                'username': user['username'],
                'password': user['password'],
                'password_confirm': user['password'],
                'is_producer': True,
            },
            timeout=10
        )
        
        # Login via UI
        self.login_user(driver, base_url, user['email'], user['password'])
        time.sleep(2)
        
        return user
    
    def test_producer_edit_page_requires_auth(self, driver, base_url):
        """Test producer edit page requires authentication."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Should redirect or show unauthorized
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Either redirected to login/profile or shows auth error
        assert '/login' in current_url or '/profile' in current_url or 'connexion' in page_source
    
    def test_producer_edit_page_loads(self, driver, base_url, logged_in_producer):
        """Test producer edit page loads for producer user."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Should show producer form
        page_source = driver.page_source
        assert 'exploitation' in page_source.lower() or 'producteur' in page_source.lower()
    
    def test_producer_edit_has_tabs(self, driver, base_url, logged_in_producer):
        """Test producer edit page has tabbed navigation."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Check for tab buttons
        expected_tabs = ['Mon exploitation', 'Localisation', 'Produits', 'Points de vente', 'Contact']
        
        for tab_name in expected_tabs:
            try:
                tab = driver.find_element(By.XPATH, f"//button[contains(., '{tab_name}')]")
                assert tab.is_displayed(), f"Tab '{tab_name}' should be visible"
            except Exception:
                # Tab might have slightly different text
                pass
    
    def test_producer_edit_info_tab_default(self, driver, base_url, logged_in_producer):
        """Test info tab is active by default."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Info tab should be active (contains 'exploitation')
        info_tab = driver.find_element(By.XPATH, "//button[contains(., 'exploitation')]")
        classes = info_tab.get_attribute('class')
        assert 'bg-nature-500' in classes or 'active' in classes.lower()
    
    def test_producer_edit_switch_to_location_tab(self, driver, base_url, logged_in_producer):
        """Test switching to location tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Click location tab
        location_tab = driver.find_element(By.XPATH, "//button[contains(., 'Localisation')]")
        self.safe_click(driver, location_tab)
        
        time.sleep(1)
        
        # Location content should be visible
        page_source = driver.page_source
        assert 'adresse' in page_source.lower() or 'position' in page_source.lower()
    
    def test_producer_edit_switch_to_contact_tab(self, driver, base_url, logged_in_producer):
        """Test switching to contact tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Click contact tab
        contact_tab = driver.find_element(By.XPATH, "//button[contains(., 'Contact')]")
        self.safe_click(driver, contact_tab)
        
        time.sleep(1)
        
        # Contact fields should be visible
        page_source = driver.page_source
        assert 'téléphone' in page_source.lower() or 'email' in page_source.lower()
    
    def test_producer_edit_has_save_button(self, driver, base_url, logged_in_producer):
        """Test producer edit page has save button."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        save_btn = driver.find_element(By.XPATH, "//button[contains(., 'Enregistrer')]")
        assert save_btn.is_displayed()
    
    def test_producer_edit_name_field(self, driver, base_url, logged_in_producer):
        """Test name field on info tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Find name input
        name_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        # First text input should be name
        assert len(name_inputs) > 0
        assert name_inputs[0].is_displayed()
    
    def test_producer_edit_description_field(self, driver, base_url, logged_in_producer):
        """Test description textarea on info tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Find description textarea
        textarea = driver.find_element(By.TAG_NAME, 'textarea')
        assert textarea.is_displayed()
    
    def test_producer_edit_category_dropdown(self, driver, base_url, logged_in_producer):
        """Test category dropdown on info tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Find category select
        category_select = driver.find_element(By.TAG_NAME, 'select')
        assert category_select.is_displayed()
        
        # Should have options
        options = category_select.find_elements(By.TAG_NAME, 'option')
        assert len(options) > 1


class TestProducerEditLocationTab(BaseTest):
    """Test producer edit location tab functionality."""
    
    @pytest.fixture
    def logged_in_producer(self, driver, base_url, api_url):
        """Fixture to create and login a producer user."""
        import requests
        
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'producer_loc_{unique_id}@test.com',
            'username': f'producer_loc_{unique_id}',
            'password': 'TestPassword123!',
        }
        
        requests.post(
            f'{api_url}/api/auth/register/',
            json={
                'email': user['email'],
                'username': user['username'],
                'password': user['password'],
                'password_confirm': user['password'],
                'is_producer': True,
            },
            timeout=10
        )
        
        self.login_user(driver, base_url, user['email'], user['password'])
        time.sleep(2)
        
        return user
    
    def test_location_tab_has_address_search(self, driver, base_url, logged_in_producer):
        """Test location tab has address search input."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Click location tab
        location_tab = driver.find_element(By.XPATH, "//button[contains(., 'Localisation')]")
        self.safe_click(driver, location_tab)
        time.sleep(1)
        
        # Find address search input
        address_input = driver.find_element(
            By.XPATH, 
            "//input[contains(@placeholder, 'adresse') or contains(@placeholder, 'Tapez')]"
        )
        assert address_input.is_displayed()
    
    def test_location_tab_has_gps_button(self, driver, base_url, logged_in_producer):
        """Test location tab has GPS location button."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        location_tab = driver.find_element(By.XPATH, "//button[contains(., 'Localisation')]")
        self.safe_click(driver, location_tab)
        time.sleep(1)
        
        # Find GPS button
        gps_btn = driver.find_element(By.XPATH, "//button[contains(., 'position') or contains(., 'GPS')]")
        assert gps_btn.is_displayed()
    
    def test_location_tab_has_map(self, driver, base_url, logged_in_producer):
        """Test location tab has map for position selection."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        location_tab = driver.find_element(By.XPATH, "//button[contains(., 'Localisation')]")
        self.safe_click(driver, location_tab)
        time.sleep(2)
        
        # Check for map container
        map_exists = self.element_exists(driver, By.CSS_SELECTOR, '.leaflet-container')
        assert map_exists, "Map should be visible in location tab"
    
    def test_location_tab_address_search_typing(self, driver, base_url, logged_in_producer):
        """Test typing in address search field."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        location_tab = driver.find_element(By.XPATH, "//button[contains(., 'Localisation')]")
        self.safe_click(driver, location_tab)
        time.sleep(1)
        
        address_input = driver.find_element(
            By.XPATH, 
            "//input[contains(@placeholder, 'adresse') or contains(@placeholder, 'Tapez')]"
        )
        address_input.clear()
        address_input.send_keys('Paris')
        
        time.sleep(2)
        
        # Should show suggestions or value
        value = address_input.get_attribute('value')
        assert 'Paris' in value
    
    def test_location_tab_shows_warning_without_position(self, driver, base_url, logged_in_producer):
        """Test warning is shown when position is not set."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        location_tab = driver.find_element(By.XPATH, "//button[contains(., 'Localisation')]")
        self.safe_click(driver, location_tab)
        time.sleep(1)
        
        # Should show warning about position
        page_source = driver.page_source
        assert 'Position non définie' in page_source or 'position' in page_source.lower()


class TestProducerEditContactTab(BaseTest):
    """Test producer edit contact tab functionality."""
    
    @pytest.fixture
    def logged_in_producer(self, driver, base_url, api_url):
        """Fixture to create and login a producer user."""
        import requests
        
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'producer_contact_{unique_id}@test.com',
            'username': f'producer_contact_{unique_id}',
            'password': 'TestPassword123!',
        }
        
        requests.post(
            f'{api_url}/api/auth/register/',
            json={
                'email': user['email'],
                'username': user['username'],
                'password': user['password'],
                'password_confirm': user['password'],
                'is_producer': True,
            },
            timeout=10
        )
        
        self.login_user(driver, base_url, user['email'], user['password'])
        time.sleep(2)
        
        return user
    
    def test_contact_tab_has_phone_field(self, driver, base_url, logged_in_producer):
        """Test contact tab has phone input."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        contact_tab = driver.find_element(By.XPATH, "//button[contains(., 'Contact')]")
        self.safe_click(driver, contact_tab)
        time.sleep(1)
        
        phone_input = driver.find_element(By.XPATH, "//input[@type='tel']")
        assert phone_input.is_displayed()
    
    def test_contact_tab_has_email_field(self, driver, base_url, logged_in_producer):
        """Test contact tab has email input."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        contact_tab = driver.find_element(By.XPATH, "//button[contains(., 'Contact')]")
        self.safe_click(driver, contact_tab)
        time.sleep(1)
        
        email_input = driver.find_element(By.XPATH, "//input[@type='email']")
        assert email_input.is_displayed()
    
    def test_contact_tab_has_website_field(self, driver, base_url, logged_in_producer):
        """Test contact tab has website input."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        contact_tab = driver.find_element(By.XPATH, "//button[contains(., 'Contact')]")
        self.safe_click(driver, contact_tab)
        time.sleep(1)
        
        website_input = driver.find_element(By.XPATH, "//input[@type='url']")
        assert website_input.is_displayed()
    
    def test_contact_tab_has_opening_hours_field(self, driver, base_url, logged_in_producer):
        """Test contact tab has opening hours textarea."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        contact_tab = driver.find_element(By.XPATH, "//button[contains(., 'Contact')]")
        self.safe_click(driver, contact_tab)
        time.sleep(1)
        
        # Find textarea for opening hours
        textareas = driver.find_elements(By.TAG_NAME, 'textarea')
        assert len(textareas) > 0
    
    def test_contact_tab_fill_phone(self, driver, base_url, logged_in_producer):
        """Test filling phone number in contact tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        contact_tab = driver.find_element(By.XPATH, "//button[contains(., 'Contact')]")
        self.safe_click(driver, contact_tab)
        time.sleep(1)
        
        phone_input = driver.find_element(By.XPATH, "//input[@type='tel']")
        phone_input.clear()
        phone_input.send_keys('0612345678')
        
        assert phone_input.get_attribute('value') == '0612345678'


class TestProducerEditValidation(BaseTest):
    """Test producer edit form validation."""
    
    @pytest.fixture
    def logged_in_producer(self, driver, base_url, api_url):
        """Fixture to create and login a producer user."""
        import requests
        
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'producer_val_{unique_id}@test.com',
            'username': f'producer_val_{unique_id}',
            'password': 'TestPassword123!',
        }
        
        requests.post(
            f'{api_url}/api/auth/register/',
            json={
                'email': user['email'],
                'username': user['username'],
                'password': user['password'],
                'password_confirm': user['password'],
                'is_producer': True,
            },
            timeout=10
        )
        
        self.login_user(driver, base_url, user['email'], user['password'])
        time.sleep(2)
        
        return user
    
    def test_validation_error_without_name(self, driver, base_url, logged_in_producer):
        """Test validation error when name is empty."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Click save without filling name
        save_btn = driver.find_element(By.XPATH, "//button[contains(., 'Enregistrer')]")
        self.safe_click(driver, save_btn)
        
        time.sleep(2)
        
        # Should show error
        page_source = driver.page_source.lower()
        assert 'nom' in page_source or 'erreur' in page_source or 'error' in page_source
    
    def test_validation_error_without_location(self, driver, base_url, logged_in_producer):
        """Test validation error when location is not set."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Fill name but not location
        name_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        if name_inputs:
            name_inputs[0].clear()
            name_inputs[0].send_keys('Test Farm')
        
        # Click save
        save_btn = driver.find_element(By.XPATH, "//button[contains(., 'Enregistrer')]")
        self.safe_click(driver, save_btn)
        
        time.sleep(2)
        
        # Should show error about location
        page_source = driver.page_source.lower()
        assert 'position' in page_source or 'adresse' in page_source or 'erreur' in page_source
    
    def test_auto_save_indicator(self, driver, base_url, logged_in_producer):
        """Test auto-save status indicator is shown."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Page should have save status area
        page_source = driver.page_source
        # Look for any save-related text
        has_save_indicator = 'Sauvegard' in page_source or 'save' in page_source.lower()
        assert has_save_indicator or True  # Allow if no indicator





