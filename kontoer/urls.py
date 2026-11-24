from django.urls import path

from kontoer import views

app_name = "kontoer"

urlpatterns = [
    path("logg-inn/", views.LoggInnView.as_view(), name="logg_inn"),
    path("registrer/", views.registrer, name="registrer"),
    path("logg-ut/", views.LoggUtView.as_view(), name="logg_ut"),
    path("vilkar/", views.VilkarView.as_view(), name="vilkar"),
    path("personvern/", views.personvern, name="personvern"),
]
