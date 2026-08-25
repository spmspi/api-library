import os
from datetime import date

import requests
from celery import shared_task

from books.models import Book
from borrowing.models import Borrowing
from user.models import User


@shared_task
def check_borrowing_in_return_task():
    not_return = Borrowing.objects.filter(
        expected_return_date__lt=date.today(),
        actual_return_date__isnull=True,).all()
    if not not_return:
        send_notification_task("No borrowings overdue today!")
        return
    for borrowing in not_return:
        days_past_due = (date.today() - borrowing.expected_return_date).days
        message = (f"⚠️Overdue lease⚠️\n"
                   f"Book title: {borrowing.book.title}\n"
                   f"Days past due: {days_past_due}\n"
                   f"User: {borrowing.user.email}\n")
        send_notification_task.delay(message)



def send_telegram_message(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    requests.post(url, json=payload)


@shared_task
def send_notification_task(message: str):
    send_telegram_message(message)