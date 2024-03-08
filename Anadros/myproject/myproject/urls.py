# urls.py
from django.contrib import admin
from django.urls import path
from myapp.views import run_training

urlpatterns = [
    path('run_training/', run_training, name='run_training'),
]
