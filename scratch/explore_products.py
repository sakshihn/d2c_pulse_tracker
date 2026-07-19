import requests

for page in range(1, 6):
    url = f"https://plumgoodness.com/products.json?page={page}"
    response = requests.get(url)
    data = response.json()
    products = data.get("products", [])
    
    for p in products:
        if "1.5%" in p["title"] and "Mandarin Pore Tightening" in p["title"]:
            print("Found on page:", page)
            print("Title:", p["title"])
            for v in p["variants"]:
                print("Variant:", v["title"], "| price:", v["price"], "| compare_at:", v["compare_at_price"], "| available:", v["available"])