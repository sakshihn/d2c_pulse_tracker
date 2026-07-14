import re
from django.core.management.base import BaseCommand
from tracking.models import Product

CATEGORY_RULES = [
    ('Sunscreen', [r'sunscreen', r'spf\s?\d']),
    ('Body Wash', [r'body wash', r'shower gel']),
    ('Shampoo', [r'shampoo']),
    ('Conditioner', [r'conditioner']),
    ('Hair Serum', [r'hair serum', r'hair growth']),
    ('Hair Mask', [r'hair mask']),
    ('Face Wash', [r'face wash', r'cleanser', r'cleansing']),
    ('Face Serum', [r'face serum', r'\bserum\b']),
    ('Moisturizer', [r'moisturizer', r'moisturiser', r'cr[eè]me', r'\bcream\b', r'\blotion\b', r'\bgel\b']),
    ('Toner', [r'toner']),
    ('Soap', [r'\bsoap\b']),
    ('Face Mask', [r'face mask', r'clay mask']),
    ('Eye Care', [r'eye cream', r'eye patch', r'under.?eye', r'under eye']),
    ('Lip Care', [r'lip balm', r'lip treatment', r'lip mask']),
    ('Body Lotion', [r'body lotion', r'body butter']),
    ('Body Mist', [r'body mist', r'perfume', r'eau de parfum', r'deodorant', r'roll.?on']),
    ('Body Scrub', [r'body scrub', r'exfoliat']),
    ('Face Scrub', [r'face scrub']),
    ('Gift Set', [r'gift set', r'gift kit', r'discovery set']),
    ('Skincare Kit', [r'\bkit\b', r'routine', r'regime', r'combo', r'duo', r'trio']),
    ('Nail Care', [r'nail polish', r'strengthener']),
    ('Makeup', [r'kajal', r'kohl', r'eyeshadow', r'highlighter']),
]


def categorize(title):
    title_lower = title.lower()
    for category, patterns in CATEGORY_RULES:
        for pattern in patterns:
            if re.search(pattern, title_lower):
                return category
    return 'Other'


class Command(BaseCommand):
    help = "Categorizes products into readable categories based on title keywords"

    def handle(self, *args, **options):
        products = Product.objects.all()
        category_counts = {}

        for p in products:
            category = categorize(p.title)
            p.category = category
            p.save()
            category_counts[category] = category_counts.get(category, 0) + 1

        self.stdout.write(self.style.SUCCESS(f"Categorized {products.count()} products."))
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            self.stdout.write(f"  {cat}: {count}")