import requests

response = requests.get("https://plumgoodness.com/products.json")
data = response.json()

print(type(data))
print(data.keys())