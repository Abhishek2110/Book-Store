import pytest
from rest_framework.reverse import reverse

# Place Order
@pytest.mark.django_db
def test_place_order_should_return_success(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture["token"]
    book_data = {
        "id": cart_id
    }
    url = reverse("Orders")
    response = client.post(url, book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Place Order - Failed (Unauthorized)
@pytest.mark.django_db
def test_place_order_should_return_failed_unauthorized(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture["token"]
    book_data = {
        "id": cart_id
    }
    url = reverse("Orders")
    response = client.post(url, book_data, content_type="application/json")
    assert response.status_code == 401
    
# Place Order
@pytest.mark.django_db
def test_place_order_should_return_cart_id_not_provided(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture["token"]
    book_data = {
    }
    url = reverse("Orders")
    response = client.post(url, book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# Get Order Details
@pytest.mark.django_db
def test_get_order_details_should_return_success(client, place_order_fixture):
    token = place_order_fixture["token"]
    url = reverse("Orders")
    response = client.get(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Get Order Details - Failed (Unauthorized)
@pytest.mark.django_db
def test_get_order_details_should_return_failed_unauthorized(client, place_order_fixture):
    token = place_order_fixture["token"]
    url = reverse("Orders")
    response = client.get(url, content_type="application/json")
    assert response.status_code == 401
    
# Cancel Order
@pytest.mark.django_db
def test_cancel_order_should_return_success(client, place_order_fixture):
    cart_id = place_order_fixture["cart_id"]
    token = place_order_fixture["token"]
    url = reverse("Orders")
    url_with_query = f"{url}?id={cart_id}"
    response = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# Cancel Order - Failed (Unauthorized)
@pytest.mark.django_db
def test_cancel_order_should_return_failed_unauthorized(client, place_order_fixture):
    cart_id = place_order_fixture["cart_id"]
    token = place_order_fixture["token"]
    url = reverse("Orders")
    url_with_query = f"{url}?id={cart_id}"
    response = client.delete(url_with_query, content_type="application/json")
    assert response.status_code == 401
    
# Cancel Order - Failed (Cart ID not provided)
@pytest.mark.django_db
def test_cancel_order_should_return_cart_id_not_provided(client, place_order_fixture):
    cart_id = place_order_fixture["cart_id"]
    token = place_order_fixture["token"]
    url = reverse("Orders")
    response = client.delete(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400

    
