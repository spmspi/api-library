from rest_framework import serializers
from django.utils import timezone
from books.models import Book
from books.serializers import BookSerializer
from borrowing.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book")


class BorrowingDetailSerializer(BorrowingSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Borrowing
        fields = (
            "book",
            "expected_return_date",
        )

    def validate_book(self, value):
        if value.inventory <= 0:
            raise serializers.ValidationError("The book is out of stock.")
        return value

    def validate_expected_return_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "You must specify a date later than today."
            )
        return value
