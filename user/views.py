from django.shortcuts import render
from django.views.generic import CreateView
from rest_framework import generics


class CreateUserView(CreateView):
    serializer_class = UserCreationSerializer

class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
