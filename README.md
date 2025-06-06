# 🎤 Rapple20 – Battle Rap avec une IA

Rapple20 est une application web interactive de **battle rap contre une intelligence artificielle**. Enregistre ton flow, et laisse l’IA te répondre avec des punchlines générées, synchronisées sur un beat 🔥.

---

## 🚀 Fonctionnalités

- 🎙 Enregistrement vocal depuis le navigateur
- 🔊 Transcription automatique via Whisper
- 💬 Génération de réponses avec un LLM local (via LM Studio)
- 🗣 Synthèse vocale avec Microsoft Edge TTS
- 🕺 Alignement rythmique avec Gentle (forced alignment)
- ⏱ Time-stretch des mots pour matcher le tempo du beat
- 🎶 Superposition automatique voix + beat

---

## 🧱 Architecture

- **Frontend** : React JS + TailwindCSS ; utilisation de la librairie `react-mic`
- **Backend** : Flask (Python)
- **Traitement audio** : librosa, PyDub, SoundFile, faster-whisper
- **LLM** : LM Studio local
- **Alignement audio/texte** : Gentle
- **Synthèse vocale** : Edge TTS

---

## 📸 Aperçu
🎙 [START] --> 🎧 Enregistrement --> ✍️ Transcription --> 🧠 Réponse IA -->
🔈 Synthèse vocale --> 🕺 Rythme aligné sur le beat --> 🎵 Mix final

---

## 🛠 Installation

### 1. Cloner le projet
```
git clone https://github.com/ton-utilisateur/rapple20.git
cd rapple20
```

### 2. Backend (Python)
Prérequis :
Python 3.8+

CUDA recommandé (sinon adapter Whisper en CPU)

LM Studio local lancé sur localhost:1234
 - Onglet Developer
 - `Select a model to load`
 - `gemma-3-1b-it-qat`
 - Activer le serveur : `Status running` en haut à gauche

Gentle lancé sur localhost:8765
- Sur un terminal, une fois le logiciel lancé, écrire : docker run -p 8765:8765 lowerquality/gentle
Fichier "beat.wav" dans le dossier du backend, ou dans le terminal dans lequel vous êtes.

**Installation :**
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
**Lancement :**
```
python backend.py
```
L’API sera disponible sur http://localhost:5000.

## 2. Frontend (React)
Prérequis :
Node.js installé

## 3. Installation et lancement
```
npm install
npm run dev
```
Le frontend tourne par défaut sur http://localhost:5173 et communique avec le backend Flask.
