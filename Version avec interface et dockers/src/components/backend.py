import subprocess
import json
import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np
import soundfile as sf



# Extraction des caractéristique du beat

def extract_bpm(path_of_beat):
    # Chargement de l'audio
    y, sr = librosa.load(path_of_beat)

    # Estimation du tempo et des battements
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    return tempo

def temps_mesure(tempo):
    return(60*4/tempo[0])



temps_mes = temps_mesure(extract_bpm("beat.wav"))




# Détermine la mesure la plus proche à superposer lors du time stretching

def closest_measure_duration(info_list, temps_mesure):
    """
    Pour chaque entrée de info_list, calcule l'entier de durée de mesure (temps_mesure) le plus proche de la durée.
    Retourne la plus petite durée correspondante trouvée.

    Args:
        info_list (list): Liste de dictionnaires avec clé "duration".
        temps_mesure (float): Durée d'une mesure (en secondes).

    Returns:
        float: La plus petite durée correspondante (en secondes).
    """
    measure_durations = []
    for entry in info_list:
        duration = entry["duration"]
        n_measures = max(1, round(duration / temps_mesure))
        closest_duration = n_measures * temps_mesure
        measure_durations.append(closest_duration)
    return max(measure_durations)




# Fonction qui superpose la sortie et le beat

def mix_audios_min_duration(audio1_path, audio2_path, output_path):
    """
    Superpose deux fichiers audio jusqu'à la durée minimale entre les deux.
    
    Args:
        audio1_path (str): Chemin vers le 1er fichier audio.
        audio2_path (str): Chemin vers le 2e fichier audio.
        output_path (str): Chemin de sortie pour l'audio combiné.
    """
    # Charger les deux fichiers audio
    audio1 = AudioSegment.from_file(audio1_path)
    audio2 = AudioSegment.from_file(audio2_path)

    # Déterminer la durée minimale
    min_duration = min(len(audio1), len(audio2))

    # Tronquer les deux fichiers à cette durée
    audio1 = audio1[:min_duration]
    audio2 = audio2[:min_duration]

    audio1 = audio1 + 12
    audio2 = audio2 - 12
    # Superposer les deux audios
    combined = audio1.overlay(audio2)

    # Exporter
    combined.export(output_path, format="wav")




# Fonction du global stretch qui stretch les phrases sur des multiples de mesures

def global_stretch(audio_path, alignment_result, temps_mesure, temps_mes, output_path_stretch):
    """
    Étire chaque segment audio aligné pour qu'il ait la même durée minimale, puis concatène avec un silence de longueur temps_mesure.
    Exporte le résultat superposé au beat.

    Args:
        audio_path (str): Chemin du fichier audio source.
        alignment_result (list): Liste des alignements sous forme de dicts {"start", "end", "duration"}.
        temps_mesure (float): Durée d'une mesure (en secondes).
        output_path (str): Chemin du fichier de sortie.
    """


    # Trouver la durée minimale parmi les segments alignés
    min_duration = temps_mesure
    y_total = np.zeros(0)
    sr = None

    for segment in alignment_result:
        start = segment["start"]
        end = segment["end"]
        y, sr = librosa.load(audio_path, sr=None, offset=start, duration=end - start)
        # Calcul du facteur d'étirement pour obtenir la durée minimale
        stretch_factor = (end - start) / min_duration
        y_stretched = librosa.effects.time_stretch(y, rate=stretch_factor)
        # Ajouter un silence de la longueur d'une mesure
        silence = np.zeros(int(sr * temps_mes))
        y_final = np.concatenate([y_stretched, silence])
        y_total = np.concatenate([y_total, y_final])

    sf.write(output_path_stretch, y_total, sr)




# Fonction de Forced Alignement avec GENTLE

def align_audio_with_gfa(audio_file, transcript_file, beat_file, gfa_api_url):
    # Prépare les fichiers à envoyer dans la requête
    files = {
        'audio': open(audio_file, 'rb'),
        'transcript': open(transcript_file, 'r'),
        'beat': open(beat_file, 'rb')
    }

    # Envoie la requête avec curl en utilisant subprocess
    try:
        response = subprocess.run([
            'curl', 
            '-X', 'POST', 
            f'{gfa_api_url}/transcriptions?async=false',  # Mise à jour avec localhost:8765
            '-F', f'audio=@{audio_file}',
            '-F', f'transcript=@{transcript_file}',
            '-F', f'beat=@{beat_file}'
        ], capture_output=True, text=True)

        # Vérifie si la requête a réussi
        if response.returncode == 0:
            # La réponse JSON
            result_json = json.loads(response.stdout)
            return result_json
        else:
            print("Erreur lors de l'appel API :", response.stderr)
            return None
    finally:
        # Ferme les fichiers après utilisation
        files['audio'].close()
        files['transcript'].close()
        files['beat'].close()



# Forced alignement sur l'audio sorti du text to speech

