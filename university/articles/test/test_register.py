import random
import string
from datetime import date, timedelta

from django.contrib.auth import get_user_model
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

        today = date.today()

        self.users = [
            {
                'username': 'validUser1',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'user143@example.com',
                'password': self.password,
                'phone': '1234545343465677657657890',
                'birth_date': str(today - timedelta(days=365 * 15))
            },

        ]
    def test_username(self):

        error_messages = []
        crated_users = []
        success_responses = []

        for user_data in self.users:
            with self.subTest(username=user_data['username']):
                response = self.client.post(
                    self.register_url,
                    data = user_data,
                    format='json'
                )
                if response.status_code == HTTP_400_BAD_REQUEST:
                    error_data = response.json()
                    errors = []
                    if 'username' in error_data:
                        errors.append(f"username: {error_data['username'][0]}")
                    if 'first_name' in error_data:
                        errors.append(f"first_name: {error_data['first_name'][0]}")
                    if 'last_name' in error_data:
                        errors.append(f"last_name: {error_data['last_name'][0]}")
                    if 'email' in error_data:
                        errors.append(f"email: {error_data['email'][0]}")
                    if 'phone' in error_data:
                        errors.append(f"phone: {error_data['phone'][0]}")
                    if 'birth_date' in error_data:
                        errors.append(f"birth_date:{error_data['birth_date'][0]}")

                    message = (f"Ошибка {HTTP_400_BAD_REQUEST} '{user_data['username']}': "
                               f"{'; '.join(errors)}")
                    error_messages.append(message)


                elif response.status_code == HTTP_201_CREATED:
                    response_data = response.json()
                    try:
                        self.assertEqual(response_data['status'], 'success')
                        self.assertEqual(response_data['redirect_url'], '/articles/')
                        message = f"Создан: {status.HTTP_201_CREATED} ({user_data['username']})"
                        success_responses.append(message)

                    except (AssertionError, KeyError) as e:
                        message = (f"Создан: {status.HTTP_201_CREATED} ({user_data['username']}),"
                                   f"не соответствует ожидаемому:{str(e)}")
                        error_messages.append(message)
                    crated_users.append(f"Создан пользователь: {user_data['username']}")

        print("\n" + "\n".join(error_messages) if error_messages else "нет ошибок")
        print("\n" + "\n".join(crated_users) if crated_users else "Не было создано пользователей")
        print("\n" + "\n".join(success_responses) if success_responses else "Нет успешных ответов от сервера")


