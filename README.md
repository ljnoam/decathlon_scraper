Instructions pour exécuter le scraper

Prérequis:
- Python 3.8+
- Chrome installé (version récente)

Installer les dépendances:

pip install -r requirements.txt

Exécuter:

python scraper.py

Remarques:
- Le script utilise `webdriver-manager` pour télécharger automatiquement la version de ChromeDriver qui correspond à votre navigateur Chrome.
- Si vous rencontrez des erreurs liées au GPU, le script désactive le GPU et utilise le mode headless récent de Chrome.
 
Paramètres personnalisables:
- Par défaut le scraper parcourt jusqu'à 200 pages (variable `max_pages` dans `scraper.py`).
- Pour réduire/incrémenter le nombre de pages, éditez la variable `max_pages` au début de la section "Pagination" dans `scraper.py`.

