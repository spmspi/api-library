from django.urls import path, include
from rest_framework import routers

from books.views import BooksViewSet, AuthorViewSet

router = routers.DefaultRouter()
router.register("books", BooksViewSet)
router.register("authors", AuthorViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "books"
