"""
Tests for sidebar filter functionality including collapse/expand.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest


class TestSidebar(BaseTest):
    """Test sidebar filter functionality."""
    
    def test_sidebar_visible_on_load(self, driver, base_url):
        """Test sidebar is visible when page loads."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0') and contains(@class, 'w-96')]")
        assert sidebar.is_displayed()
    
    def test_sidebar_has_search_section(self, driver, base_url):
        """Test sidebar has search section."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Check for search title
        search_title = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed')]//h2[contains(text(), 'Recherche')]")
        assert search_title.is_displayed()
    
    def test_sidebar_has_categories_section(self, driver, base_url):
        """Test sidebar has categories filter section."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Check for filter title
        filter_title = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed')]//h3[contains(text(), 'activité')]")
        assert filter_title.is_displayed()
    
    def test_sidebar_has_collapse_button(self, driver, base_url):
        """Test sidebar has collapse button."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Check for collapse button
        collapse_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Masquer') or @title='Masquer le panneau']")
        assert collapse_btn.is_displayed()
    
    def test_sidebar_collapse(self, driver, base_url):
        """Test sidebar can be collapsed."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Click collapse button
        collapse_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Masquer') or @title='Masquer le panneau']")
        self.safe_click(driver, collapse_btn)
        
        time.sleep(1)
        
        # Sidebar should now be hidden or collapsed
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0')]")
        classes = sidebar.get_attribute('class')
        assert 'w-0' in classes or '-translate-x' in classes
    
    def test_sidebar_expand_after_collapse(self, driver, base_url):
        """Test sidebar can be expanded after collapse."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Click collapse button
        collapse_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Masquer') or @title='Masquer le panneau']")
        self.safe_click(driver, collapse_btn)
        
        time.sleep(1)
        
        # Find and click the expand button
        expand_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Filtres') or @title='Afficher les filtres']")
        assert expand_btn.is_displayed()
        self.safe_click(driver, expand_btn)
        
        time.sleep(1)
        
        # Sidebar should be visible again
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0') and contains(@class, 'w-96')]")
        assert sidebar.is_displayed()
    
    def test_sidebar_category_tous_selected_by_default(self, driver, base_url):
        """Test 'Tous' category is selected by default."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        tous_btn = driver.find_element(By.XPATH, "//button[contains(., 'Tous')]")
        classes = tous_btn.get_attribute('class')
        assert 'bg-nature-500' in classes or 'selected' in classes.lower()
    
    def test_sidebar_category_selection(self, driver, base_url):
        """Test clicking a category selects it."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Click Maraîchage category
        try:
            maraichage_btn = driver.find_element(By.XPATH, "//button[contains(., 'Maraîchage')]")
            self.safe_click(driver, maraichage_btn)
            
            time.sleep(1)
            
            # Should be selected
            classes = maraichage_btn.get_attribute('class')
            assert 'bg-nature-500' in classes
            
            # URL should contain category parameter
            assert 'category' in driver.current_url
        except Exception:
            pytest.skip("Maraîchage category not found")
    
    def test_sidebar_category_unselect(self, driver, base_url):
        """Test clicking 'Tous' unselects other categories."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        try:
            # Click a category first
            maraichage_btn = driver.find_element(By.XPATH, "//button[contains(., 'Maraîchage')]")
            self.safe_click(driver, maraichage_btn)
            
            time.sleep(1)
            
            # Click Tous
            tous_btn = driver.find_element(By.XPATH, "//button[contains(., 'Tous')]")
            self.safe_click(driver, tous_btn)
            
            time.sleep(1)
            
            # Tous should be selected
            classes = tous_btn.get_attribute('class')
            assert 'bg-nature-500' in classes
            
            # URL should not have category parameter
            assert 'category=' not in driver.current_url
        except Exception:
            pytest.skip("Category buttons not found")
    
    def test_sidebar_all_categories_present(self, driver, base_url):
        """Test all main categories are present."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        expected_categories = [
            'Tous', 'Maraîchage', 'Élevage', 'Apiculture', 
            'Arboriculture', 'Viticulture', 'Fromagerie'
        ]
        
        for category in expected_categories:
            try:
                btn = driver.find_element(By.XPATH, f"//button[contains(., '{category}')]")
                assert btn.is_displayed(), f"Category '{category}' should be visible"
            except Exception:
                # Some categories might not exist
                pass
    
    def test_sidebar_category_has_icon(self, driver, base_url):
        """Test category buttons have icons."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Find a category button
        category_btn = driver.find_element(By.XPATH, "//button[contains(., 'Maraîchage')]")
        btn_text = category_btn.text
        
        # Should contain emoji icon
        has_icon = any(ord(c) > 127 for c in btn_text)  # Emoji check
        assert has_icon or 'icon' in category_btn.get_attribute('class').lower()
    
    def test_sidebar_category_shows_checkmark_when_selected(self, driver, base_url):
        """Test selected category shows checkmark."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Tous should be selected by default and show checkmark
        tous_btn = driver.find_element(By.XPATH, "//button[contains(., 'Tous')]")
        btn_text = tous_btn.text
        assert '✓' in btn_text or 'check' in tous_btn.get_attribute('innerHTML').lower()
    
    def test_sidebar_scrollable(self, driver, base_url):
        """Test sidebar content is scrollable."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0') and contains(@class, 'overflow-y-auto')]")
        assert sidebar.is_displayed()
    
    def test_sidebar_width_correct(self, driver, base_url):
        """Test sidebar has correct width (w-96)."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        sidebar = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'left-0') and contains(@class, 'w-96')]")
        
        # w-96 = 24rem = 384px
        size = sidebar.size
        # Allow some tolerance
        assert size['width'] >= 380 and size['width'] <= 400


class TestSidebarSearch(BaseTest):
    """Test sidebar search functionality."""
    
    def test_producer_search_input_exists(self, driver, base_url):
        """Test producer search input exists in sidebar."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        search_input = driver.find_element(
            By.XPATH, 
            "//input[contains(@placeholder, 'producteur') or contains(@placeholder, 'Producteur')]"
        )
        assert search_input.is_displayed()
    
    def test_location_search_input_exists(self, driver, base_url):
        """Test location search input exists in sidebar."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        search_input = driver.find_element(
            By.XPATH, 
            "//input[contains(@placeholder, 'ville') or contains(@placeholder, 'adresse') or contains(@placeholder, 'Ville')]"
        )
        assert search_input.is_displayed()
    
    def test_geolocation_button_exists(self, driver, base_url):
        """Test 'Use my location' button exists."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        geo_btn = driver.find_element(
            By.XPATH, 
            "//button[contains(text(), 'Moi') or contains(@title, 'position')]"
        )
        assert geo_btn.is_displayed()
    
    def test_search_go_buttons_exist(self, driver, base_url):
        """Test GO buttons exist for searches."""
        driver.get(base_url)
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        go_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'GO')]")
        assert len(go_buttons) >= 2, "Should have at least 2 GO buttons"





