from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter en arrière-plan
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL de la catégorie à scraper
URL = "https://www.decathlon.fr/equipements-loisirs/montres"
driver.get(URL)
time.sleep(5)  # Laisse le temps à la page de charger

# Scroll pour charger plus de produits
for _ in range(5):  
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Récupération des produits
produits = driver.find_elements(By.CSS_SELECTOR, "div.dpb-holder")
print(f"Nombre de produits trouvés : {len(produits)}")

# Extraction des liens des produits
produits_data = []
for produit in produits:
    try:
        lien = produit.find_element(By.CSS_SELECTOR, "a.dpb-product-model-link").get_attribute("href")

        if not lien.startswith("http"):
            lien = "https://www.decathlon.fr" + lien  # Vérification du lien

        produits_data.append(lien)
    except Exception as e:
        print("Erreur sur un produit :", e)

# Fermer le driver après la première phase
driver.quit()

# Maintenant, on va scraper les détails de chaque produit
detailed_data = []
driver = webdriver.Chrome(service=service, options=chrome_options)

for lien in produits_data:
    try:
        driver.get(lien)
        time.sleep(3)  # Laisse le temps à la page de charger

        # Extraction des informations détaillées
        try:
            nom = driver.find_element(By.CSS_SELECTOR, "h1.product-name").text.strip()
        except:
            nom = "Non disponible"

        try:
            prix = driver.find_element(By.CSS_SELECTOR, "span.vtmn-price").text.strip().replace("€", "").replace(",", ".")
        except:
            prix = "Non disponible"

        try:
            description = driver.find_element(By.CSS_SELECTOR, "p.vtmn-text-base.vtmn-mt-2").text.strip()
        except:
            description = "Non disponible"

        try:
            avis = driver.find_element(By.CSS_SELECTOR, "span.vtmn-rating_comment--primary").text.strip()
            avis = float(avis.replace("/5", "").replace(",", "."))
        except:
            avis = "Non disponible"

        try:
            disponibilite = driver.find_element(By.CSS_SELECTOR, "div.stock-info span.vtmn-text-content-primary").text.strip()
        except:
            disponibilite = "Non disponible"

        try:
            image_url = driver.find_element(By.CSS_SELECTOR, "img[alt]").get_attribute("src")
        except:
            image_url = "Non disponible"

        # Ajout des données détaillées
        detailed_data.append([nom, prix, lien, description, avis, disponibilite, image_url])

        print(f"Détails récupérés : {nom} - {prix}€ - {avis} étoiles - Stock: {disponibilite}")
    
    except Exception as e:
        print(f"Erreur sur {lien} :", e)

# Fermer Selenium
driver.quit()

# Convertir en DataFrame Pandas
df = pd.DataFrame(detailed_data, columns=["Nom", "Prix", "Lien", "Description", "Avis", "Disponibilité", "Image"])

# Sauvegarde des données détaillées
df.to_csv("decathlon_produits_details.csv", index=False)

print("Scraping terminé ! Données enregistrées dans 'decathlon_produits_details.csv'")
