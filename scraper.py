from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time
import pandas as pd

# ⚙️ Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode sans interface (désactive si tu veux voir l'exécution)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# 🔗 URL de la catégorie (exemple : T-Shirts Hommes)
URL = "https://www.decathlon.fr/homme/tee-shirts"
driver.get(URL)
time.sleep(5)  # Attente pour charger la page

# ✅ Gestion de la popup de cookies et autres overlays
try:
    popup = driver.find_element(By.CSS_SELECTOR, "div.didomi-popup-container")
    close_button = popup.find_element(By.CSS_SELECTOR, "button")
    close_button.click()
    time.sleep(2)
    print("✅ Popup fermée avec succès.")
except NoSuchElementException:
    print("✅ Aucune popup détectée.")

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

driver.quit()  # Fermer le driver après cette phase

# 📌 Scraping des détails de chaque produit
detailed_data = []
driver = webdriver.Chrome(service=service, options=chrome_options)

for lien in produits_data:
    try:
        driver.get(lien)
        time.sleep(3)  # Attente du chargement

        # 📌 Extraction des informations du produit
        def extract_text(selector, default="Non disponible"):
            try:
                return driver.find_element(By.CSS_SELECTOR, selector).text.strip()
            except NoSuchElementException:
                return default

        nom = extract_text("h1.product-name")
        prix = extract_text("span.vtmn-price").replace("€", "").replace(",", ".")
        description = extract_text("p.vtmn-text-base.vtmn-mt-2")
        avis = extract_text("span.vtmn-rating_comment--primary").replace("/5", "").replace(",", ".")
        nb_avis = extract_text("span.svelte-o73tzc").replace("Voir les ", "").replace(" avis", "")

        # ✅ Vérification des types de valeurs
        try:
            avis = float(avis)
        except:
            avis = "Non disponible"

        try:
            nb_avis = int(nb_avis)
        except:
            nb_avis = "Non disponible"

        # 📌 Sélection et récupération des tailles et stocks
        disponibilites_tailles = []
        tailles = driver.find_elements(By.CSS_SELECTOR, "button.variant-list__button")

        if tailles:  # S'il y a plusieurs tailles, les parcourir
            for taille in tailles:
                try:
                    taille_nom = taille.get_attribute("title") or taille.text.strip()

                    if taille.get_attribute("aria-current") == "true":
                        print(f"✅ Taille {taille_nom} déjà sélectionnée.")
                        continue

                    if not taille.is_displayed() or not taille.is_enabled():
                        print(f"⚠️ Taille {taille_nom} non cliquable, passage à la suivante.")
                        continue

                    driver.execute_script("arguments[0].scrollIntoView();", taille)
                    time.sleep(1)

                    try:
                        taille.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", taille)

                    time.sleep(2)  # Attente pour la mise à jour du stock

                    stock = extract_text("span.stock-info__availability-text")
                    disponibilites_tailles.append(f"{taille_nom}: {stock}")

                except Exception as e:
                    print(f"⚠️ Erreur lors du clic sur la taille {taille_nom}: {e}")

            disponibilite = " | ".join(disponibilites_tailles) if disponibilites_tailles else "Non disponible"
        else:  # Si pas de tailles, récupérer la disponibilité globale
            disponibilite = extract_text("div.stock-info span.vtmn-text-content-primary")

        # 📌 Récupération de l'image
        try:
            image_url = driver.find_element(By.CSS_SELECTOR, "img[alt]").get_attribute("src")
        except:
            image_url = "Non disponible"

        # ✅ Stocker les données
        detailed_data.append([nom, prix, lien, description, avis, nb_avis, disponibilite, image_url])
        print(f"📌 Détails récupérés : {nom} - {prix}€ - {avis} étoiles - {nb_avis} avis - Stock: {disponibilite}")

    except Exception as e:
        print(f"❌ Erreur sur {lien} : {e}")

driver.quit()  # Fermeture du driver

# 📌 Sauvegarde des données
df = pd.DataFrame(detailed_data, columns=["Nom", "Prix", "Lien", "Description", "Avis", "Nombre d'avis", "Disponibilité", "Image"])
df.to_csv("decathlon_produits_details.csv", index=False)

print("✅ Scraping terminé ! Données enregistrées dans 'decathlon_produits_details.csv'")
