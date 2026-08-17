from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    cover = models.CharField(
        max_length=5,
        choices=CoverChoices.choices,)
    Inventory = models.PositiveIntegerField()
    daily_free = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title
