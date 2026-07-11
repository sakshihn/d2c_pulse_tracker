import requests
import json

page = 1

while True:
    url = f"https://dotandkey.com/products.json?page={page}"
    response = requests.get(url)
    print("Page:", page, "Status code:", response.status_code)

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Page", page, "did not return valid JSON. Raw text was:")
        print(response.text[:300])
        break

    products_list = data["products"]

    if len(products_list) == 0:
        print("Page", page, "came back empty. Stopping.")
        break

    for p in products_list:
        print(p["title"], "-", p["tags"][:5], "..." if len(p["tags"]) > 5 else "")

    page = page + 1

print("Done. Stopped at page:", page)