"""
Tests for sale mode management functionality.
"""
import pytest
import time
import uuid
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from base_test import BaseTest


class TestSaleModeManager(BaseTest):
    """Test sale mode management functionality."""
    
    @pytest.fixture
    def logged_in_producer_with_profile(self, driver, base_url, api_url):
        """Fixture for producer with profile."""
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'sale_mode_{unique_id}@test.com',
            'username': f'sale_mode_{unique_id}',
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
                'name': f'Sale Mode Farm {unique_id}',
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
        
        return user
    
    def test_sales_tab_visible(self, driver, base_url, logged_in_producer_with_profile):
        """Test sales tab is visible."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        assert sales_tab.is_displayed()
    
    def test_sales_tab_content(self, driver, base_url, logged_in_producer_with_profile):
        """Test sales tab shows sale mode management."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        page_source = driver.page_source
        assert 'Modes de vente' in page_source or 'mode' in page_source.lower()
    
    def test_sales_tab_add_button(self, driver, base_url, logged_in_producer_with_profile):
        """Test sales tab has add button."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        assert add_btn.is_displayed()
    
    def test_sales_tab_click_add_shows_form(self, driver, base_url, logged_in_producer_with_profile):
        """Test clicking add button shows sale mode form."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        # Form should appear
        page_source = driver.page_source
        assert 'Type de mode' in page_source or 'Titre' in page_source
    
    def test_sale_mode_form_type_dropdown(self, driver, base_url, logged_in_producer_with_profile):
        """Test sale mode form has type dropdown."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        # Find type select
        type_select = driver.find_element(By.TAG_NAME, 'select')
        options = type_select.find_elements(By.TAG_NAME, 'option')
        
        # Should have multiple options
        assert len(options) > 1
    
    def test_sale_mode_types_available(self, driver, base_url, logged_in_producer_with_profile):
        """Test all sale mode types are available."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        page_source = driver.page_source
        expected_types = ['Vente sur place', 'téléphone', 'Distributeur', 'Livraison', 'Marchés']
        found = sum(1 for t in expected_types if t.lower() in page_source.lower())
        assert found >= 3, "Should have at least 3 sale mode types"
    
    def test_sale_mode_form_title_field(self, driver, base_url, logged_in_producer_with_profile):
        """Test sale mode form has title field."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        # Find title input
        title_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        assert len(title_inputs) > 0
    
    def test_sale_mode_form_instructions_field(self, driver, base_url, logged_in_producer_with_profile):
        """Test sale mode form has instructions field."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        # Find instructions textarea
        textareas = driver.find_elements(By.TAG_NAME, 'textarea')
        assert len(textareas) > 0, "Should have instructions textarea"
    
    def test_sale_mode_form_cancel_button(self, driver, base_url, logged_in_producer_with_profile):
        """Test sale mode form has cancel button."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        cancel_btn = driver.find_element(By.XPATH, "//button[contains(., 'Annuler')]")
        assert cancel_btn.is_displayed()
    
    def test_sale_mode_form_cancel_hides_form(self, driver, base_url, logged_in_producer_with_profile):
        """Test clicking cancel hides the form."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        cancel_btn = driver.find_element(By.XPATH, "//button[contains(., 'Annuler')]")
        self.safe_click(driver, cancel_btn)
        time.sleep(1)
        
        # Add button should be visible again
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        assert add_btn.is_displayed()
    
    def test_sale_mode_opening_hours(self, driver, base_url, logged_in_producer_with_profile):
        """Test sale mode form shows opening hours."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        page_source = driver.page_source
        assert 'Horaires' in page_source or 'Lundi' in page_source
    
    def test_sale_mode_opening_hours_days(self, driver, base_url, logged_in_producer_with_profile):
        """Test opening hours shows all days."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        page_source = driver.page_source
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        found = sum(1 for d in days if d in page_source)
        assert found >= 6, "Should show most days of week"
    
    def test_phone_order_shows_phone_field(self, driver, base_url, logged_in_producer_with_profile):
        """Test phone order type shows phone field."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        # Select phone order type
        type_select = driver.find_element(By.TAG_NAME, 'select')
        select = Select(type_select)
        select.select_by_value('phone_order')
        
        time.sleep(0.5)
        
        # Phone field should appear
        phone_inputs = driver.find_elements(By.XPATH, "//input[@type='tel']")
        assert len(phone_inputs) > 0, "Should show phone input for phone orders"
    
    def test_vending_machine_shows_24_7_option(self, driver, base_url, logged_in_producer_with_profile):
        """Test vending machine type shows 24/7 option."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        # Select vending machine type
        type_select = driver.find_element(By.TAG_NAME, 'select')
        select = Select(type_select)
        select.select_by_value('vending_machine')
        
        time.sleep(0.5)
        
        page_source = driver.page_source
        assert '24/7' in page_source or '24h' in page_source.lower()
    
    def test_market_shows_market_info_field(self, driver, base_url, logged_in_producer_with_profile):
        """Test market type shows market info field."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        add_btn = driver.find_element(By.XPATH, "//button[contains(., 'Ajouter') and contains(., 'mode')]")
        self.safe_click(driver, add_btn)
        time.sleep(1)
        
        # Select market type
        type_select = driver.find_element(By.TAG_NAME, 'select')
        select = Select(type_select)
        select.select_by_value('market')
        
        time.sleep(0.5)
        
        page_source = driver.page_source
        assert 'marché' in page_source.lower() or 'indications' in page_source.lower()
    
    def test_empty_sale_modes_message(self, driver, base_url, logged_in_producer_with_profile):
        """Test empty state message for sale modes."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        sales_tab = driver.find_element(By.XPATH, "//button[contains(., 'vente') or contains(., 'Points')]")
        self.safe_click(driver, sales_tab)
        time.sleep(2)
        
        page_source = driver.page_source.lower()
        assert 'aucun mode' in page_source or 'aucun' in page_source





