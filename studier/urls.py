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
    path("notater/<int:pk>/ov/", views.ov_pa_feil, name="ov_pa_feil"),
    path("jobber/<int:pk>/", views.jobb, name="jobb"),
    path("jobber/<int:pk>/steg/", views.steg, name="steg"),
    path("quizer/<int:pk>/start/", views.start_quiz, name="start_quiz"),
    path("okter/<int:pk>/sporsmal/<int:nr>/", views.sporsmal, name="sporsmal"),
    path("okter/<int:pk>/lever/", views.lever, name="lever"),
    path("okter/<int:pk>/resultat/", views.resultat, name="resultat"),
]
