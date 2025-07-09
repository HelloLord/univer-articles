import unittest

from .models import CustomUser
from .utils import KeywordExtract
from rest_framework.test import APITestCase
class TestRussianYakeKeywordsExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extractor = KeywordExtract


class TestReviewPermission(APITestCase):
    def test_reviewer(self):
        user = CustomUser.objects.create(username='test')
        self.client.force_login(user)
        response = self.client.get('/articles/review')
        self.assertEqual(response.status_code, 403)