#audio_file = "rap_sin_beat.wav"
#transcript_file = "transcript.txt"
#beat_file = "beat.wav"
#gfa_api_url = "http://localhost:8765"  # Mise à jour avec le bon port

#alignment_result = align_audio_with_gfa(audio_file, transcript_file, beat_file, gfa_api_url)





# Fonction qui détecte les derniers mots d'une ligne du transcript

def get_last_words_of_lines(text_file_path):
    """
    Prend un chemin vers un fichier texte et retourne une liste des derniers mots de chaque ligne.
    """
    last_words = []
    with open(text_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            words = [w.strip(".,!?;:()[]{}\"'") for w in line.strip().split()]
            if words:
                last_words.append(words[-1])
    return last_words

"""
derniers_mots = get_last_words_of_lines("transcript.txt")
# === Charger l'audio original ===
y, sr = librosa.load("rap_sin_beat.wav", sr=None)

gentle_data = alignment_result

# === Extraire les mots bien alignés ===
intervals = []
for word_data in gentle_data["words"]:
    if word_data.get("case") == "success":
        start = word_data["start"]
        end = word_data["end"]
        word = word_data["word"]
        intervals.append((start, end, word))

# === Rythme cible ===
pattern = [1.0, 0.5, 0.5, 1.0, 1.0]  
   # Cycle rythmique

duree_noire = temps_mes/4  # Durée d'une noire (ex: 0.5s → 120 BPM)

output = np.zeros(0)

for i, (x1, x2, mot) in enumerate(intervals):
    coeff = pattern[i % len(pattern)]
    target_duration = coeff * duree_noire
    if target_duration < len(mot)*0.05 :
        target_duration = target_duration*1.5

    segment = y[int(x1*sr):int(x2*sr)]
    original_duration = x2 - x1
    if original_duration == 0:
        continue  # Évite une division par zéro

    stretch_factor = target_duration / original_duration

    try:
        stretched = librosa.effects.time_stretch(segment, rate=1/stretch_factor)
        if mot in derniers_mots:
            pause = np.zeros(int(sr*temps_mes))
            stretched = np.concatenate([stretched, pause])
    except librosa.util.exceptions.ParameterError:
        continue  # Si le segment est trop court pour être stretché

    output = np.concatenate([output, stretched])

# === Export final ===
sf.write("output_quentin2.wav", output, sr)

audio = AudioSegment.from_file("output_quentin2.wav", format="wav")
nonsilent_ranges = detect_nonsilent(
    audio,
    min_silence_len=1095,
    silence_thresh = -40
)

# Get durations and timestamps
info = []
for start, end in nonsilent_ranges:
    if start != 0:
        start -= 1
    end += 1
    duration_sec = (end - start) / 1000.0
    info.append({"start": start / 1000.0, "end": end / 1000.0, "duration": duration_sec})


# On finit par faire un global stretch et à mixer le deux audios
global_stretch("output_quentin2.wav", info, closest_measure_duration(info,temps_mes),temps_mes, "final_rap_sin_beat.wav")
mix_audios_min_duration("final_rap_sin_beat.wav", "beat.wav", "quentin_withbeat2.wav")
"""
#######################################################################################################################################


from flask import Flask, request, send_file
from flask_cors import CORS
from faster_whisper import WhisperModel
import requests
import os
import edge_tts
import asyncio
import uuid

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
GENERATED_FOLDER = os.path.join(BASE_DIR, "generated")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

LM_STUDIO_API_URL = "http://localhost:1234/v1/chat/completions"
whisper_model = WhisperModel("small", device="cuda", compute_type="int8")

def transcribe_audio(audio_path):
    segments, _ = whisper_model.transcribe(audio_path)
    return " ".join(segment.text for segment in segments)

BATTLE_PROMPT = (
    "You are a ruthless, cocky battle rapper in the middle of a brutal rap battle. "
    "Your opponent just dropped some weak bars, and now it’s your turn to DESTROY them. "
    "Never praise them. Your tone is disrespectful, confident, funny, and full of punchlines.Be concise. Each verse must be about the same size.\n\n"
    "Example:\n"
    "Opponent: You rhyme like trash, your bars are whack, you try to rap but talent's what you lack.\n"
    "Response: You call that rap? Man, that’s baby noise,\n"
    "I’m the boss of this ring, you’re just playin’ with toys.\n"
    "My punchlines hit hard like a mic to your jaw,\n"
    "You stepped in this cypher — now reap what you saw.\n\n"
    "Now respond to the following opponent verse:"
)

def send_to_llm(text):
    payload = {
        "model": "gemma-3-1b-it-qat",
        "messages": [
            {"role": "system", "content": BATTLE_PROMPT},
            {"role": "user", "content": text}
        ],
        "temperature": 0.9
    }

    try:
        response = requests.post(LM_STUDIO_API_URL, json=payload)
        response.raise_for_status()
        resp = response.json()
        print("📥 Réponse brute :", resp)

        if "choices" in resp:
            message = resp["choices"][0].get("message", {})
            text = message.get("content", "") or resp["choices"][0].get("text", "")
            return clean_response(text)
        return "Erreur : réponse inattendue du LLM"

    except Exception as e:
        print("❌ Erreur LLM :", e)
        return "Erreur lors de la génération du texte"

def clean_response(text):
    # Nettoyage basique des erreurs fréquentes
    lines = text.strip().splitlines()
    cleaned = [line for line in lines if not any(word in line.lower() for word in ["he's great", "respect", "admire", "talent"])]
    return "\n".join(cleaned[:8])  # max 8 lignes

async def text_to_speech(text, output_file, voice="en-US-GuyNeural"):
    print(f"🔊 Génération vocale vers : {output_file}")
    tts = edge_tts.Communicate(text, voice)
    await tts.save(output_file)
    if os.path.exists(output_file):
        print("✅ Fichier audio généré avec succès.")
    else:
        print("❌ Échec de la synthèse vocale.")

@app.route("/upload", methods=["POST"])
def handle_upload():
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.wav")
    output_path = os.path.join(GENERATED_FOLDER, f"{file_id}_response.wav")
    file.save(input_path)

    try:
        print("🔍 Transcription...")
        txt = transcribe_audio(input_path)
        print("🎤 Texte transcrit :", txt)

        print("🧠 Génération du rap battle...")
        rap_response = send_to_llm(txt)
        print("📜 Texte généré :", rap_response)

        print("🗣 Synthèse vocale...")
        asyncio.run(text_to_speech(rap_response, output_path))

        if not os.path.exists(output_path):
            print("❌ Audio manquant :", output_path)
            return f"Erreur : audio non généré ({output_path})", 500
        
        #gfa_api_url = "http://localhost:8765"  # Mise à jour avec le bon port
        gfa_api_url = "http://127.0.0.1:8765"

        # 📝 Sauvegarde dans un fichier .txt
        with open("rap_response.txt", "w", encoding="utf-8") as f:
            f.write(rap_response)

        alignment_result = align_audio_with_gfa(output_path, "rap_response.txt", "beat.wav", gfa_api_url)

        print(alignment_result)

        derniers_mots = get_last_words_of_lines("rap_response.txt")
        # === Charger l'audio original ===
        y, sr = librosa.load(output_path, sr=None)

        gentle_data = alignment_result

        # === Extraire les mots bien alignés ===
        intervals = []
        for word_data in gentle_data["words"]:
            if word_data.get("case") == "success":
                start = word_data["start"]
                end = word_data["end"]
                word = word_data["word"]
                intervals.append((start, end, word))

        # === Rythme cible ===
        pattern = [1.0, 0.5, 0.5, 1.0, 1.0]  
        # Cycle rythmique

        duree_noire = temps_mes/4  # Durée d'une noire (ex: 0.5s → 120 BPM)

        output = np.zeros(0)

        for i, (x1, x2, mot) in enumerate(intervals):
            coeff = pattern[i % len(pattern)]
            target_duration = coeff * duree_noire
            if target_duration < len(mot)*0.05 :
                target_duration = target_duration*1.5

            segment = y[int(x1*sr):int(x2*sr)]
            original_duration = x2 - x1
            if original_duration == 0:
                continue  # Évite une division par zéro

            stretch_factor = target_duration / original_duration

            try:
                stretched = librosa.effects.time_stretch(segment, rate=1/stretch_factor)
                if mot in derniers_mots:
                    pause = np.zeros(int(sr*temps_mes))
                    stretched = np.concatenate([stretched, pause])
            except librosa.util.exceptions.ParameterError:
                continue  # Si le segment est trop court pour être stretché

            output = np.concatenate([output, stretched])

        # === Export final ===
        sf.write("output_quentin2.wav", output, sr)

        audio = AudioSegment.from_file("output_quentin2.wav", format="wav")
        nonsilent_ranges = detect_nonsilent(
            audio,
            min_silence_len=1095,
            silence_thresh = -40
        )

        # Get durations and timestamps
        info = []
        for start, end in nonsilent_ranges:
            if start != 0:
                start -= 250
            end += 250
            duration_sec = (end - start) / 1000.0
            info.append({"start": start / 1000.0, "end": end / 1000.0, "duration": duration_sec})


        # On finit par faire un global stretch et à mixer le deux audios
        global_stretch("output_quentin2.wav", info, closest_measure_duration(info,temps_mes),temps_mes, "final_rap_sin_beat.wav")
        mix_audios_min_duration("final_rap_sin_beat.wav", "beat.wav", "quentin_withbeat2.wav")
        

        print("✅ Envoi du fichier audio.")
        return send_file("quentin_withbeat2.wav", mimetype="audio/wav")

    except Exception as e:
        print("❌ Erreur serveur :", e)
        return f"Erreur serveur : {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

