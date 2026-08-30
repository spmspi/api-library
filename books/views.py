from rest_framework import viewsets

from books.permissions import IsAdminOrIfAuthenticatedReadOnly, IsAdminOrReadOnly

from books.models import Book, Author
from books.serializers import (
    BookSerializer,
    AuthorSerializer,
    BookDetailSerializer,
    BookListSerializer, BookUpdateSerializer,
)


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.prefetch_related("author").all()
    permission_classes = (IsAdminOrReadOnly, )

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        if self.action == "update":
            return BookUpdateSerializer
        elif self.action == "detail":
            return BookDetailSerializer
        return BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
