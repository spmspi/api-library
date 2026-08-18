from django.shortcuts import render
from rest_framework import viewsets

from books.models import Book, Author
from books.serializers import BookSerializer, AuthorSerializer, BookReviewSerializer


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.prefetch_related("author").all()
    serializer_class = BookSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BookSerializer
        elif self.action == "retrieve":
            return BookReviewSerializer
        return BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

