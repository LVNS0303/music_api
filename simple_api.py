import os
import json
import uuid
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
from flask_cors import CORS  # <-- ADICIONADO

app = Flask(__name__, static_folder='static')
CORS(app)  # <-- ADICIONADO (Habilita o CORS para o frontend)



# Configurações de diretórios
BASE_DIR = Path(__file__).resolve().parent
# --- CORRIGIDO ---
# O diretório de áudio agora fica dentro de 'static' para consistência
AUDIO_DIR = BASE_DIR / "static" / "audio_files"
COVERS_DIR = BASE_DIR / "static" / "assets"
DATA_FILE = BASE_DIR / "music_data.json"

# Criar diretórios se não existirem
AUDIO_DIR.mkdir(exist_ok=True)
COVERS_DIR.mkdir(exist_ok=True)

# Carregar dados das músicas
def load_music_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_music_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

music_data = load_music_data()

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

# Endpoint para listar todas as músicas
@app.route('/api/music', methods=['GET'])
def get_all_music():
    return jsonify(list(music_data.values()))

# Endpoint para upload de música e capa
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'music' not in request.files:
        return jsonify({'error': 'Nenhum arquivo de música enviado'}), 400
    
    music_file = request.files['music']
    cover_file = request.files.get('cover')
    name = request.form.get('name')

    if not name:
        return jsonify({'error': 'Nome da música é obrigatório'}), 400

    if music_file.filename == '':
        return jsonify({'error': 'Nenhum arquivo de música selecionado'}), 400
    
    music_id = str(uuid.uuid4())
    
    # Salvar arquivo de música
    music_filename = secure_filename(f"{music_id}_{music_file.filename}")
    music_path = AUDIO_DIR / music_filename
    music_file.save(music_path)

    cover_path_str = ""
    if cover_file and cover_file.filename != '':
        cover_filename = secure_filename(f"{music_id}_{cover_file.filename}")
        cover_path = COVERS_DIR / cover_filename
        cover_file.save(cover_path)
        cover_path_str = f"/static/assets/{cover_filename}"

    new_music = {
        'id': music_id,
        'nome': name,
        # --- CORRIGIDO ---
        # O caminho salvo no JSON agora corresponde à rota estática
        'musica': f'/static/audio_files/{music_filename}',
        'capa': cover_path_str
    }
    
    music_data[music_id] = new_music
    save_music_data(music_data)

    return jsonify(new_music), 201

@app.route('/upload')
def upload_page():
    return send_from_directory('templates', 'upload.html')

# Endpoint para servir arquivos de áudio
# --- CORRIGIDO ---
# A rota agora corresponde ao caminho usado no 'music_data.json'
@app.route('/static/audio_files/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)