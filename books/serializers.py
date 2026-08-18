from books.models import Author, Book
from rest_framework import serializers


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "authors")


class BookReviewSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    class Meta:
        model = Book
        fields = ("id", "title", "authors", "cover", "inventory", "daily_free")


