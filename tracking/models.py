from django.db import models

# Create your models here.
class Product(models.Model):
    shopify_product_id = models.BigIntegerField(unique=True)
    title = models.CharField(max_length=500)
    vendor = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    date_scraped = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title