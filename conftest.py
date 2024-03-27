import pytest
from rest_framework.reverse import reverse

@pytest.fixture
@pytest.mark.django_db
def login_fixture(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com",
        "is_superuser" : True
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    login_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    return response.data['token']

@pytest.fixture
@pytest.mark.django_db
def create_book_fixture(client, login_fixture):
    book_data = {
        "title": "Interstellar",
        "author": "Abhishek",
        "price": 20,
        "quantity": 15
    }
    url = reverse("books")
    response = client.post(url, book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {login_fixture}")
    return {'token': login_fixture, 'book_id': response.data["data"]["id"]}
    
@pytest.fixture
@pytest.mark.django_db
def create_cart_items_fixture(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    token = create_book_fixture['token']
    cart_data = {
        "book": book_id,
        "quantity": 2
    }
    url = reverse("Cart")
    response = client.post(url, cart_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    return {'token': token, 'cart_id': response.data["data"]["id"]}

@pytest.fixture
@pytest.mark.django_db
def place_order_fixture(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture['token']
    cart_data = {
        "id": cart_id
    }
    url = reverse("Orders")
    response = client.post(url, cart_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    return {'token': token, 'cart_id': cart_id}