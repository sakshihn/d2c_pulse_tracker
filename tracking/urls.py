from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('clusters/', views.cluster_view, name='cluster_view'),
]