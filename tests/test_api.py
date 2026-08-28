from datetime import date, timedelta

from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book, Author
from django.contrib.auth import get_user_model

from books.serializers import BookSerializer, BookListSerializer
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingDetailSerializer

BOOK_URL = reverse("books:book-list")
BORROWING_URL = reverse("borrowing:borrowing-list")

def sample_book(**params):
    author, _ = Author.objects.get_or_create(
        first_name="Test",
        last_name="Author",
    )

    defaults = {
        "title": "sample Book",
        "cover": "Hard",
        "inventory": 0,
        "daily_fee": 1.3,
    }
    book = Book.objects.create(**defaults)
    book.author.add(author)
    defaults.update(params)


    return book

def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])

def sample_borrowing(**params):

    defaults = {
        "borrow_date": date.today(),
        "expected_return_date": date.today() + timedelta(days=7),
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



    def test_borrowing_unauthenticated(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_book(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOK_URL)

        book = Book.objects.order_by("id")
        serializer = BookListSerializer(book, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_search_borrowing(self):

        user2 = get_user_model().objects.create_user(
            "test22@test.com",
            "testpass",
        )

        book1 = sample_book(title="Test Book Test")
        book2 = sample_book(title="one test book")
        book3 = sample_book(title="two test book")

        bor1 = sample_borrowing(user=self.user, book=book1)
        bor2 = sample_borrowing(user=user2, book=book2)
        bor3 = sample_borrowing(user=user2, book=book3)

        res = self.client.get(
            BORROWING_URL, {"user_id": f"{self.user.id}"}
        )

        serializer1 = BorrowingSerializer(bor1)
        serializer2 = BorrowingSerializer(bor2)
        serializer3 = BorrowingSerializer(bor3)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_validation(self):
        book = sample_book(inventory=0)
        payload = {
            "borrow_date": date.today(),
            "expected_return_date": date.today() + timedelta(days=7),
            "book": book.id,
        }
        res = self.client.post(BORROWING_URL, payload, format="json")
        print("RESPONSE STATUS:", res.status_code)
        print("RESPONSE DATA:", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)





