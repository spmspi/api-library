from rest_framework import serializers

from Borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("borrow_date", "book_id", "user_id")

class BorrowingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing


