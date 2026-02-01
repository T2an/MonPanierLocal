"""
Tests for product management functionality.
"""
import pytest
import time
import uuid
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from base_test import BaseTest


class TestProductManager(BaseTest):
    """Test product management functionality."""
    
    def setup_producer_with_login(self, driver, base_url, api_url):
        """Setup a producer with a created profile."""
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'prod_mgr_{unique_id}@test.com',
            'username': f'prod_mgr_{unique_id}',
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
        
        # Login
        login_response = requests.post(
            f'{api_url}/api/auth/login/',
            json={'email': user['email'], 'password': user['password']},
            timeout=10
        )
        tokens = login_response.json()
        
        # Create producer profile
        requests.post(
            f'{api_url}/api/producers/',
            json={
                'name': f'Test Farm {unique_id}',
                'address': '123 Test Street, Paris',
                'latitude': '48.8566',
                'longitude': '2.3522',
                'category': 'maraîchage',
            },
            headers={'Authorization': f'Bearer {tokens["access"]}'},
            timeout=10
        )
        
        # Login via UI
        self.login_user(driver, base_url, user['email'], user['password'])
        time.sleep(2)
        
        return user, tokens
    
    @pytest.fixture
    def logged_in_producer_with_profile(self, driver, base_url, api_url):
        """Fixture for logged in producer with existing profile."""
        return self.setup_producer_with_login(driver, base_url, api_url)
    
    def test_products_tab_visible_after_profile_creation(self, driver, base_url, logged_in_producer_with_profile):
        """Test products tab is visible after profile is created."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        assert products_tab.is_displayed()
        # Should be enabled
        assert 'opacity-50' not in products_tab.get_attribute('class')
    
    def test_products_tab_shows_calendar_and_form(self, driver, base_url, logged_in_producer_with_profile):
        """Test products tab shows calendar and product form."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Click products tab
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        page_source = driver.page_source
        assert 'Calendrier' in page_source or 'calendrier' in page_source.lower()
        assert 'Gérer' in page_source or 'produit' in page_source.lower()
    
    def test_product_form_has_name_field(self, driver, base_url, logged_in_producer_with_profile):
        """Test product form has name field."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        # Find product name input
        name_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Tomates') or contains(@placeholder, 'produit')]")
        assert name_input.is_displayed()
    
    def test_product_form_has_category_dropdown(self, driver, base_url, logged_in_producer_with_profile):
        """Test product form has category dropdown."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        # Find category select
        selects = driver.find_elements(By.TAG_NAME, 'select')
        assert len(selects) > 0, "Should have category dropdown"
    
    def test_product_form_has_availability_options(self, driver, base_url, logged_in_producer_with_profile):
        """Test product form has availability period options."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        page_source = driver.page_source
        assert "Période de disponibilité" in page_source or "disponibilité" in page_source.lower()
        assert "Tout l'année" in page_source or "all_year" in page_source.lower()
    
    def test_product_form_custom_availability_shows_months(self, driver, base_url, logged_in_producer_with_profile):
        """Test custom availability option shows month selectors."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        # Find availability type select and change to custom
        availability_selects = driver.find_elements(By.TAG_NAME, 'select')
        for select_elem in availability_selects:
            options = select_elem.find_elements(By.TAG_NAME, 'option')
            for opt in options:
                if 'custom' in opt.get_attribute('value').lower() or 'personnalisée' in opt.text.lower():
                    select = Select(select_elem)
                    select.select_by_value(opt.get_attribute('value'))
                    break
        
        time.sleep(1)
        
        # Should show month selectors
        page_source = driver.page_source
        assert 'Janvier' in page_source or 'début' in page_source.lower() or 'mois' in page_source.lower()
    
    def test_product_form_add_button(self, driver, base_url, logged_in_producer_with_profile):
        """Test product form has add button."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'produit')]")
        assert add_btn.is_displayed()
    
    def test_add_product(self, driver, base_url, logged_in_producer_with_profile):
        """Test adding a new product."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        # Fill product name
        name_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Tomates') or contains(@placeholder, 'produit')]")
        name_input.clear()
        name_input.send_keys('Tomates Bio')
        
        # Click add button
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'produit')]")
        self.safe_click(driver, add_btn)
        
        time.sleep(3)
        
        # Product should appear in list
        page_source = driver.page_source
        assert 'Tomates Bio' in page_source


