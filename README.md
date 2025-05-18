# 🛒 Decathlon Web Scraper

Un scraper web automatisé qui extrait les informations des produits sur le site de Decathlon, développé en Python avec Selenium.

---

## 🔍 Objectif

Ce projet permet de parcourir dynamiquement une catégorie de produits (ex. : T-shirts pour hommes) sur Decathlon.fr et de collecter les données importantes pour chaque article affiché, telles que :

- Nom du produit
- Prix
- URL du produit
- Détails supplémentaires (si disponibles)

---

## 🛠️ Technologies utilisées

- **Python 3**
- **Selenium**
- **ChromeDriver**
- **pandas** (pour l’export CSV)

---

## 📦 Fichiers

```
decathlon-scraper/
├── scraper.py                     # Script principal
├── chromedriver.exe              # WebDriver Chrome local (Windows)
├── decathlon_produits_details.csv  # Données extraites
├── screen scraping.png           # Capture d’écran du scraping
```

---

## ▶️ Comment exécuter le projet

### 🔧 Prérequis

- Python 3 installé
- Google Chrome installé
- `chromedriver.exe` compatible avec ta version de Chrome
- Installer les dépendances :

```bash
pip install selenium pandas
```

### 🚀 Lancer le script

```bash
python scraper.py
```

Cela lancera un navigateur Chrome en arrière-plan, naviguera vers une page produit de Decathlon et collectera les infos produits automatiquement.

Les résultats sont enregistrés dans un fichier CSV nommé **`decathlon_produits_details.csv`**.

---

## 📸 Résultat visuel

Une capture d’écran (`screen scraping.png`) est incluse pour illustrer une session de scraping en cours.

---

## 🔐 À propos de l’usage

⚠️ Ce script est à but éducatif.  
Le scraping de sites web doit respecter les conditions d'utilisation du site ciblé. Utilisez ce projet de manière responsable.

---

## 👨‍💻 Auteur

- **Noam** – Étudiant en informatique, passionné par l'automatisation et la collecte de données.

---

## 📄 Licence

Ce projet est open-source, vous pouvez le réutiliser, l'adapter ou le modifier à des fins personnelles ou pédagogiques.
