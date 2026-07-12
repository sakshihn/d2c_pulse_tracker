from django.shortcuts import render
from .models import Product

def product_list(request):
    vendor_filter = request.GET.get('vendor', '')
    
    products = Product.objects.all().order_by('vendor', 'price')
    
    if vendor_filter:
        products = products.filter(vendor=vendor_filter)
    
    vendors = Product.objects.values_list('vendor', flat=True).distinct().order_by('vendor')
    
    return render(request, 'tracking/product_list.html', {
        'products': products,
        'vendors': vendors,
        'selected_vendor': vendor_filter,
    })