import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

def load_environment():
    """Charge les variables d'environnement et assure la création du dossier de sauvegarde."""
    load_dotenv(dotenv_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), '../.env'))

    port = int(os.getenv('PORT', 5000))  # Valeur par défaut 5000 si non spécifié
    backup_folder = os.getenv('BACKUP_FOLDER', './uploads')  # Valeur par défaut './uploads'
    api_key = os.getenv('API_KEY', 'default_key')  # Valeur par défaut 'default_key'

    # Créer le dossier de backup si nécessaire
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    return port, backup_folder, api_key

# Charger les configurations
PORT, BACKUP_FOLDER, API_KEY = load_environment()

# Initialiser l'application Flask
app = Flask(__name__)
app.config['PORT'] = PORT
app.config['BACKUP_FOLDER'] = BACKUP_FOLDER
app.config['API_KEY'] = API_KEY

# Validation de la clé API
validate_api_key = lambda key: key == API_KEY

@app.route('/upload', methods=['POST'])
def upload_file():
    api_key = request.headers.get('API-Key')
    
    if not api_key:
        return jsonify({'error': 'API key is missing'}), 401
    
    if not validate_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Ajouter un horodatage au nom du fichier pour éviter les conflits
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(BACKUP_FOLDER, filename)
        file.save(filepath)
        return jsonify({'success': f'File saved as {filename}'}), 200
    except Exception as e:
        return jsonify({'error': f'File not saved: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)
