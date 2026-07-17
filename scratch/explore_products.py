import requests

for page in range(1, 7):
    url = f"https://dotandkey.com/products.json?page={page}"
    response = requests.get(url)
    data = response.json()
    products = data.get("products", [])
    
    for p in products:
        if "Meltie" in p["title"]:
            print("Found on page:", page)
            print("Title:", p["title"])
            for v in p["variants"]:
                print("Variant available:", v["available"], "| price:", v["price"])