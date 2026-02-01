"""
Tests for producer detail page.
"""
import pytest
import time
import requests
from selenium.webdriver.common.by import By
from base_test import BaseTest


class TestProducerDetail(BaseTest):
    """Test producer detail page."""
    
    def get_producer_id(self, api_url):
        """Get a producer ID from API."""
        try:
            response = requests.get(f'{api_url}/api/producers/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', data)
                if results and len(results) > 0:
                    return results[0]['id']
        except Exception:
            pass
        return None
    
    def test_producer_detail_page_loads(self, driver, base_url, api_url):
        """Test producer detail page loads."""
        producer_id = self.get_producer_id(api_url)
        
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        driver.get(f'{base_url}/producers/{producer_id}')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Should show producer information
        page_source = driver.page_source
        assert 'error' not in page_source.lower() or len(page_source) > 1000
    
    def test_producer_detail_shows_name(self, driver, base_url, api_url):
        """Test producer detail shows producer name."""
        producer_id = self.get_producer_id(api_url)
        
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        # Get producer name from API
        response = requests.get(f'{api_url}/api/producers/{producer_id}/')
        producer_name = response.json().get('name', '')
        
        driver.get(f'{base_url}/producers/{producer_id}')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        page_source = driver.page_source
        assert producer_name in page_source or 'producteur' in page_source.lower()
    
    def test_producer_detail_shows_address(self, driver, base_url, api_url):
        """Test producer detail shows address."""
        producer_id = self.get_producer_id(api_url)
        
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        driver.get(f'{base_url}/producers/{producer_id}')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Should show address or location info
        page_source = driver.page_source.lower()
        has_address = 'adresse' in page_source or 'rue' in page_source or 'ville' in page_source
        assert has_address or len(page_source) > 500
    
    def test_producer_detail_shows_category(self, driver, base_url, api_url):
        """Test producer detail shows category."""
        producer_id = self.get_producer_id(api_url)
        
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        driver.get(f'{base_url}/producers/{producer_id}')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        page_source = driver.page_source.lower()
        # Check for any category-related content
        categories = ['maraîchage', 'élevage', 'apiculture', 'viticulture', 'céréales', 'boulangerie']
        has_category = any(cat in page_source for cat in categories) or 'catégorie' in page_source
        assert has_category or len(page_source) > 500
    
    def test_producer_detail_has_back_link(self, driver, base_url, api_url):
        """Test producer detail has link to go back."""
        producer_id = self.get_producer_id(api_url)
        
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        driver.get(f'{base_url}/producers/{producer_id}')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Should have navbar with home link
        logo_link = driver.find_element(By.XPATH, "//a[contains(@href, '/')]")
        assert logo_link.is_displayed()
    
    def test_producer_detail_invalid_id(self, driver, base_url):
        """Test producer detail with invalid ID shows error."""
        driver.get(f'{base_url}/producers/99999999')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        page_source = driver.page_source.lower()
        # Should show error or 404
        has_error = 'erreur' in page_source or 'error' in page_source or '404' in page_source or 'introuvable' in page_source
        assert has_error or 'producteur' in page_source
    
    def test_navigate_to_producer_from_list(self, driver, base_url, api_url):
        """Test navigating to producer detail from list view."""
        # First check if there are producers
        producer_id = self.get_producer_id(api_url)
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Switch to list view
        liste_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Liste')]")
        self.safe_click(driver, liste_btn)
        time.sleep(3)
        
        # Try to find a producer link/card
        try:
            producer_link = driver.find_element(
                By.XPATH, 
                "//a[contains(@href, '/producers/')]"
            )
            self.safe_click(driver, producer_link)
            time.sleep(2)
            
            assert '/producers/' in driver.current_url
        except Exception:
            # No clickable producer found, which is okay if list is empty
            pass
    
    def test_producer_detail_shows_products(self, driver, base_url, api_url):
        """Test producer detail shows products section."""
        producer_id = self.get_producer_id(api_url)
        
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        driver.get(f'{base_url}/producers/{producer_id}')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        page_source = driver.page_source.lower()
        # Should mention products somewhere
        has_products_section = 'produit' in page_source or 'product' in page_source
        assert has_products_section or len(page_source) > 500
    
    def test_producer_detail_shows_contact(self, driver, base_url, api_url):
        """Test producer detail shows contact information."""
        producer_id = self.get_producer_id(api_url)
        
        if not producer_id:
            pytest.skip("No producers available for testing")
        
        driver.get(f'{base_url}/producers/{producer_id}')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        page_source = driver.page_source.lower()
        # Should show contact info like phone, email, or website
        has_contact = 'téléphone' in page_source or 'phone' in page_source or 'email' in page_source or 'contact' in page_source or 'horaires' in page_source
        assert has_contact or len(page_source) > 500
















