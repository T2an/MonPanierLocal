"""
Tests détaillés pour diagnostiquer les problèmes d'inscription et de connexion.
Ces tests capturent et affichent toutes les erreurs pour faciliter le diagnostic.
"""
import pytest
import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from base_test import BaseTest


class TestAuthDetailed(BaseTest):
    """Tests détaillés d'authentification avec diagnostic."""
    
    def test_register_detailed(self, driver, base_url):
        """Test d'inscription avec capture détaillée des erreurs."""
        print("\n=== TEST D'INSCRIPTION DÉTAILLÉ ===")
        
        # Générer des identifiants uniques
        unique_id = str(uuid.uuid4())[:8]
        test_email = f'test_register_{unique_id}@test.com'
        test_username = f'test_user_{unique_id}'
        test_password = 'TestPassword123!'
        
        print(f"Email: {test_email}")
        print(f"Username: {test_username}")
        print(f"Password: {test_password}")
        
        # Aller sur la page d'inscription
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Capturer la page source initiale
        print("\n--- Page d'inscription chargée ---")
        print(f"URL: {driver.current_url}")
        
        # Vérifier que les champs existent
        try:
            email_input = driver.find_element(By.ID, 'email')
            username_input = driver.find_element(By.ID, 'username')
            password_input = driver.find_element(By.ID, 'password')
            password_confirm_input = driver.find_element(By.ID, 'password_confirm')
            is_producer_checkbox = driver.find_element(By.ID, 'is_producer')
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            
            print("✅ Tous les champs du formulaire sont présents")
        except NoSuchElementException as e:
            print(f"❌ Champ manquant: {e}")
            driver.save_screenshot('screenshots/register_missing_fields.png')
            raise
        
        # Remplir le formulaire
        print("\n--- Remplissage du formulaire ---")
        try:
            email_input.clear()
            email_input.send_keys(test_email)
            print(f"✅ Email saisi: {email_input.get_attribute('value')}")
            
            username_input.clear()
            username_input.send_keys(test_username)
            print(f"✅ Username saisi: {username_input.get_attribute('value')}")
            
            password_input.clear()
            password_input.send_keys(test_password)
            print(f"✅ Password saisi: {'*' * len(test_password)}")
            
            password_confirm_input.clear()
            password_confirm_input.send_keys(test_password)
            print(f"✅ Password confirm saisi: {'*' * len(test_password)}")
            
            # Ne pas cocher is_producer pour ce test
            if is_producer_checkbox.is_selected():
                is_producer_checkbox.click()
            print("✅ Checkbox is_producer non cochée")
            
        except Exception as e:
            print(f"❌ Erreur lors du remplissage: {e}")
            driver.save_screenshot('screenshots/register_fill_error.png')
            raise
        
        # Soumettre le formulaire
        print("\n--- Soumission du formulaire ---")
        try:
            submit_btn.click()
            print("✅ Bouton de soumission cliqué")
        except Exception as e:
            print(f"❌ Erreur lors de la soumission: {e}")
            driver.save_screenshot('screenshots/register_submit_error.png')
            raise
        
        # Attendre la réponse
        print("\n--- Attente de la réponse ---")
        time.sleep(5)
        
        # Capturer l'état après soumission
        current_url = driver.current_url
        page_source = driver.page_source
        
        print(f"URL après soumission: {current_url}")
        
        # Vérifier les erreurs dans la page
        error_indicators = [
            'erreur', 'error', 'Erreur', 'Error',
            'existe déjà', 'already exists',
            'correspondent pas', 'do not match',
            'caractères', 'characters',
            'requis', 'required'
        ]
        
        errors_found = []
        for indicator in error_indicators:
            if indicator.lower() in page_source.lower():
                errors_found.append(indicator)
        
        if errors_found:
            print(f"\n⚠️ Indicateurs d'erreur trouvés: {errors_found}")
        
        # Chercher un message d'erreur spécifique
        try:
            # Chercher un élément d'erreur
            error_elements = driver.find_elements(By.CSS_SELECTOR, 
                '[class*="error"], [class*="Error"], [role="alert"], .text-red, .text-error')
            
            if error_elements:
                print("\n--- Messages d'erreur trouvés ---")
                for i, elem in enumerate(error_elements):
                    error_text = elem.text.strip()
                    if error_text:
                        print(f"Erreur {i+1}: {error_text}")
        except Exception as e:
            print(f"Note: Impossible de trouver des éléments d'erreur: {e}")
        
        # Capturer la console du navigateur pour les erreurs JavaScript
        print("\n--- Vérification des erreurs JavaScript ---")
        try:
            logs = driver.get_log('browser')
            if logs:
                print("Erreurs JavaScript trouvées:")
                for log in logs:
                    if log['level'] in ['SEVERE', 'WARNING']:
                        print(f"  [{log['level']}] {log['message']}")
            else:
                print("✅ Aucune erreur JavaScript")
        except Exception as e:
            print(f"Note: Impossible d'accéder aux logs du navigateur: {e}")
        
        # Vérifier si on a été redirigé
        if '/login' in current_url:
            print("\n✅ Redirection vers /login détectée - Inscription probablement réussie")
        elif '/register' in current_url:
            print("\n⚠️ Toujours sur /register - Inscription peut-être échouée")
            driver.save_screenshot('screenshots/register_still_on_page.png')
            
            # Afficher le contenu de la page pour debug
            print("\n--- Contenu de la page (extrait) ---")
            # Chercher les messages d'erreur dans le HTML
            if 'ErrorMessage' in page_source or 'error' in page_source.lower():
                # Extraire le texte visible
                body_text = driver.find_element(By.TAG_NAME, 'body').text
                print(body_text[:500])  # Premiers 500 caractères
        else:
            print(f"\n⚠️ Redirection vers: {current_url}")
        
        # Prendre une capture d'écran finale
        driver.save_screenshot('screenshots/register_final_state.png')
        print("\n✅ Capture d'écran sauvegardée: screenshots/register_final_state.png")
    
    def test_login_detailed(self, driver, base_url):
        """Test de connexion avec capture détaillée des erreurs."""
        print("\n=== TEST DE CONNEXION DÉTAILLÉ ===")
        
        # D'abord, créer un utilisateur via l'API ou l'interface
        unique_id = str(uuid.uuid4())[:8]
        test_email = f'test_login_{unique_id}@test.com'
        test_username = f'test_login_{unique_id}'
        test_password = 'TestPassword123!'
        
        print(f"Email: {test_email}")
        print(f"Username: {test_username}")
        print(f"Password: {test_password}")
        
        # Essayer de s'inscrire d'abord
        print("\n--- Inscription préalable ---")
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        try:
            email_input = driver.find_element(By.ID, 'email')
            username_input = driver.find_element(By.ID, 'username')
            password_input = driver.find_element(By.ID, 'password')
            password_confirm_input = driver.find_element(By.ID, 'password_confirm')
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            
            email_input.send_keys(test_email)
            username_input.send_keys(test_username)
            password_input.send_keys(test_password)
            password_confirm_input.send_keys(test_password)
            
            submit_btn.click()
            time.sleep(5)
            
            if '/login' in driver.current_url:
                print("✅ Inscription réussie")
            else:
                print("⚠️ Inscription peut-être échouée, mais on continue le test de connexion")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'inscription: {e}")
            print("On continue quand même le test de connexion")
        
        # Maintenant tester la connexion
        print("\n--- Test de connexion ---")
        driver.get(f'{base_url}/login')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        print(f"URL: {driver.current_url}")
        
        try:
            email_input = driver.find_element(By.ID, 'email')
            password_input = driver.find_element(By.ID, 'password')
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            
            print("✅ Champs de connexion trouvés")
        except NoSuchElementException as e:
            print(f"❌ Champ manquant: {e}")
            driver.save_screenshot('screenshots/login_missing_fields.png')
            raise
        
        # Remplir le formulaire
        print("\n--- Remplissage du formulaire de connexion ---")
        email_input.clear()
        email_input.send_keys(test_email)
        password_input.clear()
        password_input.send_keys(test_password)
        
        print(f"✅ Formulaire rempli")
        print(f"  Email: {email_input.get_attribute('value')}")
        print(f"  Password: {'*' * len(test_password)}")
        
        # Soumettre
        print("\n--- Soumission du formulaire ---")
        submit_btn.click()
        time.sleep(5)
        
        # Vérifier le résultat
        current_url = driver.current_url
        page_source = driver.page_source
        
        print(f"URL après soumission: {current_url}")
        
        # Vérifier les erreurs
        if 'erreur' in page_source.lower() or 'error' in page_source.lower():
            print("\n⚠️ Indicateurs d'erreur trouvés dans la page")
            
            # Chercher les messages d'erreur
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR,
                    '[class*="error"], [class*="Error"], [role="alert"]')
                for elem in error_elements:
                    error_text = elem.text.strip()
                    if error_text:
                        print(f"  Erreur: {error_text}")
            except:
                pass
        
        # Vérifier la console JavaScript
        try:
            logs = driver.get_log('browser')
            if logs:
                print("\nErreurs JavaScript:")
                for log in logs:
                    if log['level'] in ['SEVERE', 'WARNING']:
                        print(f"  [{log['level']}] {log['message']}")
        except:
            pass
        
        # Vérifier si on est connecté
        if '/login' not in current_url:
            print("\n✅ Probablement connecté (pas sur /login)")
        else:
            print("\n⚠️ Toujours sur /login - Connexion peut-être échouée")
            driver.save_screenshot('screenshots/login_failed.png')
        
        driver.save_screenshot('screenshots/login_final_state.png')
        print("\n✅ Capture d'écran sauvegardée: screenshots/login_final_state.png")
    
    def test_register_error_messages(self, driver, base_url):
        """Test spécifique pour voir les messages d'erreur d'inscription."""
        print("\n=== TEST DES MESSAGES D'ERREUR D'INSCRIPTION ===")
        
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Test 1: Mots de passe différents
        print("\n--- Test 1: Mots de passe différents ---")
        unique_id = str(uuid.uuid4())[:8]
        
        driver.find_element(By.ID, 'email').send_keys(f'test1_{unique_id}@test.com')
        driver.find_element(By.ID, 'username').send_keys(f'test1_{unique_id}')
        driver.find_element(By.ID, 'password').send_keys('Password123!')
        driver.find_element(By.ID, 'password_confirm').send_keys('DifferentPassword123!')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        time.sleep(3)
        
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        print(f"Texte de la page après soumission:")
        print(page_text[:1000])
        
        driver.save_screenshot('screenshots/register_password_mismatch.png')
        
        # Réinitialiser pour le test suivant
        driver.get(f'{base_url}/register')
        self.wait_for_page_load(driver)
        time.sleep(2)
        
        # Test 2: Mot de passe trop court
        print("\n--- Test 2: Mot de passe trop court ---")
        unique_id = str(uuid.uuid4())[:8]
        
        driver.find_element(By.ID, 'email').send_keys(f'test2_{unique_id}@test.com')
        driver.find_element(By.ID, 'username').send_keys(f'test2_{unique_id}')
        driver.find_element(By.ID, 'password').send_keys('short')
        driver.find_element(By.ID, 'password_confirm').send_keys('short')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        time.sleep(3)
        
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        print(f"Texte de la page après soumission:")
        print(page_text[:1000])
        
        driver.save_screenshot('screenshots/register_short_password.png')




