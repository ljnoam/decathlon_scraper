from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# ⚙️ Configuration Selenium
chrome_options = Options()
# Use the new headless mode for recent Chrome versions and disable GPU to avoid GPU-related errors on some systems
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # reduce noisy logs
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

# Use webdriver-manager to download and use the ChromeDriver matching the installed Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 🔗 URL de la catégorie (exemple : T-Shirts Femmes)
URL = "https://www.decathlon.fr/femme/tee-shirts"
driver.get(URL)
time.sleep(3)

# 🔽 Pagination et collecte des liens (limitées aux 5 premières pages)
produits_data = []
current_page = 1
max_pages = 200  # maximum pages to scrape (was 5) - adjust if needed
wait = WebDriverWait(driver, 15)
while current_page <= max_pages:
    # Scroller pour forcer le chargement des cards
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    # Récupération des produits sur la page courante
    produits = driver.find_elements(By.CSS_SELECTOR, "div.dpb-holder")
    print(f"🛍️ Page {current_page} — produits trouvés sur la page : {len(produits)}")

    for produit in produits:
        try:
            lien = produit.find_element(By.CSS_SELECTOR, "a.dpb-product-model-link").get_attribute("href")
            if lien and not lien.startswith("http"):
                lien = "https://www.decathlon.fr" + lien
            if lien and lien not in produits_data:
                produits_data.append(lien)
        except Exception as e:
            print(f"⚠️ Erreur sur un produit : {e}")

    # Si on a atteint le maximum de pages demandé, sortir
    if current_page >= max_pages:
        break

    # Tenter de cliquer sur le bouton 'Page suivante'
    try:
        next_btn = None
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "nav[aria-label*='Pagination de la liste de produits'] button[data-direction='right']")
        except Exception:
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Page suivante de la liste de produits']")
            except Exception:
                next_btn = None

        if not next_btn:
            print("ℹ️ Bouton 'Page suivante' introuvable — arrêt de la pagination.")
            break

        if next_btn.get_attribute('disabled') is not None or not next_btn.is_enabled():
            print("ℹ️ Bouton 'Page suivante' désactivé — fin de la pagination.")
            break

        # mémoriser le premier lien de la page pour détecter le changement
        try:
            first_link_before = produits[0].find_element(By.CSS_SELECTOR, "a.dpb-product-model-link").get_attribute("href") if produits else None
        except Exception:
            first_link_before = None

        # cliquer sur 'suivant' via JS
        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
        time.sleep(0.3)
        try:
            driver.execute_script("arguments[0].click();", next_btn)
        except Exception:
            try:
                next_btn.click()
            except Exception as e:
                print(f"⚠️ Impossible de cliquer sur 'suivant' : {e}")
                break

        # attendre que le premier lien change ou que de nouveaux produits apparaissent
        def first_link_changed(d):
            try:
                new_produits = d.find_elements(By.CSS_SELECTOR, "div.dpb-holder")
                if not new_produits:
                    return False
                new_first = new_produits[0].find_element(By.CSS_SELECTOR, "a.dpb-product-model-link").get_attribute("href")
                return new_first != first_link_before
            except Exception:
                return False

        try:
            wait.until(first_link_changed)
        except Exception:
            time.sleep(2)

        current_page += 1
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Erreur lors de la pagination : {e}")
        break

print(f"🛍️ Total de liens produits collectés : {len(produits_data)}")

driver.quit()

# 📌 Scraping des détails de chaque produit
detailed_data = []
driver = webdriver.Chrome(service=service, options=chrome_options)

for lien in produits_data:
    try:
        driver.get(lien)
        time.sleep(3)

        # ✅ Fermer la popup de cookies si présente
        try:
            popup = driver.find_element(By.CSS_SELECTOR, "div.didomi-popup-container")
            close_button = popup.find_element(By.CSS_SELECTOR, "button")
            close_button.click()
            time.sleep(2)
            print("✅ Popup fermée avec succès.")
        except NoSuchElementException:
            pass

        def extract_text(selector, default="Non disponible"):
            try:
                return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            except NoSuchElementException:
                return default


        # 📌 Récupération des informations
        nom = extract_text("h1.product-name")
        prix = extract_text("span.vtmn-price").replace("€", "").replace(",", ".")
        description = extract_text("p.vtmn-text-base.vtmn-mt-2")
        avis = extract_text("span.vtmn-rating_comment--primary").replace("/5", "").replace(",", ".")
        try:
            avis = float(avis)
        except:
            avis = "Non disponible"

        # 📌 Récupération de la marque
        marque = extract_text("a[aria-label*='produits de la marque']")


        # 📌 Gestion des couleurs disponibles
        couleurs_dispo = []
        try:
            couleurs = driver.find_elements(By.CSS_SELECTOR, "button.variant-list__button")
            for couleur in couleurs:
                couleur_nom = couleur.get_attribute("title")
                if couleur_nom:
                    couleurs_dispo.append(couleur_nom)
        except:
            couleurs_dispo = ["Non disponible"]

        couleurs_str = ", ".join(couleurs_dispo)

        # 📌 Gestion des tailles et disponibilités
        disponibilites_tailles = []
        try:
            tailles = driver.find_elements(By.CSS_SELECTOR, "li.vtmn-sku-selector__item")
            if tailles:
                for taille in tailles:
                    try:
                        taille_nom = taille.get_attribute("aria-label").split(",")[0].replace("Taille ", "").strip()
                        stock_statut = "En stock" if "inStock" in taille.get_attribute("class") else "Rupture"

                        disponibilites_tailles.append(f"{taille_nom}: {stock_statut}")

                    except Exception as e:
                        print(f"⚠️ Erreur sur la taille {taille_nom}: {e}")

            disponibilite = " | ".join(disponibilites_tailles) if disponibilites_tailles else "Non disponible"

        except:
            disponibilite = "Non disponible"

        # ✅ Stocker les données (sans 'Nombre d'avis' ni 'Image')
        detailed_data.append([nom, marque, prix, lien, description, avis, couleurs_str, disponibilite])
        print(f"📌 Détails récupérés : titre:{nom} - marque:{marque} - {prix}€ - {avis} étoiles - Couleurs: {couleurs_str} - Stock: {disponibilite}")

    except Exception as e:
        print(f"❌ Erreur sur {lien} : {e}")

driver.quit()

# 📌 Sauvegarde des données (sans 'Nombre d'avis' ni 'Image')
df = pd.DataFrame(detailed_data, columns=["Nom", "Marque", "Prix", "Lien", "Description", "Avis", "Couleurs Disponibles", "Disponibilité"])
df.to_csv("decathlon_produits_details.csv", index=False)

print("✅ Scraping terminé ! Données enregistrées dans 'decathlon_produits_details.csv'")
