from flask import Flask, request, jsonify, send_from_directory
import os
import threading
import subprocess
from TTS.api import TTS

app = Flask(__name__)

# Assurez-vous que le dossier 'static' existe
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

# Dictionnaire des modèles TTS compatibles
TTS_MODELS = {
    "tacotron2": "tts_models/en/ljspeech/tacotron2-DDC",
    "fast_pitch": "tts_models/en/vctk/fast_pitch"
}

def generate_tts(model_name, text, speaker=None, speed=1.0):
    """Génère un fichier audio à partir d'un texte en utilisant le modèle TTS choisi."""
    output_file = os.path.join(STATIC_DIR, f"output_{model_name}.wav")

    if model_name == "edge-tts":
        command = f'edge-tts --text "{text}" --voice "en-US-GuyNeural" --write-media {output_file}'
        subprocess.run(command, shell=True)

    else:
        # Charger le modèle correspondant
        tts_model = TTS(model_name=TTS_MODELS[model_name], progress_bar=False).to("cpu")

        if model_name == "fast_pitch":
            if not speaker:
                raise ValueError("Le modèle FastPitch nécessite un speaker !")
            tts_model.tts_to_file(text=text, file_path=output_file, speaker=speaker, speed=speed)
        else:
            tts_model.tts_to_file(text=text, file_path=output_file, speed=speed)

    return output_file

@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    texte_genere = data.get('text', 'Hello world')
    model_name = data.get('model', 'edge-tts')  # Modèle par défaut = Edge-TTS
    speaker = data.get('speaker', None)  # Speaker optionnel
    speed = data.get('speed', 1.0)  # Vitesse optionnelle

    try:
        output_file = generate_tts(model_name, texte_genere, speaker, speed)
        return jsonify({"audio_url": f"http://127.0.0.1:5001/static/{os.path.basename(output_file)}"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Route pour servir les fichiers audio
@app.route('/static/<path:filename>')
def serve_file(filename):
    return send_from_directory(STATIC_DIR, filename)

# Démarrer Flask sur le port 5001
def run_flask():
    app.run(port=5001, debug=False, use_reloader=False, threaded=True)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()
