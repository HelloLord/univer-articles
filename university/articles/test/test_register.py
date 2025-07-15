import random
import string
from django.contrib.auth import get_user_model
from pyexpat.errors import messages
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
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

        self.invalid_start_chars_users = [
            {'username': '@username', 'password': self.password, 'email': 'user6@example.com'},
            {'username': '.username', 'password': self.password, 'email': 'user7@example.com'},
            {'username': '1username', 'password': self.password, 'email': 'user8@example.com'},
            {'username': '123456', 'password': self.password, 'email': 'user9@example.com'},
            {'username': 'Alex224', 'password': self.password, 'email': 'user10@example.com'}
        ]

    def test_username(self):

        error_messages = []
        crated_users = []

        for user_data in self.invalid_start_chars_users:
            with self.subTest(username=user_data['username']):
                response = self.client.post(
                    self.register_url,
                    data = user_data,
                    format='json'
                )
                if response.status_code == HTTP_400_BAD_REQUEST:
                    self.assertIn('username', response.json())
                    message = f"\nОшибка: недопустимый username({user_data['username']})"
                    error_messages.append(message)
                elif response.status_code == HTTP_201_CREATED:
                    message = f"\nСоздан пользователь с username ({user_data['username']})"
                    crated_users.append(message)

        print("\n" + "\n".join(error_messages))
        print("\n" + "\n".join(crated_users))


