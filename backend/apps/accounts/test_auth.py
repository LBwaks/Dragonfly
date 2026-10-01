import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_login_me_and_logout(client):
    user = get_user_model().objects.create_user(
        username="dragonfly", password="strong-test-password", email="user@example.com"
    )
    response = client.post(
        reverse("auth-login"),
        {"username": "dragonfly", "password": "strong-test-password"},
        content_type="application/json",
    )
    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json()["user"]["id"] == user.id
    response = client.get(reverse("auth-me"), HTTP_AUTHORIZATION=f"Token {token}")
    assert response.status_code == 200
    assert response.json()["username"] == "dragonfly"
    assert (
        client.post(reverse("auth-logout"), HTTP_AUTHORIZATION=f"Token {token}").status_code == 204
    )
    assert client.get(reverse("auth-me"), HTTP_AUTHORIZATION=f"Token {token}").status_code == 401


@pytest.mark.django_db
def test_invalid_login_does_not_disclose_account_state(client):
    response = client.post(
        reverse("auth-login"),
        {"username": "unknown", "password": "wrong"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "Invalid username or password" in str(response.json())
