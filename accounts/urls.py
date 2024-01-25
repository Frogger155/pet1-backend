from django.urls import path
from .views import *

urlpatterns = [
    path('create/', UserCreate.as_view()),
    path('delete/<int:pk>/', UserDelete.as_view()),
]