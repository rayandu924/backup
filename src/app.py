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
    max_folder_size = int(os.getenv('MAX_FOLDER_SIZE', 500 * 1024 * 1024))  # 500 MB par défaut

    # Créer le dossier de backup si nécessaire
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    return port, backup_folder, api_key, max_folder_size

def get_folder_size(folder):
    """Retourne la taille totale du dossier en octets."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

# Charger les configurations
PORT, BACKUP_FOLDER, API_KEY, MAX_FOLDER_SIZE = load_environment()

# Initialiser l'application Flask
app = Flask(__name__)
app.config['PORT'] = PORT
app.config['BACKUP_FOLDER'] = BACKUP_FOLDER
app.config['API_KEY'] = API_KEY
app.config['MAX_FOLDER_SIZE'] = MAX_FOLDER_SIZE

# Variable globale pour stocker la dernière mise à jour
last_update_time = None

# Validation de la clé API
validate_api_key = lambda key: key == API_KEY

@app.route('/upload', methods=['POST'])
def upload_file():
    global last_update_time

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

    # Vérifier si la taille actuelle du dossier dépasse la limite autorisée
    current_size = get_folder_size(BACKUP_FOLDER)
    file_size = file.content_length

    if current_size + file_size > MAX_FOLDER_SIZE:
        return jsonify({'error': 'Backup folder is full, cannot upload more files'}), 507  # 507 Insufficient Storage
    
    try:
        # Ajouter un horodatage au nom du fichier pour éviter les conflits
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(BACKUP_FOLDER, filename)
        file.save(filepath)

        # Mettre à jour la variable last_update_time
        last_update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({'success': f'File saved as {filename}'}), 200
    except Exception as e:
        return jsonify({'error': f'File not saved: {str(e)}'}), 500

@app.route('/is_alive', methods=['GET'])
def is_alive():
    return jsonify({'status': 'alive'}), 200

@app.route('/last_update', methods=['GET'])
def last_update():
    if last_update_time:
        return jsonify({'last_update': last_update_time}), 200
    else:
        return jsonify({'last_update': 'No updates yet'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)
