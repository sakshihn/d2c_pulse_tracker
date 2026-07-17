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
from django.shortcuts import get_object_or_404
import json

def home(request):
    return render(request, 'tracking/home.html')

def logout_goodbye(request):
    return render(request, 'tracking/logout_goodbye.html')

def about_builder(request):
    return render(request, 'tracking/about.html')

@login_required
def insights_view(request):
    brand_stats = (
        Product.objects.values('vendor')
        .annotate(avg_price=Avg('price'), min_price=Min('price'), max_price=Max('price'), count=Count('id'))
        .order_by('-avg_price')
    )
    brand_labels = [b['vendor'] for b in brand_stats]
    brand_avg_prices = [float(b['avg_price']) for b in brand_stats]
    brand_min_prices = [float(b['min_price']) for b in brand_stats]
    brand_max_prices = [float(b['max_price']) for b in brand_stats]

    category_stats = (
        Product.objects.exclude(category=None)
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    category_labels = [c['category'] for c in category_stats]
    category_counts = [c['count'] for c in category_stats]

    availability_stats = Product.objects.values('available').annotate(count=Count('id'))
    availability_labels = ['In Stock' if a['available'] else 'Out of Stock' for a in availability_stats]
    availability_counts = [a['count'] for a in availability_stats]

    top_expensive = Product.objects.order_by('-price')[:10]
    top_labels = [p.title[:30] for p in top_expensive]
    top_prices = [float(p.price) for p in top_expensive]

    return render(request, 'tracking/insights.html', {
        'brand_labels': json.dumps(brand_labels),
        'brand_avg_prices': json.dumps(brand_avg_prices),
        'brand_min_prices': json.dumps(brand_min_prices),
        'brand_max_prices': json.dumps(brand_max_prices),
        'category_labels': json.dumps(category_labels),
        'category_counts': json.dumps(category_counts),
        'availability_labels': json.dumps(availability_labels),
        'availability_counts': json.dumps(availability_counts),
        'top_labels': json.dumps(top_labels),
        'top_prices': json.dumps(top_prices),
    })



@login_required
def cluster_view(request):
    category_stats = (
        Product.objects.exclude(category=None)
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    categories = []
    for stat in category_stats:
        sample_products = Product.objects.filter(category=stat['category'])[:5]
        categories.append({
            'name': stat['category'],
            'count': stat['count'],
            'sample': sample_products,
        })

    return render(request, 'tracking/clusters.html', {'categories': categories})


@login_required
def category_detail(request, category_name):
    search_query = request.GET.get('q', '')
    sort = request.GET.get('sort', '')

    products = Product.objects.filter(category=category_name)
    if search_query:
        products = products.filter(title__icontains=search_query)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('vendor', 'price')

    return render(request, 'tracking/category_detail.html', {
        'category_name': category_name,
        'products': products,
        'search_query': search_query,
        'selected_sort': sort,
    })


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


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    history = PriceHistory.objects.filter(product=product).order_by('recorded_at')

    chart_labels = [h.recorded_at.strftime('%b %d, %H:%M') for h in history]
    chart_prices = [float(h.price) for h in history]

    return render(request, 'tracking/product_detail.html', {
        'product': product,
        'chart_labels': json.dumps(chart_labels),
        'chart_prices': json.dumps(chart_prices),
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