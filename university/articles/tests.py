import unittest
from .utils import KeywordExtract

class TestRussianYakeKeywordsExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extractor = KeywordExtract
