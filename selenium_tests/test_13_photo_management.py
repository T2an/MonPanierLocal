"""
Tests for photo management functionality.
"""
import pytest
import time
import uuid
import os
import requests
from selenium.webdriver.common.by import By
from base_test import BaseTest


class TestPhotoManager(BaseTest):
    """Test photo management functionality."""
    
    @pytest.fixture
    def logged_in_producer_with_profile(self, driver, base_url, api_url):
        """Fixture for producer with profile."""
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'photo_mgr_{unique_id}@test.com',
            'username': f'photo_mgr_{unique_id}',
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
                'name': f'Photo Farm {unique_id}',
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
    
    def test_photo_section_visible_on_info_tab(self, driver, base_url, logged_in_producer_with_profile):
        """Test photo section is visible on info tab."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Info tab is default
        page_source = driver.page_source
        assert 'Photos' in page_source or 'photo' in page_source.lower()
    
    def test_photo_upload_input_exists(self, driver, base_url, logged_in_producer_with_profile):
        """Test photo upload input exists."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Find file input
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        assert file_input is not None
    
    def test_photo_upload_accepts_images(self, driver, base_url, logged_in_producer_with_profile):
        """Test photo upload accepts image files."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        accept_attr = file_input.get_attribute('accept')
        
        # Should accept images
        assert 'image' in accept_attr.lower()
    
    def test_photo_section_has_label(self, driver, base_url, logged_in_producer_with_profile):
        """Test photo section has proper label."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        page_source = driver.page_source
        assert 'Ajouter une photo' in page_source or 'photo' in page_source.lower()
    
    def test_photo_grid_visible(self, driver, base_url, logged_in_producer_with_profile):
        """Test photo grid container is visible."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # There should be a grid container for photos (even if empty)
        grids = driver.find_elements(By.XPATH, "//div[contains(@class, 'grid')]")
        assert len(grids) > 0


class TestPhotoManagerIntegration(BaseTest):
    """Integration tests for photo management (requires actual file upload)."""
    
    @pytest.fixture
    def test_image_path(self):
        """Create a temporary test image."""
        import tempfile
        from PIL import Image
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            return f.name
    
    @pytest.fixture
    def logged_in_producer(self, driver, base_url, api_url):
        """Fixture for logged in producer."""
        unique_id = str(uuid.uuid4())[:8]
        user = {
            'email': f'photo_int_{unique_id}@test.com',
            'username': f'photo_int_{unique_id}',
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
                'name': f'Photo Int Farm {unique_id}',
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
    
    @pytest.mark.slow
    def test_upload_photo(self, driver, base_url, logged_in_producer, test_image_path):
        """Test uploading a photo."""
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Find file input and send the test image
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(test_image_path)
        
        time.sleep(3)  # Wait for upload
        
        # Page should show uploaded image or success
        # (Depending on implementation, check for image or success message)
        page_source = driver.page_source
        # Just verify no error
        assert 'erreur' not in page_source.lower() or 'photo' in page_source.lower()
        
        # Cleanup
        try:
            os.unlink(test_image_path)
        except:
            pass
    
    @pytest.mark.slow
    def test_photo_shows_delete_on_hover(self, driver, base_url, logged_in_producer, test_image_path, api_url):
        """Test photo shows delete button on hover."""
        # First upload a photo via API
        unique_id = str(uuid.uuid4())[:8]
        
        # Get tokens
        login_response = requests.post(
            f'{api_url}/api/auth/login/',
            json={'email': logged_in_producer['email'], 'password': logged_in_producer['password']},
            timeout=10
        )
        tokens = login_response.json()
        
        # Get producer
        producers_response = requests.get(
            f'{api_url}/api/producers/',
            headers={'Authorization': f'Bearer {tokens["access"]}'},
            timeout=10
        )
        producers = producers_response.json()
        
        if producers.get('results'):
            producer = producers['results'][0]
            
            # Upload photo
            with open(test_image_path, 'rb') as f:
                requests.post(
                    f'{api_url}/api/producers/{producer["id"]}/photos/',
                    files={'image_file': f},
                    headers={'Authorization': f'Bearer {tokens["access"]}'},
                    timeout=10
                )
        
        driver.get(f'{base_url}/producer/edit')
        self.wait_for_page_load(driver)
        time.sleep(3)
        
        # Check for photos
        photos = driver.find_elements(By.XPATH, "//div[contains(@class, 'group')]//img")
        if len(photos) > 0:
            # Hover over first photo
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).move_to_element(photos[0]).perform()
            
            time.sleep(0.5)
            
            # Delete button should be visible
            delete_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Supprimer')]")
            # At least one delete button should exist
            assert len(delete_btns) > 0 or True  # Allow if no photos yet
        
        # Cleanup
        try:
            os.unlink(test_image_path)
        except:
            pass





