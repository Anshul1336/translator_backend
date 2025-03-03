


# code of pre-fixed input




from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
from pydub import AudioSegment

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

@app.route("/")
def home():
    return "Flask server is running!"

# Initialize Speech Recognizer
recognizer = sr.Recognizer()

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    """Receives an audio file, ensures it's WAV, and returns the transcribed text."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        filename = file.filename

        if not filename.endswith('.wav'):
            return jsonify({'error': 'Only WAV files are supported'}), 400

        audio_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(audio_path)  # Save the WAV file

        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        recognized_text = recognizer.recognize_google(audio_data)
        return jsonify({'original_text': recognized_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    source_language = request.form.get("source_language", "en")
    target_language = request.form.get("target_language", "hi")

    # Save audio file temporarily
    filepath = os.path.join(UPLOAD_FOLDER, "input.wav")
    file.save(filepath)

    # Placeholder for actual processing
    original_text = "Hello, this is a test"  # Replace with Speech-to-Text logic
    translated_text = GoogleTranslator(source=source_language, target=target_language).translate(original_text)


    # Simulate generating an audio file
    translated_audio_url = "translated.mp3"  # Replace with actual TTS logic

    return jsonify({
        "original_text": original_text,
        "translated_text": translated_text,
        "audio_url": translated_audio_url
    })

@app.route('/speak', methods=['POST'])
def text_to_speech():
    """Converts text to speech and returns a WAV audio file."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('lang', 'en')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        temp_mp3_path = os.path.join(OUTPUT_FOLDER, "output.mp3")
        temp_wav_path = os.path.join(OUTPUT_FOLDER, "output.wav")

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_mp3_path)

        # Convert MP3 to WAV
        sound = AudioSegment.from_mp3(temp_mp3_path)
        sound.export(temp_wav_path, format="wav")

        return jsonify({'audio_url': f'http://localhost:5000/get_audio'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/translated.mp3')
def serve_audio():
    return send_from_directory(os.getcwd(), "translated.mp3", mimetype="audio/mpeg")

@app.route('/get_audio')
def get_audio():
    """Serves the generated WAV speech audio file."""
    audio_path = os.path.join(OUTPUT_FOLDER, "output.wav")
    return send_file(audio_path, as_attachment=True, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
