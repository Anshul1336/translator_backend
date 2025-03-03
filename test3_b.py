import requests

url = "http://localhost:5000/speak"
data = {
    "text": "Bonjour",
    "lang": "fr"
}

response = requests.post(url, json=data)
print(response.json())  # Output: {'audio_url': 'http://localhost:5000/output.mp3'}
