from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS

from pydub import AudioSegment
from gtts.lang import tts_langs

import os

# Use the dynamic port provided by Railway
port = int(os.environ.get("PORT", 5000))




app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

recognizer = sr.Recognizer()

# Define valid Google Speech Recognition languages (partial list)
valid_stt_languages = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "mr": "Marathi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ru": "Russian",
}

@app.route("/")
def home():
    return "Flask server is running!"

@app.route('/translate', methods=['POST'])
def translate_audio():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        source_language = request.form.get("source_language", "en").lower()
        target_language = request.form.get("target_language", "hi").lower()

        # Validate Source Language (Speech Recognition)
        if source_language not in valid_stt_languages:
            return jsonify({"error": f"Source language '{source_language}' not supported for STT"}), 400

        # Validate Target Language (Text-to-Speech)
        supported_tts_languages = tts_langs()
        if target_language not in supported_tts_languages:
            return jsonify({"error": f"Target language '{target_language}' not supported for TTS"}), 400

        # Save uploaded file
        file_extension = file.filename.split('.')[-1].lower()
        temp_audio_path = os.path.join(UPLOAD_FOLDER, f"input.{file_extension}")
        file.save(temp_audio_path)

        # Convert to WAV if necessary
        audio_path = os.path.join(UPLOAD_FOLDER, "input.wav")
        if file_extension != "wav":
            audio = AudioSegment.from_file(temp_audio_path)
            audio.export(audio_path, format="wav")
        else:
            audio_path = temp_audio_path

        if not os.path.exists(audio_path):
            return jsonify({"error": "Failed to save audio file"}), 500

        # Convert speech to text (STT)
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            original_text = recognizer.recognize_google(audio_data, language=source_language)

        # Translate text
        translated_text = GoogleTranslator(source=source_language, target=target_language).translate(original_text)

        # Convert translated text to speech (TTS)
        output_mp3_path = os.path.join(OUTPUT_FOLDER, "translated.mp3")
        output_wav_path = os.path.join(OUTPUT_FOLDER, "translated.wav")

        tts = gTTS(text=translated_text, lang=target_language, slow=False)
        tts.save(output_mp3_path)

        # Convert MP3 to WAV
        sound = AudioSegment.from_mp3(output_mp3_path)
        sound.export(output_wav_path, format="wav")

        return jsonify({
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_url": request.host_url + "get_translated_audio"
        })

    except Exception as e:
        return jsonify({"error": f"Error processing audio: {str(e)}"}), 500
    
@app.route('/speak', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('lang', 'en').lower()

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Validate Language for TTS
        supported_languages = tts_langs()
        if lang not in supported_languages:
            return jsonify({"error": f"Language '{lang}' not supported for TTS"}), 400

        temp_mp3_path = os.path.join(OUTPUT_FOLDER, "output.mp3")
        temp_wav_path = os.path.join(OUTPUT_FOLDER, "output.wav")

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_mp3_path)

        # Convert MP3 to WAV
        sound = AudioSegment.from_mp3(temp_mp3_path)
        sound.export(temp_wav_path, format="wav")

        return jsonify({'audio_url': request.host_url + "get_audio"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio')
def get_audio():
    try:
        audio_path = os.path.join(OUTPUT_FOLDER, "output.wav")
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404
        return send_file(audio_path, mimetype='audio/wav')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_translated_audio')
def get_translated_audio():
    try:
        audio_path = os.path.join(OUTPUT_FOLDER, "translated.wav")
        if not os.path.exists(audio_path):
            return jsonify({"error": "Translated audio file not found"}), 404
        return send_file(audio_path, mimetype='audio/wav')
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
