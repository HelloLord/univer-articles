import random
import string
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


        self.users = [
            {'username': 'admin', 'password': self.password, 'email': 'user0@example.com'},
            {'username': 'root', 'password': self.password, 'email': 'user1@example.com'},
            {'username': 'superuser', 'password': self.password, 'email': 'user2@example.com'},
            {'username': '@test', 'password': self.password, 'email': 'user3@example.com'},
            {'username': '.test', 'password': self.password, 'email': 'user4@example.com'},
            {'username': '+test', 'password': self.password, 'email': 'user5@example.com'},
            {'username': '-test', 'password': self.password, 'email': 'user6@example.com'},
            {'username': '_test', 'password': self.password, 'email': 'user7@example.com'},
            {'username': '1test', 'password': self.password, 'email': 'user8@example.com'},
            {'username': '1234', 'password': self.password, 'email': 'user9@example.com'},
            {'username': 'abc', 'password': self.password, 'email': 'user10@example.com'},
            {'username': 'a' * 31, 'password': self.password, 'email': 'user11@example.com'},
            {'username': 'test!user', 'password': self.password, 'email': 'user12@example.com'},
            {'username': 'test user', 'password': self.password, 'email': 'user13@example.com'},
            {'username': 'test#user', 'password': self.password, 'email': 'user14@example.com'},
            {'username': 'existing', 'password': self.password, 'email': 'user15@example.com'},
            {'username': 'validUser', 'password': self.password, 'email': 'user16@example.com'},
            {'username': 'user.name', 'password': self.password, 'email': 'user17@example.com'},
            {'username': 'user+test', 'password': self.password, 'email': 'user18@example.com'},
            {'username': 'user-test', 'password': self.password, 'email': 'user19@example.com'},
            {'username': 'user_name', 'password': self.password, 'email': 'user20@example.com'},
            {'username': 'User123', 'password': self.password, 'email': 'user21@example.com'},
            {'username': 'Jhon02', 'first_name': '123', 'password':self.password, 'email': 'user1224@gmail.com'}
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
        print("\n" + "\n".join(crated_users) if crated_users else "не было создано пользователей")
        print("\n" + "\n".join(success_responses) if success_responses else "Нет успешных ответов от сервера")


