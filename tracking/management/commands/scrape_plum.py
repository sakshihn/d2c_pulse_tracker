import time
import requests
from django.core.management.base import BaseCommand
from tracking.models import Product


class Command(BaseCommand):
    help = "Scrapes Plum Goodness products and saves them to the database"

    def handle(self, *args, **options):
        page = 1

        while True:
            url = f"https://plumgoodness.com/products.json?page={page}"
            response = requests.get(url)

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                self.stdout.write(f"Page {page} did not return valid JSON. Stopping.")
                break

            products_list = data["products"]

            if len(products_list) == 0:
                self.stdout.write(f"Page {page} came back empty. Stopping.")
                break

            for p in products_list:
                if "hide" not in p["tags"]:
                    variant = p["variants"][0]

                    Product.objects.update_or_create(
                        shopify_product_id=p["id"],
                        defaults={
                            "title": p["title"],
                            "vendor": p["vendor"],
                            "price": variant["price"],
                            "available": variant["available"],
                        }
                    )
                    self.stdout.write(f"Saved: {p['title']}")

            page = page + 1
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Done scraping Plum Goodness."))