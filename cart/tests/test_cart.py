import pytest
from rest_framework.reverse import reverse

# Create Cart Items
@pytest.mark.django_db
def test_create_cart_items_should_return_success(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    token = create_book_fixture["token"]
    book_data = {
        "book": book_id,
        "quantity": 2
    }
    url = reverse("Cart")
    response = client.post(url, book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 201
    
# Create Cart Items - Failed (Unauthorized)
@pytest.mark.django_db
def test_create_cart_items_should_return_failed_unauthorized(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    token = create_book_fixture["token"]
    book_data = {
        "book": book_id
    }
    url = reverse("Cart")
    response = client.post(url, book_data, content_type="application/json")
    assert response.status_code == 401
    
# Create Cart Items - Failed (Book ID not provided)
@pytest.mark.django_db
def test_create_cart_items_should_return_failed_book_id_not_provided(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    token = create_book_fixture["token"]
    book_data = {
        "quantity": 2
    }
    url = reverse("Cart")
    response = client.post(url, book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Get Cart
@pytest.mark.django_db
def test_get_books_should_return_success(client, create_cart_items_fixture):
    token = create_cart_items_fixture["token"]
    url = reverse("Cart")
    response = client.get(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200

# Get Cart - Failed (Unauthorized)
@pytest.mark.django_db
def test_get_books_should_return_failed_unauthorized(client, create_cart_items_fixture):
    token = create_cart_items_fixture["token"]
    url = reverse("Cart")
    response = client.get(url, content_type="application/json")
    assert response.status_code == 401
    
# Delete Book
@pytest.mark.django_db
def test_delete_cart_should_return_success(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture["token"]
    url = reverse("Cart")
    url_with_query = f"{url}?id={cart_id}"
    response = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Delete Book - Failed (Unauthorized)
@pytest.mark.django_db
def test_delete_cart_should_return_failed_unauthorized(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture["token"]
    url = reverse("Cart")
    url_with_query = f"{url}?id={cart_id}"
    response = client.delete(url_with_query, content_type="application/json")
    assert response.status_code == 401
    
# Delete Book - Failed (Cart ID not provided)
@pytest.mark.django_db
def test_delete_cart_should_return_failed_cart_id_not_provided(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture["token"]
    url = reverse("Cart")
    response = client.delete(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400 