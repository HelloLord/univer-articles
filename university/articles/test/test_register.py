from django.contrib.auth import get_user_model, user_logged_in
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
CustomUser = get_user_model()


class TestRegisterCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/register'

        self.user_name = 'qwerty123'
        self.email1 = 'test1@example.com'
        self.email2 = 'test2@example.com'
        self.password = 'testpass123'

        self.user1 = {
            'username': self.user_name,
            'password': self.password,
            'email': self.email1
        }

        self.user2 = {
            'username': self.user_name,
            'password': self.password,
            'email': self.email2
        }
        self.user3 = {
            'username': 'testuser',
            'password': self.password,
            'email': 'qwer@gmail.com'
        }

    """
    Проверяем регистрацию с повторным username
    """
    def test_duplicate(self):
        response1 = self.client.post(
            self.register_url,
            data=self.user1,
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response_data1 = response1.json()
        self.assertIn('status', response_data1)
        self.assertIn('redirect_url', response1.json())
        print(f"response 1 data: {response1.json()}")




        response2 = self.client.post(
            self.register_url,
            data=self.user2,
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response2.json())
        print(f"response 2 data: {response2.json()}")




        response3 = self.client.post(
            self.register_url,
            data = self.user3,
            format='json'
        )
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)
        response_data3 = response3.json()
        self.assertIn('status', response_data3)
        self.assertIn('redirect_url', response_data3)
        print(f"response 3 data: {response3.json()}")



        users = CustomUser.objects.filter(username = self.user_name)
        self.assertEqual(users.count(), 1)
        user = CustomUser.objects.all()
        self.assertEqual(user.count(), 2)
        self.assertEqual(users.first().email, self.email1)


