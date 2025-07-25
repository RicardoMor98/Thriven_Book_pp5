from django.db import models
from django.contrib.auth.models import AbstractUser

# Constants
GENRES = [
    ('action', 'Action'),
    ('comedy', 'Comedy'),
    ('romance', 'Romance'),
    ('horror', 'Horror'),
    ('sci-fi', 'Science Fiction'),
]

AGE_RATINGS = [
    ('14+', '14+'),
    ('16+', '16+'),
    ('18+', '18+'),
]

SKILL_LEVELS = [
    ('beginner', 'Beginner'),
    ('casual', 'Casual'),
    ('professional', 'Professional'),
]

PRONOUNS = [
    ('he', 'He'),
    ('she', 'She'),
    ('other', 'Other'),
]

# Create your models here.
class User(AbstractUser):
    pronoun = models.CharField(max_length=10, choices=PRONOUNS)
    date_of_birth = models.DateField()
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_author = models.BooleanField(default=False)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, null=True, blank=True)