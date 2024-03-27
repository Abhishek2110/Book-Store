from django.urls import path
from . import views

urlpatterns = [
    path('Cart/', views.CartApi.as_view()),
]