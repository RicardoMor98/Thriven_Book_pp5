from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.urls import reverse

# Constants
GENRES = [
    ('action', 'Action'),
    ('comedy', 'Comedy'),
    ('romance', 'Romance'),
    ('horror', 'Horror'),
    ('sci-fi', 'Science Fiction'),
    ('fantasy', 'Fantasy'),
    ('mystery', 'Mystery'),
    ('thriller', 'Thriller'),
    ('drama', 'Drama'),
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
    ('he', 'He/Him'),
    ('she', 'She/Her'),
    ('they', 'They/Them'),
    ('other', 'Other'),
]

COMMENT_IMPORTANCE = [
    (1, 'Low'),
    (2, 'Medium'),
    (3, 'High'),
    (4, 'Very High'),
]

# Create your models here.
class User(AbstractUser):
    pronoun = models.CharField(max_length=10, choices=PRONOUNS)
    date_of_birth = models.DateField()
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_author = models.BooleanField(default=False)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, null=True, blank=True)

class BookPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=GENRES)
    age_rating = models.CharField(max_length=10, choices=AGE_RATINGS)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BookPost, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BookPost, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BookPost, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)