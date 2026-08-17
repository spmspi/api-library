from django.shortcuts import render
from rest_framework import viewsets

from books.models import Book, Author
from books.serializers import BookSerializer, AuthorSerializer


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

