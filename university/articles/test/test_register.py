from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
CustomUser = get_user_model()


class TestRegisterCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/register'
        self.user_name = 'User02'
        self.valid_data = {
            'username': self.user_name,
            'password': 'testpass123',
            'email': 'test@example.com',
        }
    def test_create_user_with_valid_data(self):
        response = self.client.post(
            self.register_url,
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(CustomUser.objects.filter(username=self.user_name).exists())

        user = CustomUser.objects.get(username = self.user_name)
        self.assertTrue(user.is_authenticated)