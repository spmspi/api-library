from books.models import Author, Book
from rest_framework import serializers


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("title", "daily_free")


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "inventory", "daily_free")


class BookDetailSerializer(BookSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        many=True,
        slug_field="full_name",
    )

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_free")
