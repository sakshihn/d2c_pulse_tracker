import requests
import json

page = 1

while True:
    url = f"https://plumgoodness.com/products.json?page={page}"
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

    if page == 1:
        for p in products_list:
            if "hide" not in p["tags"]:
                print(json.dumps(p, indent=2))
                break   # just show one, then stop showing full dumps

    for p in products_list:
        if "hide" not in p["tags"]:
            print(p["title"], "-", len(p["variants"]), "variant(s)")

    page = page + 1

print("Done. Stopped at page:", page)