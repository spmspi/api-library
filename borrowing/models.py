from django.db import models
from books.models import Book
from user.models import User
from .task import send_telegram_message


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def rental_cost(self):
        if not self.actual_return_date:
            return "Book not returned yet"
        if self.actual_return_date > self.expected_return_date:
            overdue_days = (self.actual_return_date - self.expected_return_date).days
            return f"Rent arrears: {overdue_days} days"
        return "The book returned on time"

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        message = (
            f"<b>New Borrowing!</b>\n"
            f"Book: {borrowing.book.title}\n"
            f"User: {borrowing.user.email}\n"
            f"Expected return date: {borrowing.expected_return_date}"
        )
        send_telegram_message.delay_on_commit(message)


