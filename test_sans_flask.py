import torch
from faster_whisper import WhisperModel
import requests
import os
import edge_tts
import asyncio

# Paramètres
audio_file_path = "8_miles.wav"  # Remplace par le chemin réel de ton fichier
LM_STUDIO_API_URL = "http://172.17.3.46:1234/v1/chat/completions"
model_size = "small"

# Charger Fast Whisper
whisper_model = WhisperModel(model_size, device="cuda", compute_type="int8")

def transcribe_audio(audio_path):
    """Transcrit un fichier audio en texte avec Whisper."""
    segments, _ = whisper_model.transcribe(audio_path)
    return " ".join(segment.text for segment in segments)

def send_to_llm(text):
    """Envoie le texte au modèle LM Studio et récupère la réponse."""
    response = requests.post(
        LM_STUDIO_API_URL,
        json={
            "model": "Qwen/Qwen2-0.5B-Instruct-GGUF",
            "messages": [
                {"role": "system", "content": "You're a talented rapper who has to respond to the given rap with style. You must respond with a 20-line text that follows the same flow, rhymes, and tone. Keep a provocative style with the same theme. Don't repeat the original lyrics, but find a punchline that responds intelligently, in English."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.7
        }
    )
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erreur de réponse du LLM")

async def text_to_speech(text, output_file, voice="en-US-GuyNeural"):
    """Convertit un texte en audio avec Edge-TTS."""
    tts = edge_tts.Communicate(text, voice)
    await tts.save(output_file)
    print(f"Fichier audio enregistré sous : {output_file}")

# Exécution du pipeline
txt = transcribe_audio(audio_file_path)
print("Transcription:", txt, "\n")

rap_response = send_to_llm(txt)
print("Réponse du LLM:", rap_response, "\n")

# Génération du fichier audio
output_audio = "generated_speech.wav"
asyncio.run(text_to_speech(rap_response, output_audio))