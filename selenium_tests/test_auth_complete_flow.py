"""
Test du flux complet d'inscription et de connexion pour reproduire le problème utilisateur.
"""
import pytest
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from base_test import BaseTest


class TestAuthCompleteFlow(BaseTest):
    """Test du flux complet d'authentification."""
    
    def test_complete_registration_and_login_flow(self, driver, base_url):
        """Test complet : inscription puis connexion immédiate."""
        print("\n" + "="*60)
        print("TEST COMPLET : INSCRIPTION + CONNEXION")
        print("="*60)
        
        # Générer des identifiants uniques
        unique_id = str(uuid.uuid4())[:8]
        test_email = f'complete_test_{unique_id}@test.com'
        test_username = f'complete_user_{unique_id}'
        test_password = 'TestPassword123!'
        
        print(f"\n📧 Email: {test_email}")
        print(f"👤 Username: {test_username}")
        print(f"🔒 Password: {test_password}")
        
        # ========== ÉTAPE 1 : INSCRIPTION ==========
        print("\n" + "-"*60)
        print("ÉTAPE 1 : INSCRIPTION")
        print("-"*60)
        
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        print(f"✅ Page d'inscription chargée: {driver.current_url}")
        
        # Remplir le formulaire
        email_input = driver.find_element(By.ID, 'email')
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        password_confirm_input = driver.find_element(By.ID, 'password_confirm')
        
        email_input.clear()
        email_input.send_keys(test_email)
        print(f"✅ Email saisi")
        
        username_input.clear()
        username_input.send_keys(test_username)
        print(f"✅ Username saisi")
        
        password_input.clear()
        password_input.send_keys(test_password)
        print(f"✅ Password saisi")
        
        password_confirm_input.clear()
        password_confirm_input.send_keys(test_password)
        print(f"✅ Password confirm saisi")
        
        # Soumettre
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        print("✅ Formulaire soumis")
        
        # Attendre et vérifier
        time.sleep(5)
        current_url = driver.current_url
        page_source = driver.page_source
        
        print(f"\n📍 URL après soumission: {current_url}")
        
        # Vérifier les erreurs - chercher spécifiquement les messages d'erreur visibles
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        visible_errors = [
            'Erreur lors de l\'inscription',
            'Les mots de passe ne correspondent pas',
            'existe déjà',
            'Un utilisateur avec',
            'doit contenir au moins'
        ]
        
        has_visible_error = any(error in body_text for error in visible_errors)
        
        if has_visible_error:
            print(f"\n❌ ERREUR VISIBLE DÉTECTÉE:")
            print(body_text[:500])
            driver.save_screenshot('screenshots/complete_flow_register_error.png')
            pytest.fail("Erreur visible lors de l'inscription")
        
        if '/login' in current_url:
            print("✅ Inscription réussie - Redirection vers /login")
        else:
            print(f"⚠️ URL inattendue après inscription: {current_url}")
            driver.save_screenshot('screenshots/complete_flow_register_unexpected.png')
        
        # ========== ÉTAPE 2 : CONNEXION ==========
        print("\n" + "-"*60)
        print("ÉTAPE 2 : CONNEXION")
        print("-"*60)
        
        # S'assurer qu'on est sur la page de connexion
        if '/login' not in driver.current_url:
            driver.get(f'{base_url}/login')
            self.wait_for_page_load(driver)
            time.sleep(2)
        
        print(f"✅ Page de connexion chargée: {driver.current_url}")
        
        # Remplir le formulaire de connexion
        email_input = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'password')
        
        email_input.clear()
        email_input.send_keys(test_email)
        print(f"✅ Email de connexion saisi")
        
        password_input.clear()
        password_input.send_keys(test_password)
        print(f"✅ Password de connexion saisi")
        
        # Soumettre
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        print("✅ Formulaire de connexion soumis")
        
        # Attendre et vérifier
        time.sleep(5)
        current_url = driver.current_url
        page_source = driver.page_source
        
        print(f"\n📍 URL après connexion: {current_url}")
        
        # Vérifier les erreurs - chercher spécifiquement les messages d'erreur visibles
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        visible_errors = [
            'Erreur de connexion',
            'Email ou mot de passe incorrect',
            'incorrect',
            'invalide'
        ]
        
        has_visible_error = any(error in body_text for error in visible_errors)
        
        if has_visible_error:
            print(f"\n❌ ERREUR VISIBLE DÉTECTÉE:")
            print(body_text[:500])
            driver.save_screenshot('screenshots/complete_flow_login_error.png')
            pytest.fail("Erreur visible lors de la connexion")
        
        if '/login' not in current_url:
            print("✅ Connexion réussie - Redirection vers la page d'accueil")
            
            # Vérifier qu'on est bien connecté
            time.sleep(2)
            page_source = driver.page_source
            
            if 'Déconnexion' in page_source or 'Mon Profil' in page_source:
                print("✅ État de connexion confirmé dans la page")
            else:
                print("⚠️ Pas d'indicateur de connexion dans la page")
        else:
            print(f"⚠️ Toujours sur /login - Connexion peut-être échouée")
            driver.save_screenshot('screenshots/complete_flow_login_failed.png')
        
        # Capture finale
        driver.save_screenshot('screenshots/complete_flow_final.png')
        print("\n✅ Test terminé - Capture d'écran sauvegardée")
        
        print("\n" + "="*60)
        print("RÉSUMÉ")
        print("="*60)
        print(f"✅ Inscription: {'Réussie' if '/login' in driver.current_url or '/register' not in driver.current_url else 'Échouée'}")
        print(f"✅ Connexion: {'Réussie' if '/login' not in driver.current_url else 'Échouée'}")
    
    def test_register_with_existing_email(self, driver, base_url):
        """Test d'inscription avec un email existant pour voir le message d'erreur."""
        print("\n" + "="*60)
        print("TEST : INSCRIPTION AVEC EMAIL EXISTANT")
        print("="*60)
        
        # D'abord créer un utilisateur
        unique_id = str(uuid.uuid4())[:8]
        test_email = f'existing_{unique_id}@test.com'
        test_username = f'existing_{unique_id}'
        test_password = 'TestPassword123!'
        
        # Inscription initiale
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        driver.find_element(By.ID, 'email').send_keys(test_email)
        driver.find_element(By.ID, 'username').send_keys(test_username)
        driver.find_element(By.ID, 'password').send_keys(test_password)
        driver.find_element(By.ID, 'password_confirm').send_keys(test_password)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(5)
        
        print(f"✅ Premier utilisateur créé: {test_email}")
        
        # Essayer de s'inscrire à nouveau avec le même email
        print("\n--- Tentative d'inscription avec email existant ---")
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        driver.find_element(By.ID, 'email').send_keys(test_email)
        driver.find_element(By.ID, 'username').send_keys(f'different_{unique_id}')
        driver.find_element(By.ID, 'password').send_keys(test_password)
        driver.find_element(By.ID, 'password_confirm').send_keys(test_password)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(5)
        
        # Vérifier le message d'erreur
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        print("\n--- Message d'erreur affiché ---")
        print(page_text[:1000])
        
        if 'existe déjà' in page_text or 'already exists' in page_text.lower():
            print("✅ Message d'erreur correct affiché")
        else:
            print("⚠️ Message d'erreur attendu non trouvé")
        
        driver.save_screenshot('screenshots/register_existing_email.png')

