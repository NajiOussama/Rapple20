import React, { useState, useRef } from "react";
import { ReactMic } from "react-mic";
import AudioTimer from "./AudioTimer";

export default function VoiceRecorder() {
  const [voice, setVoice] = useState(false);
  const [blobLink, setBlobLink] = useState(null);
  const [mp3ReplyURL, setMp3ReplyURL] = useState(null);
  const [step, setStep] = useState("🎤 Clique pour lancer la battle !");
  const [totalTime, setTotalTime] = useState(null);
  const startTimeRef = useRef(null);

  const startRec = () => {
    setVoice(true);
    setBlobLink(null);
    setMp3ReplyURL(null);
    setStep("🎙 Spit ton feu !");
    setTotalTime(null);
    startTimeRef.current = Date.now();
  };

  const stopRec = () => {
    setVoice(false);
    setStep("🔄 Transcription...");
  };

  const onStop = (recordedBlob) => {
    setBlobLink(recordedBlob.blobURL);
    sendToBackend(recordedBlob.blob);
  };

  const sendToBackend = async (blob) => {
    const formData = new FormData();
    formData.append("file", blob, "recording.wav");

    try {
      setStep("⚙️ Analyse de ton flow...");
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Erreur d'envoi");

      setStep("🤖 LLM prépare sa punchline...");
      const data = await response.blob();

      setStep("🎧 Synthèse de la réponse...");
      const mp3URL = URL.createObjectURL(data);
      setMp3ReplyURL(mp3URL);

      setStep("🔥 Voici sa réponse !");
      const total = ((Date.now() - startTimeRef.current) / 1000).toFixed(2);
      setTotalTime(total);
    } catch (error) {
      console.error("Erreur backend :", error);
      setStep("❌ Une erreur est survenue...");
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-12 p-6 rounded-xl shadow-2xl bg-gradient-to-br from-black to-zinc-900 text-white border border-cyan-500 font-rap tracking-wide">
      <h2 className="text-4xl font-extrabold text-cyan-400 mb-6 text-center drop-shadow-md">
        🎤 RAP BATTLE ZONE
      </h2>

      <div className="flex justify-center mb-2">
        <AudioTimer voice={voice} />
      </div>

      <p className="text-center text-xl font-semibold text-lime-400 mb-4 animate-pulse">
        {step}
      </p>

      <ReactMic
        record={voice}
        className="w-full mb-6 rounded-md overflow-hidden"
        onStop={onStop}
        strokeColor="#22d3ee"
        backgroundColor="#1e293b"
      />

      <div className="flex justify-center gap-4 mb-6">
        {voice ? (
          <button
            onClick={stopRec}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-full text-lg font-bold shadow-lg transition-transform hover:scale-105"
          >
            ⏹ Stop ton flow
          </button>
        ) : (
          <button
            onClick={startRec}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-full text-lg font-bold shadow-lg transition-transform hover:scale-105"
          >
            🎙 Lâche ton couplet
          </button>
        )}
      </div>

      {blobLink && (
        <div className="text-center mt-6 border-t border-gray-600 pt-4">
          <h3 className="text-lg font-bold text-pink-400 mb-2">🎧 Ton freestyle :</h3>
          <audio controls src={blobLink} className="w-full mb-4" />
          <a href={blobLink} download="recording.wav">
            <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-full text-lg font-bold shadow-lg transition-transform hover:scale-105">
              ⬇️ Télécharge ta performance
            </button>
          </a>
        </div>
      )}

      {mp3ReplyURL && (
        <div className="text-center mt-10 border-t border-gray-600 pt-4">
          <h3 className="text-2xl font-bold text-yellow-300 mb-2">🤖 Réponse de l'IA :</h3>
          <audio controls src={mp3ReplyURL} className="w-full mb-2" />
          <p className="text-sm text-gray-300 mt-2">
            ⏱ Temps total de la battle : <span className="font-bold text-white">{totalTime} s</span>
          </p>
        </div>
      )}
    </div>
  );
}
