import os

from django.contrib import admin
from django.urls import path


if os.environ.get("DJANGO_SETTINGS_MODULE"):
    urlpatterns = [
        path('admin/', admin.site.urls),
    ]
