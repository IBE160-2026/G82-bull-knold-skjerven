from django.urls import path

from studier import views

app_name = "studier"

urlpatterns = [
    path("emner/ny/", views.ny_emne, name="ny_emne"),
    path("emner/<int:pk>/", views.emne, name="emne"),
    path("emner/<int:pk>/navn/", views.endre_navn, name="endre_navn"),
    path("emner/<int:pk>/slett/", views.slett_emne, name="slett_emne"),
    path("emner/<int:pk>/last-opp/", views.last_opp, name="last_opp"),
    path("notater/<int:pk>/", views.notat, name="notat"),
]
