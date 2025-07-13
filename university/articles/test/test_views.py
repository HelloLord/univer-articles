from audioop import reverse

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

CustomUser = get_user_model()

class TestRegisterCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/register'
        self.valid_payload = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
        }
    def test_create_user_with_valid_data(self):
        response = self.client.post(
            self.register_url,
            data=self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())

        user = CustomUser.objects.get(username = 'testuser')
        self.assertTrue(user.is_authenticated)



class BaseTestCase(APITestCase):
    TEST_CONTENT = {
        'title': 'eerticle',
        'abstract': 'test543fggdf',
        'content': 'Билет №1 Транспонировать матрицу относительно побочной диагонали с помощью цикла do while, '
                   'не использовать дополнительных матриц и массивов. В main ввести строку, '
                   'состоящую из целых чисел, разделенных произвольным количеством пробелов. '
                   'В функции преобразовать строку в массив коротких целых чисел. Вывести массив',
        'category': 3
    }
    @classmethod
    def setUpTestData(cls):
        pass

class TestReviewPermission(BaseTestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

        self.client.force_login(self.user)

    def test_reviewer_access_denied(self):
        response = self.client.get('/articles/review')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_access_ok(self):
        self.user.is_reviewer = True
        self.user.save()

        response = self.client.get('/articles/review')
        self.assertEqual(response.status_code, status.HTTP_200_OK)






# class TestArticleSubmission(BaseTestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = CustomUser.objects.create_user(username='testuser2', password='testpass2')
#         self.client.force_authenticate(user=self.user)
#
#     def test_article_submission(self):
#         data = self.TEST_CONTENT
#         response = self.client.post('/articles/create', data)
#         print(response.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)