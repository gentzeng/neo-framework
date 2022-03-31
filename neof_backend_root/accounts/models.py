from django.contrib.auth.models import AbstractUser
from django.db.models import PositiveSmallIntegerField


class User(AbstractUser):
    RESEARCHER = 1
    TEST_SUBJECT = 2
    EPHEMERAL_TEST_SUBJECT = 3

    ROLE_CHOICES = (
        (RESEARCHER, "Researcher"),
        (TEST_SUBJECT, "Test Subject"),
        (EPHEMERAL_TEST_SUBJECT, "Ephemeral Test Subject"),
    )

    role = PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
