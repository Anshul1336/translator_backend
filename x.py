from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

@app.route("/")
def home():
    return "Flask server is running!"

# Initialize Speech Recognizer
recognizer = sr.Recognizer()

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    """Receives an audio file and returns the transcribed text."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        audio_path = "temp_audio.wav"
        file.save(audio_path)

        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        recognized_text = recognizer.recognize_google(audio_data)
        return jsonify({'original_text': recognized_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate_text():
    """Translates the given text from one language to another."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        from_lang = data.get('from_lang', 'auto')
        to_lang = data.get('to_lang', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        translated_text = GoogleTranslator(source=from_lang, target=to_lang).translate(text)
        return jsonify({'translated_text': translated_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/speak', methods=['POST'])
def text_to_speech():
    """Converts text to speech and returns the audio file."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('lang', 'en')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        tts = gTTS(text=text, lang=lang, slow=False)
        audio_path = "output.mp3"
        tts.save(audio_path)

        return jsonify({'audio_url': f'http://localhost:5000/{audio_path}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output.mp3')
def get_audio():
    """Serves the generated speech audio file."""
    return app.send_static_file("output.mp3")

if __name__ == '__main__':
    app.run(debug=True)
