from .query_sets_test import register_users
from django.contrib.auth import get_user_model
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

CustomUser = get_user_model()


class TestRegisterCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/register'
        CustomUser.objects.all().delete()

        self.users = register_users

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
                    crated_users.append(f"Создан пользователь:"
                                        f"\nusername: {user_data['username']}"
                                        f"\nfirst_name: {user_data['first_name']}"
                                        f"\nlast_name: {user_data['last_name']}"
                                        f"\nlogin: {user_data['username']}"
                                        f"\nphone:{user_data['phone']}"
                                        f"\nbirth_date: {user_data['birth_date']}\n")

        print("\n" + "\n".join(error_messages) if error_messages else "нет ошибок")
        print("\n" + "\n".join(crated_users) if crated_users else "Не было создано пользователей")
        print("\n" + "\n".join(success_responses) if success_responses else "Нет успешных ответов от сервера")


