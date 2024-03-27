from django.urls import path
from . import views

urlpatterns = [
    path('Cart/', views.CartApi.as_view(), name='Cart'),
    path('Orders/', views.OrderApi.as_view(), name='Orders'),
]