import requests
from dotenv import load_dotenv
import os

# Chemin du répertoire parent du script en cours
parent_directory = os.path.dirname(__file__)

# Charger les variables d'environnement depuis le fichier .env situé dans le répertoire parent
load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), '../.env'))

# Récupérer les valeurs des variables d'environnement
url = f"http://localhost:{os.getenv('PORT')}/upload"
files = {'file': open(os.path.join(parent_directory, 'test.jpg'), 'rb')}
headers = {'API-Key': os.getenv('API_KEY')}

# Effectuer la requête POST pour envoyer le fichier
response = requests.post(url, files=files, headers=headers)

# Afficher la réponse JSON du serveur
print(response.json())
