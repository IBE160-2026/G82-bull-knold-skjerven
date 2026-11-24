"""
URL-er for FåreQuiz.

Det finnes ingen /admin/ og ingen rute til MEDIA_ROOT (AD-8, AD-14).
"""

from django.urls import include, path

from farequiz import views

urlpatterns = [
    path("", views.startside, name="startside"),
    path("", include("kontoer.urls")),
]
