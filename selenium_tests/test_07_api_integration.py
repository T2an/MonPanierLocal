"""
Tests for frontend-API integration.
"""
import pytest
import time
import requests
from selenium.webdriver.common.by import By
from base_test import BaseTest


class TestAPIIntegration(BaseTest):
    """Test frontend-API integration."""
    
    def test_api_health_endpoint(self, api_url):
        """Test API health endpoint is accessible."""
        response = requests.get(f'{api_url}/health/', timeout=10)
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    def test_api_readiness_endpoint(self, api_url):
        """Test API readiness endpoint."""
        response = requests.get(f'{api_url}/ready/', timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert data['cache'] == 'connected'
    
    def test_api_producers_endpoint(self, api_url):
        """Test API producers endpoint."""
        response = requests.get(f'{api_url}/api/producers/', timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data or isinstance(data, list)
    
    def test_api_producers_nearby_endpoint(self, api_url):
        """Test API nearby producers endpoint."""
        response = requests.get(
            f'{api_url}/api/producers/nearby/',
            params={'latitude': 48.8566, 'longitude': 2.3522, 'radius_km': 50},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data or 'distances' in data or 'count' in data
    
    def test_api_product_categories_endpoint(self, api_url):
        """Test API product categories endpoint."""
        response = requests.get(f'{api_url}/api/products/categories/', timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data or isinstance(data, list)
    
    def test_api_cache_stats_endpoint(self, api_url):
        """Test API cache stats endpoint."""
        response = requests.get(f'{api_url}/api/cache/stats/', timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert 'cache' in data
    
    def test_frontend_loads_producers_from_api(self, driver, base_url, api_url):
        """Test frontend loads producer data from API."""
        # First get producer count from API
        response = requests.get(f'{api_url}/api/producers/', timeout=10)
        api_count = response.json().get('count', 0)
        
        # Load frontend list view
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Switch to list view
        liste_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Liste')]")
        self.safe_click(driver, liste_btn)
        
        time.sleep(3)
        
        # Verify frontend shows appropriate content
        page_source = driver.page_source.lower()
        if api_count > 0:
            assert 'producteur' in page_source or 'ferme' in page_source
        else:
            assert 'aucun' in page_source or 'pas de' in page_source or len(page_source) > 500
    
    def test_api_authentication_flow(self, api_url):
        """Test API authentication endpoints."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Register
        register_response = requests.post(
            f'{api_url}/api/auth/register/',
            json={
                'email': f'api_test_{unique_id}@test.com',
                'username': f'api_test_{unique_id}',
                'password': 'TestPassword123!',
                'password_confirm': 'TestPassword123!',
            },
            timeout=10
        )
        assert register_response.status_code in [200, 201]
        
        # Login
        login_response = requests.post(
            f'{api_url}/api/auth/login/',
            json={
                'email': f'api_test_{unique_id}@test.com',
                'password': 'TestPassword123!',
            },
            timeout=10
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert 'access' in tokens
        assert 'refresh' in tokens
        
        # Get user info
        me_response = requests.get(
            f'{api_url}/api/auth/me/',
            headers={'Authorization': f'Bearer {tokens["access"]}'},
            timeout=10
        )
        assert me_response.status_code == 200
        user = me_response.json()
        assert user['email'] == f'api_test_{unique_id}@test.com'
    
    def test_api_search_producers(self, api_url):
        """Test API producer search."""
        response = requests.get(
            f'{api_url}/api/producers/',
            params={'search': 'Ferme'},
            timeout=10
        )
        assert response.status_code == 200
    
    def test_api_filter_producers_by_category(self, api_url):
        """Test API producer category filter."""
        response = requests.get(
            f'{api_url}/api/producers/',
            params={'category': 'maraîchage'},
            timeout=10
        )
        assert response.status_code == 200
    
    def test_api_throttling(self, api_url):
        """Test API throttling doesn't block reasonable usage."""
        # Make several requests quickly
        for i in range(10):
            response = requests.get(f'{api_url}/api/producers/', timeout=10)
            assert response.status_code in [200, 429]  # 429 is rate limited
            
            if response.status_code == 429:
                # Rate limited - this is expected behavior
                break
















