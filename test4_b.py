import requests

url = "http://localhost:5000/output.mp3"
response = requests.get(url)

# Save file
with open("downloaded_audio.mp3", "wb") as file:
    file.write(response.content)

print("Audio downloaded successfully!")
