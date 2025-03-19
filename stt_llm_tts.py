from flask import Flask, request, jsonify, send_file
import torch
from faster_whisper import WhisperModel
import requests
import time
import os

app = Flask(__name__)

# Charger Fast Whisper
model_size = "small"
whisper_model = WhisperModel(model_size, device="cuda", compute_type="int8")

# Adresse de l'API de LM Studio
LM_STUDIO_API_URL = "http://172.17.3.46:1234/v1/chat/completions"

@app.route("/")
def home():
    return "Le serveur Flask fonctionne !"

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier audio reçu"}), 400

    audio_file = request.files["file"]
    audio_path = "temp_audio.wav"
    audio_file.save(audio_path)

    # Transcription avec Fast Whisper
    segments, _ = whisper_model.transcribe(audio_path)
    transcribed_text = " ".join(segment.text for segment in segments)

    # Envoi du texte au LLM via LM Studio
    response = requests.post(
        LM_STUDIO_API_URL,
        json={
            "model": "Qwen/Qwen2-0.5B-Instruct-GGUF",
            "messages": [
                {"role": "system", "content": "You're a talented rapper who has to respond to the given rap with style. You must respond with a 20-line text that follows the same flow, rhymes, and tone. Keep a provocative style with the same theme. Don't repeat the original lyrics, but find a punchline that responds intelligently, in English."},
                {"role": "user", "content": transcribed_text}
            ],
            "temperature": 0.7
        }
    )

    if response.status_code == 200:
        generated_text = response.json()["choices"][0]["message"]["content"]
    else:
        generated_text = "Erreur de réponse du LLM"

    return jsonify({"text": transcribed_text, "llm_response": generated_text})

@app.route("/tts", methods=["POST"])
def text_to_speech():
    data = request.get_json()
    if "text" not in data:
        return jsonify({"error": "Aucun texte fourni"}), 400

    text = data["text"]

    # Générer un fichier audio avec Edge-TTS (Exemple d'utilisation)
    tts_output = "output.wav"
    command = f'edge-tts --text "{text}" --write-media {tts_output}'
    result = os.system(command)
    print(result)

    if result != 0:
        return jsonify({"error": "Erreur lors de la génération audio"}), 500

    return send_file(tts_output, mimetype="audio/wav", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
