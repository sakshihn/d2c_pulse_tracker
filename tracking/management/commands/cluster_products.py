import re
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tracking.models import Product


def clean_title(title):
    title = title.lower()
    title = re.sub(r"by bodylovin'?", '', title)
    title = re.sub(r'pack of \d+', '', title)
    title = re.sub(r'\d+\s?(ml|g|gm|pairs?)', '', title)
    title = re.sub(r'\d+%', '', title)
    title = re.sub(r'[^\w\s]', '', title)
    return title.strip()


class Command(BaseCommand):
    help = "Clusters products into groups based on title similarity using TF-IDF and KMeans"

    def handle(self, *args, **options):
        products = list(Product.objects.all())
        titles = [clean_title(p.title) for p in products]

        self.stdout.write(f"Clustering {len(titles)} products...")

        vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        tfidf_matrix = vectorizer.fit_transform(titles)

        best_k = None
        best_score = -1
        for k in [10, 15, 20, 25, 30]:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(tfidf_matrix)
            score = silhouette_score(tfidf_matrix, labels)
            self.stdout.write(f"k={k}, silhouette score={score:.4f}")
            if score > best_score:
                best_score = score
                best_k = k

        self.stdout.write(f"Best k = {best_k} (score={best_score:.4f})")

        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)

        for product, cluster_id in zip(products, cluster_labels):
            product.cluster_id = int(cluster_id)
            product.save()

        self.stdout.write(self.style.SUCCESS(f"Done. Assigned {len(products)} products into {best_k} clusters."))