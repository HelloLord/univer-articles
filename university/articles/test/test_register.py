import random
import string

from django.contrib.auth import get_user_model, user_logged_in
from django.template.defaultfilters import length
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
CustomUser = get_user_model()


class TestRegisterCase(APITestCase):
    @staticmethod
    def generate_username(length=10):
        chars = string.ascii_letters + string.digits + '@.+-_'
        return ''.join(random.choice(chars) for _ in range(length))

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/register'
        self.password = 'testpass123'

        CustomUser.objects.all().delete()

        self.user1 = {
            'username': 'testuser1',
            'password': self.password,
            'email': 'test1@example.com'
        }

        self.user2 = {
            'username': 'testuser1',  # Дубликат username
            'password': self.password,
            'email': 'test2@example.com'
        }

        self.user3 = {
            'username': 'testuser3',
            'password': self.password,
            'email': 'test1@example.com'  # Дубликат email из user1
        }

        self.user4 = {
            'username': 'A' * 3,  # Слишком короткий
            'password': self.password,
            'email': 'test4@example.com'
        }

        self.user5 = {
            'username': 'A' * 32,  # Слишком длинный
            'password': self.password,
            'email': 'test5@example.com'
        }

    def test_successful_reg(self):
        """
        Запрос создания пользователя.
        """

        response = self.client.post(
            self.register_url,
            data=self.user1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data1 = response.json()
        self.assertIn('status', response_data1)
        self.assertIn('redirect_url', response.json())
        print(f"\nresponse 1 data: {response.json()}, \nstatus: {status.HTTP_201_CREATED}")
        print(f"CREATED USER: {self.user1}")


    def test_duplicate_username(self):
        """
        Запрос с повторным USERNAME
        """
        self.client.post(self.register_url, data = self.user1, format='json')

        response = self.client.post(
            self.register_url,
            data=self.user2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.json())
        print(f"\nresponse 2 data: {response.json()}, \nstatus: {response.status_code}")
        print(f"EXISTING USERNAME: {self.user2['username']}")


    def test_duplicate_email(self):
        """
        Запрос с повторным EMAIL
        """
        self.client.post(self.register_url, data=self.user1, format='json')

        response = self.client.post(
            self.register_url,
            data=self.user3,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        print(f"\nresponse 3 data: {response.json()}, \nstatus: {response.status_code}")
        print(f"EXISTING EMAIL: {self.user3['email']}")


    def test_short_username(self):
        """
        запрос с коротким USERNAME < 4
        """
        response = self.client.post(
            self.register_url,
            data = self.user4,
            format = 'json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(f"\nresponse 4 data: {response.json()}, \nstatus: {response.status_code}")
        print(f"Username not in required length '{self.user4['username']}' ")


    def test_long_username(self):
        """
        запрос с длинным USERNAME > 30
        """
        response = self.client.post(
            self.register_url,
            data = self.user5,
            format= 'json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(f"\nresponse 5 data: {response.json()}, \nstatus: {response.status_code}")
        print(f"Username not in required length '{self.user5['username']}'")

