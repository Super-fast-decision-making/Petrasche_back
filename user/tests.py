from django.test import TestCase

# Create your tests here.
class TestView(TestCase):
    def test_same_num(self):
        self.assertEqual(2,2)