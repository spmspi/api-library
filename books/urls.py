from django.urls import path, include
from rest_framework import routers

from books.views import BooksViewSet, AuthorViewSet

router = routers.DefaultRouter()
router.register("Books", BooksViewSet)
router.register("Authors", AuthorViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "books"