class TestProductCalendar(BaseTest):
    """Test product calendar functionality."""
    
    @pytest.fixture
    def logged_in_producer_with_products(self, driver, base_url, api_url):
        """Fixture for producer with products."""
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'prod_cal_{unique_id}@test.com',
            'username': f'prod_cal_{unique_id}',
            'password': 'TestPassword123!',
        }
        
        # Register
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
        
        # Login and create producer
        login_response = requests.post(
            f'{api_url}/api/auth/login/',
            json={'email': user['email'], 'password': user['password']},
            timeout=10
        )
        tokens = login_response.json()
        
        # Create producer
        producer_response = requests.post(
            f'{api_url}/api/producers/',
            json={
                'name': f'Calendar Farm {unique_id}',
                'address': '123 Test Street',
                'latitude': '48.8566',
                'longitude': '2.3522',
                'category': 'maraîchage',
            },
            headers={'Authorization': f'Bearer {tokens["access"]}'},
            timeout=10
        )
        producer = producer_response.json()
        
        # Add products
        for product_name in ['Tomates', 'Carottes', 'Pommes']:
            requests.post(
                f'{api_url}/api/products/',
                json={
                    'name': product_name,
                    'producer': producer['id'],
                    'availability_type': 'custom',
                    'availability_start_month': 4,
                    'availability_end_month': 10,
                },
                headers={'Authorization': f'Bearer {tokens["access"]}'},
                timeout=10
            )
        
        # Login via UI
        self.login_user(driver, base_url, user['email'], user['password'])
        time.sleep(2)
        
        return user
    
    def test_calendar_visible_on_products_tab(self, driver, base_url, logged_in_producer_with_products):
        """Test calendar is visible on products tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        # Calendar should be visible
        page_source = driver.page_source
        assert 'Calendrier de disponibilité' in page_source or 'disponibilité' in page_source.lower()
    
    def test_calendar_shows_12_months(self, driver, base_url, logged_in_producer_with_products):
        """Test calendar shows all 12 months."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        page_source = driver.page_source
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        found_months = sum(1 for m in months if m in page_source)
        assert found_months >= 10, "Should show most months"
    
    def test_calendar_shows_product_names(self, driver, base_url, logged_in_producer_with_products):
        """Test calendar shows product names."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        page_source = driver.page_source
        # Should show products from fixture
        assert 'Tomates' in page_source or 'Carottes' in page_source
    
    def test_calendar_empty_message(self, driver, base_url, api_url):
        """Test calendar shows empty message when no products."""
        # Create producer without products
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'prod_empty_{unique_id}@test.com',
            'username': f'prod_empty_{unique_id}',
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
        
        login_response = requests.post(
            f'{api_url}/api/auth/login/',
            json={'email': user['email'], 'password': user['password']},
            timeout=10
        )
        tokens = login_response.json()
        
        requests.post(
            f'{api_url}/api/producers/',
            json={
                'name': f'Empty Farm {unique_id}',
                'address': '123 Test Street',
                'latitude': '48.8566',
                'longitude': '2.3522',
                'category': 'maraîchage',
            },
            headers={'Authorization': f'Bearer {tokens["access"]}'},
            timeout=10
        )
        
        self.login_user(driver, base_url, user['email'], user['password'])
        time.sleep(2)
        
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        products_tab = driver.find_element(By.XPATH, "//button[contains(., 'Produits')]")
        self.safe_click(driver, products_tab)
        time.sleep(2)
        
        page_source = driver.page_source.lower()
        assert 'aucun produit' in page_source or 'aucun' in page_source





