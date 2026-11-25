from django.urls import path

from studier import views

app_name = "studier"

urlpatterns = [
    path("emner/ny/", views.ny_emne, name="ny_emne"),
    path("emner/<int:pk>/", views.emne, name="emne"),
    path("emner/<int:pk>/navn/", views.endre_navn, name="endre_navn"),
]
