import requests

# Define the API endpoint
url = "http://127.0.0.1:5000/translate"

# Define the data to send
data = {
    "text": "How are you",
    "to_lang": "es"
}

# Send a POST request
response = requests.post(url, json=data)

# Print the response
print("Response:", response.json())
