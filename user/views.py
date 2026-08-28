from django.views.generic import CreateView
from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(CreateView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
