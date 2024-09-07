import requests

endpoint = "http://localhost:5000/up/sendmessage"

data = {
    "message": "meow",
    "name": ""
}

response = requests.post(endpoint, json=data)
response.raise_for_status()
print(response.text)
print(response.status_code)
print(response.headers.get('Content-Type'))