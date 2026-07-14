import re
from django.shortcuts import render
from django.db.models import Avg, Min, Max, Count
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from .models import Product, PriceHistory

def home(request):
    return render(request, 'tracking/home.html')

@login_required
def cluster_view(request):
    products = Product.objects.exclude(category=None).order_by('category', 'vendor')

    categories = {}
    for p in products:
        categories.setdefault(p.category, []).append(p)

    # sort categories by number of products, descending
    categories = dict(sorted(categories.items(), key=lambda x: -len(x[1])))

    return render(request, 'tracking/clusters.html', {'categories': categories})

@login_required
def product_list(request):
    vendor_filter = request.GET.get('vendor', '')
    sort = request.GET.get('sort', '')
    search_query = request.GET.get('q', '')

    products = Product.objects.all()
    if vendor_filter:
        products = products.filter(vendor=vendor_filter)
    if search_query:
        products = products.filter(title__icontains=search_query)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('vendor', 'price')

    products = list(products)

    def first_letter_key(product):
        match = re.search(r'[A-Za-z]', product.title)
        return match.group().lower() if match else 'z'

    if sort == 'name_asc':
        products.sort(key=first_letter_key)
    elif sort == 'name_desc':
        products.sort(key=first_letter_key, reverse=True)

    vendors = Product.objects.values_list('vendor', flat=True).distinct().order_by('vendor')
    brand_stats = (
        Product.objects.values('vendor')
        .annotate(avg_price=Avg('price'), min_price=Min('price'), max_price=Max('price'), count=Count('id'))
        .order_by('-avg_price')
    )
    price_changes = PriceHistory.objects.raw("""
        SELECT sub.id, sub.title, sub.vendor, sub.price, sub.prev_price, 
               (sub.price - sub.prev_price) AS diff,
               sub.recorded_at
        FROM (
            SELECT
                ph.id,
                p.title,
                p.vendor,
                ph.price,
                LAG(ph.price) OVER (PARTITION BY ph.product_id ORDER BY ph.recorded_at) AS prev_price,
                ph.recorded_at
            FROM tracking_pricehistory ph
            JOIN tracking_product p ON p.id = ph.product_id
        ) sub
        WHERE sub.prev_price IS NOT NULL AND sub.price != sub.prev_price
        ORDER BY sub.recorded_at DESC
        LIMIT 10
    """)
    return render(request, 'tracking/product_list.html', {
        'products': products,
        'vendors': vendors,
        'selected_vendor': vendor_filter,
        'selected_sort': sort,
        'search_query': search_query,
        'brand_stats': brand_stats,
        'price_changes': price_changes,
    })


class CustomSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SignUpView(CreateView):
    form_class = CustomSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'