from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.BookApi.as_view(), name='books'),
]