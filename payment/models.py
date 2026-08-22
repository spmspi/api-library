from django.db import models

class Payment(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeEnum(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(choices=StatusEnum.choices, max_length=10)
    type = models.CharField(choices=TypeEnum.choices, max_length=10)
    Borrowing_id = models.ForeignKey("Borrowing", on_delete=models.CASCADE)
    session_url = models.URLField(max_length=200)
    session_id = models.CharField(max_length=200)
    money = models.DecimalField(max_digits=10, decimal_places=2)


"""    * Status: Enum: PENDING | PAID
    * Type: Enum: PAYMENT | FINE
    * Borrowing id: int
    * Session url: Url (ссылка на платежную сессию Stripe)
    * Session id: str (id платежной сессии Stripe)
    * Money to pay: decimal (в $USD) — рассчитанная общая стоимость аренды"""
