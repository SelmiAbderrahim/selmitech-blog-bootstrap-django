from django.urls import path
from .views import *
from django.conf import settings

urlpatterns = [
    path("", home, name="home"),
    path('logout/', logout, name='logout'),
    path('search/', search, name='search'),
    path("post/<slug>", detail, name="detail"),
    path("category/<slug>", category, name="category"),
]