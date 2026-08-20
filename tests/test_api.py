from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book

BOOK_URL = reverse("books:book-list")
BORROWING_URL = reverse("borrowing:borrowing-list")

def sample_book(**params):
    author = {
        "first_name": "Test",
        "last_name": "Author",
    }

    defaults = {
        "title": "sample Book",
        "author": author,
        "cover": "Hard",
        "inventory": 5,
        "daily_free": 1.3,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)

def datail_url(book_id):
    return reverse("books:book-detail", args=[book_id])

class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)