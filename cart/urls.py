from django.urls import path
from . import views

urlpatterns = [
    path('Cart/', views.CartApi.as_view()),
    path('Orders/', views.OrderApi.as_view()),
]