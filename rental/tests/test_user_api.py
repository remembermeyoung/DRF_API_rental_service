from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

JWT = settings.SIMPLE_JWT['AUTH_HEADER_TYPES'][0]


class UserTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create(username='test_user', email='test@test.com')
        user.set_password('test_password')
        user.save()

    def test_registration(self):

        reg_url = reverse('registration')

        response = self.client.post(reg_url, {'username': 'test_user1',
                                             'password': 'test_password1',
                                             'email': 'test1@test.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_and_logout(self):

        login_url = reverse('login')
        history_url = reverse('history')
        logout_url = reverse('logout')
        refresh_url = reverse('token_refresh')

        not_auth_response = self.client.get(history_url)
        self.assertEqual(not_auth_response.status_code, status.HTTP_401_UNAUTHORIZED)

        no_username_login_response = self.client.post(login_url, {'password': 'test_password'})
        self.assertEqual(no_username_login_response.status_code, status.HTTP_400_BAD_REQUEST)

        wrong_data_login_response = self.client.post(login_url, {'username': 'test_user1', 'password': 'test_password'})
        self.assertEqual(wrong_data_login_response.status_code, status.HTTP_401_UNAUTHORIZED)

        login_response = self.client.post(login_url, {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        token = {'HTTP_AUTHORIZATION': f'{JWT} {login_response.data['access']}'}

        auth_response = self.client.get(history_url, **token)
        self.assertEqual(auth_response.status_code, status.HTTP_204_NO_CONTENT)

        no_token_logout_response = self.client.post(logout_url, **token)
        self.assertEqual(no_token_logout_response.status_code, status.HTTP_400_BAD_REQUEST)

        wrong_token_logout_response = self.client.post(logout_url, data={'refresh_token': '123'}, **token)
        self.assertEqual(wrong_token_logout_response.status_code, status.HTTP_400_BAD_REQUEST)

        logout_response = self.client.post(logout_url, data={'refresh_token': f'{login_response.data['refresh']}'}, **token)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        try_refresh_response = self.client.post(refresh_url, {'refresh': f'{login_response.data['refresh']}'})
        self.assertEqual(try_refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(try_refresh_response.data['detail'], 'Token is blacklisted')
