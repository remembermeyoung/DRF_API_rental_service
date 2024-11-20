import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rental.models import Bicycle, Orders

JWT = settings.SIMPLE_JWT['AUTH_HEADER_TYPES'][0]

User = get_user_model()

@pytest.fixture()
def create_tokens(client):
    User.objects.create_user(username='test_user1', email='test1@test.com', password='test_password1')
    User.objects.create_user(username='test_user2', email='test2@test.com', password='test_password2')

    token_url = reverse('token_get')
    token_response1 = client.post(token_url, {'username': 'test_user1', 'password': 'test_password1'})
    token_response2 = client.post(token_url, {'username': 'test_user2', 'password': 'test_password2'})
    token1 = {'HTTP_AUTHORIZATION': f'{JWT} {token_response1.data['access']}'}
    token2 = {'HTTP_AUTHORIZATION': f'{JWT} {token_response2.data['access']}'}
    return token1, token2

@pytest.fixture()
def create_bicycles():
    bicycles = [Bicycle(model=f'bicycle{i}', price=100) for i in range(1,4)]
    Bicycle.objects.bulk_create(bicycles)

@pytest.mark.django_db
@pytest.mark.usefixtures('create_bicycles')
class TestRent:

    def test_start_rent_success(self, create_tokens, client):
        token1, token2 = create_tokens
        rent_url = reverse('bicycle-start-rent', kwargs = {'pk': 1})

        not_auth_rent_response = client.patch(rent_url)
        assert not_auth_rent_response.status_code == status.HTTP_401_UNAUTHORIZED

        auth_rent_response = client.patch(rent_url, **token1)
        assert auth_rent_response.status_code == status.HTTP_200_OK
        assert Orders.objects.filter(id=1).exists() == True

    def test_finish_rent_success(self, create_tokens, client):
        token1, token2 = create_tokens
        rent_url = reverse('bicycle-start-rent', kwargs={'pk': 1})
        rent_finish_url = reverse('bicycle-finish-rent', kwargs={'pk': 1})

        auth_rent_response = client.patch(rent_url, **token1)
        auth_rent_finish_response = client.patch(rent_finish_url, **token1)
        assert auth_rent_finish_response.status_code == status.HTTP_200_OK
        assert Orders.objects.filter(id=1, rent_finish=None).exists() == False

    def test_start_or_finish_rent_notfound(self, create_tokens, client):
        token1, token2 = create_tokens
        rent_url = reverse('bicycle-start-rent', kwargs={'pk': 10})
        finish_rent_url = reverse('bicycle-finish-rent', kwargs={'pk': 10})

        auth_rent_response = client.patch(rent_url, **token1)
        auth_finish_rent_response = client.patch(rent_url, **token1)
        assert auth_rent_response.status_code == status.HTTP_404_NOT_FOUND
        assert auth_finish_rent_response.status_code == status.HTTP_404_NOT_FOUND

    def test_rent_two_bicycles(self, create_tokens, client):
        token1, token2 = create_tokens
        rent_url = reverse('bicycle-start-rent', kwargs={'pk': 1})
        rent_url2 = reverse('bicycle-start-rent', kwargs={'pk': 2})

        auth_rent_response = client.patch(rent_url, **token1)
        second_auth_rent_response = client.patch(rent_url2, **token1)
        assert auth_rent_response.status_code == status.HTTP_200_OK
        assert second_auth_rent_response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rent_rented_bicycle(self, create_tokens, client):
        token1, token2 = create_tokens
        rent_url = reverse('bicycle-start-rent', kwargs={'pk': 1})

        auth_rent_response = client.patch(rent_url, **token1)
        auth_rent_response2 = client.patch(rent_url, **token2)
        assert auth_rent_response.status_code == status.HTTP_200_OK
        assert auth_rent_response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_finish_rent_from_another_user(self, create_tokens, client):
        token1, token2 = create_tokens
        rent_url = reverse('bicycle-start-rent', kwargs={'pk': 1})
        auth_rent_response = client.patch(rent_url, **token1)
        assert auth_rent_response.status_code == status.HTTP_200_OK

        finish_rent_url = reverse('bicycle-finish-rent', kwargs={'pk': 1})
        auth_finish_rent_response = client.patch(finish_rent_url, **token2)
        assert auth_finish_rent_response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_history(self, create_tokens, client):
        token1, token2 = create_tokens
        history_url = reverse('orders-history')
        empty_history_response = client.get(history_url, **token1)
        assert 'empty' in empty_history_response.data

        rent_url = reverse('bicycle-start-rent', kwargs={'pk': 1})
        auth_rent_response = client.patch(rent_url, **token1)
        assert 'empty' in empty_history_response.data

    def test_history(self, create_tokens, client):
        token1, token2 = create_tokens

        rent_url = reverse('bicycle-start-rent', kwargs={'pk': 1})
        finish_rent_url = reverse('bicycle-finish-rent', kwargs={'pk': 1})
        auth_rent_response = client.patch(rent_url, **token1)
        auth_finish_rent_response = client.patch(finish_rent_url, **token1)

        history_url = reverse('orders-history')
        empty_history_response = client.get(history_url, **token1)
        assert 'empty' not in empty_history_response.data

