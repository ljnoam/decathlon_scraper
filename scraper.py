from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time
import pandas as pd

# ⚙️ Configuration Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# 🔗 URL de la catégorie (exemple : T-Shirts Hommes)
URL = "https://www.decathlon.fr/homme/tee-shirts"
driver.get(URL)
time.sleep(5)

# 🔽 Scroll pour charger plus de produits
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# 🔎 Récupération des produits
produits = driver.find_elements(By.CSS_SELECTOR, "div.dpb-holder")
print(f"🛍️ Nombre de produits trouvés : {len(produits)}")

# 📌 Extraction des liens des produits
produits_data = []
for produit in produits:
    try:
        lien = produit.find_element(By.CSS_SELECTOR, "a.dpb-product-model-link").get_attribute("href")
        if not lien.startswith("http"):
            lien = "https://www.decathlon.fr" + lien
        produits_data.append(lien)
    except Exception as e:
        print(f"⚠️ Erreur sur un produit : {e}")

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
        nb_avis = extract_text("span.svelte-o73tzc").replace("Voir les ", "").replace(" avis", "")

        try:
            avis = float(avis)
        except:
            avis = "Non disponible"

        try:
            nb_avis = int(nb_avis)
        except:
            nb_avis = "Non disponible"

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

        # 📌 Récupération de l'image
        try:
            image_url = driver.find_element(By.CSS_SELECTOR, "img[alt]").get_attribute("src")
        except:
            image_url = "Non disponible"

        # ✅ Stocker les données
        detailed_data.append([nom, marque, prix, lien, description, avis, nb_avis, couleurs_str, disponibilite, image_url])
        print(f"📌 Détails récupérés : titre:{nom} - marque:{marque} - {prix}€ - {avis} étoiles - {nb_avis} avis - Couleurs: {couleurs_str} - Stock: {disponibilite}")

    except Exception as e:
        print(f"❌ Erreur sur {lien} : {e}")

driver.quit()

# 📌 Sauvegarde des données
df = pd.DataFrame(detailed_data, columns=["Nom", "Marque", "Prix", "Lien", "Description", "Avis", "Nombre d'avis", "Couleurs Disponibles", "Disponibilité", "Image"])
df.to_csv("decathlon_produits_details.csv", index=False)

print("✅ Scraping terminé ! Données enregistrées dans 'decathlon_produits_details.csv'")
