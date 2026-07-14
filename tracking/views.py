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
    products = Product.objects.exclude(cluster_id=None).order_by('cluster_id', 'vendor')
    
    clusters = {}
    for p in products:
        clusters.setdefault(p.cluster_id, []).append(p)
    
    return render(request, 'tracking/clusters.html', {'clusters': clusters})

@login_required
def product_list(request):
    vendor_filter = request.GET.get('vendor', '')
    products = Product.objects.all().order_by('vendor', 'price')
    if vendor_filter:
        products = products.filter(vendor=vendor_filter)
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