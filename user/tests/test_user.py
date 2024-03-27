import pytest
from rest_framework.reverse import reverse

# Valid Registration
@pytest.mark.django_db
def test_user_registration_should_return_success(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201

# Invalid Password
@pytest.mark.django_db
def test_user_registration_should_return_failed_password(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 400
    
# Invalid Email
@pytest.mark.django_db
def test_user_registration_should_return_failed_email(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpalgmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 400
    
# Duplicate Username
@pytest.mark.django_db
def test_user_registration_should_return_failed_duplicate(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 400   
    
# Valid Login
@pytest.mark.django_db
def test_user_login_should_return_success(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201
    login_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234"
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    assert response.status_code == 200
 
# Invalid Login Credentials
@pytest.mark.django_db
def test_user_login_should_return_failed_incorrect_username(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201
    login_data = {
        "username" : "anirudh",
        "password" : "Anirudh1234"
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    assert response.status_code == 400
    
# Reset Password
@pytest.mark.django_db
def test_reset_password_should_return_success(client):
    # Register a user
    register_data = {
        "username": "Anirudh",
        "password": "Anirudh@1234",
        "email": "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201
    reset_password_data = {
        "email": "bhshkrajpal@gmail.com"
    }
    url = reverse("reset")
    response = client.post(url, reset_password_data, content_type="application/json")
    assert response.status_code == 200
    token = response.data.get("token")
    print(response.data)
    new_password_data = {
        "new_password": "Rajpal@1234"
    }
    url = reverse("change") + f"?token={token}"
    response = client.post(url, new_password_data, content_type="application/json")
    assert response.status_code == 200

# Reset Passwored - Failed
@pytest.mark.django_db
def test_reset_password_should_return_failed(client):
    register_data = {
        "username" : "Anirudh",
        "password" : "Anirudh@1234",
        "email" : "bhshkrajpal@gmail.com"
    }
    url = reverse("register")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201
    reset_password_data = {
        "email" : "bhshkrajpal@gmail.comm"
    }
    url = reverse("reset")
    response = client.post(url, reset_password_data, content_type="application/json")
    assert response.status_code == 404
    new_password_data = {
        "password" : "Rajpal@1234"
    }
    url = reverse("change")
    response = client.post(url, new_password_data, content_type="application/json")
    assert response.status_code == 400