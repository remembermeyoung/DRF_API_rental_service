from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rental.models import Bicycle, Orders

JWT = settings.SIMPLE_JWT['AUTH_HEADER_TYPES'][0]


def sample_user(username='test_user', password='test_password', email='test@test.com'):
    return get_user_model().objects.create_user(username, password, email)


def force_auth(client, username):
    user = get_user_model().objects.get(username=username)
    client.force_authenticate(user=user)


class StartRentTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Bicycle.objects.create(model='TestModel', price=100)

    def test_bicycle_list(self):

        all_list_url = reverse('bicycle_list', kwargs={'status': 'all'})
        all_list_response = self.client.get(all_list_url)
        self.assertEqual(all_list_response.status_code, status.HTTP_200_OK)

        free_list_url = reverse('bicycle_list', kwargs={'status': 'free'})
        free_list_response = self.client.get(free_list_url)
        self.assertEqual(free_list_response.status_code, status.HTTP_200_OK)

        rented_list_url = reverse('bicycle_list', kwargs={'status': 'rented'})
        rented_list_response = self.client.get(rented_list_url)
        self.assertEqual(rented_list_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unsafe_request_from_not_auth(self):

        url = reverse('bicycle_detail', kwargs={'pk': 1})
        unsafe_response = self.client.patch(url)
        self.assertEqual(unsafe_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rent_bicycle(self):

        user = sample_user()
        self.client.force_authenticate(user=user)
        self.assertEqual(Orders.objects.count(), 0)

        url = reverse('bicycle_detail', kwargs={'pk': 1})
        rent_response = self.client.patch(url)
        self.assertEqual(rent_response.status_code, status.HTTP_200_OK)

        rent_check_response = self.client.get(url)
        self.assertEqual(rent_check_response.data['status'], 'rented')
        self.assertEqual(Orders.objects.count(), 1)


class RentTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Bicycle.objects.create(model='TestModel', price=100, status='rented')
        bicycle_obj = Bicycle.objects.get(model='TestModel')
        Orders.objects.create(bicycle=bicycle_obj, user=sample_user())

        sample_user(username='test_user2', password='test_password2', email='test2@test.com')

    def test_models_str(self):
        test_bicycle = Bicycle.objects.get(id=1)
        test_order = Orders.objects.get(id=1)

        self.assertEqual(str(test_bicycle), f'{test_bicycle.model}')
        self.assertEqual(str(test_order), f'{test_order.user.username}, {test_order.bicycle.model}')

    def test_try_to_re_rent(self):
        client2 = APIClient()
        force_auth(client2, 'test_user2')

        url = reverse('bicycle_detail', kwargs={'pk': 1})
        re_rent_response = client2.patch(url)
        self.assertEqual(re_rent_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_try_to_rent_second_bicycle(self):
        force_auth(self.client, 'test_user')
        Bicycle.objects.create(model='TestModel2', price=100)

        url = reverse('bicycle_detail', kwargs={'pk': 2})
        second_rent_response = self.client.patch(url)
        self.assertEqual(second_rent_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Bicycle.objects.get(model='TestModel2').status, 'free')
        self.assertEqual(Orders.objects.count(), 1)

    def test_finish_rent(self):
        force_auth(self.client, 'test_user')

        url = reverse('bicycle_detail', kwargs={'pk': 1})

        bring_response = self.client.patch(url)
        self.assertEqual(bring_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bicycle.objects.get(model='TestModel').status, 'free')
        self.assertTrue(Orders.objects.get(id=1).rent_finish)
