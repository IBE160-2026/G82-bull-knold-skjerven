from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class BrukerManager(BaseUserManager):
    """Manager for `Bruker`. E-post lagres alltid med små bokstaver (AD-15)."""

    use_in_migrations = True

    def _lag_bruker(self, email, password, **ekstra):
        if not email:
            raise ValueError("E-post må fylles ut.")
        bruker = self.model(email=self.normalize_email(email).lower(), **ekstra)
        bruker.set_password(password)
        bruker.save(using=self._db)
        return bruker

    def create_user(self, email, password=None, **ekstra):
        ekstra.setdefault("is_staff", False)
        ekstra.setdefault("is_superuser", False)
        return self._lag_bruker(email, password, **ekstra)

    def create_superuser(self, email, password=None, **ekstra):
        ekstra.setdefault("is_staff", True)
        ekstra.setdefault("is_superuser", True)
        if ekstra["is_staff"] is not True:
            raise ValueError("En superbruker må ha is_staff=True.")
        if ekstra["is_superuser"] is not True:
            raise ValueError("En superbruker må ha is_superuser=True.")
        return self._lag_bruker(email, password, **ekstra)

    def get_by_natural_key(self, email):
        return self.get(email=email.lower())


class Bruker(AbstractUser):
    """Bruker med e-post som brukernavn (AD-15)."""

    username = None
    email = models.EmailField("e-post", unique=True)
    vilkar_godtatt = models.DateTimeField("vilkår godtatt", null=True, blank=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = BrukerManager()

    class Meta:
        verbose_name = "bruker"
        verbose_name_plural = "brukere"

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.email.lower()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
