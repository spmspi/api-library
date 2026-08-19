from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets

from books.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingDetailSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user").all()
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            book = serializer.validated_data["book"]
            book.inventory -= 1
            book.save()
            serializer.save(user=self.request.user)
