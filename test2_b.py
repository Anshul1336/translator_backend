import requests

url = "http://localhost:5000/recognize"
file_path = "D:\\Cooding\\translator\\audio\\translator\\test.wav"

with open(file_path, 'rb') as file:
    response = requests.post(url, files={'file': file})

print(response.json())  # Output: {'original_text': 'Hello, how are you?'}
