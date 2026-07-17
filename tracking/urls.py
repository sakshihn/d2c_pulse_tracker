from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('clusters/', views.cluster_view, name='cluster_view'),
    path('clusters/<str:category_name>/', views.category_detail, name='category_detail'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('insights/', views.insights_view, name='insights_view'),
]