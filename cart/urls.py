from django.urls import path
from . import views

urlpatterns = [
    path('AddCartItems/', views.CartApi.as_view()),
    path('CartItems/', views.CartApi.as_view()),
    path('DeleteCart/', views.CartApi.as_view()),
]