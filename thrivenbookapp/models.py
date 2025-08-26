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
    """Custom User model with additional fields for authors and readers"""
    pronoun = models.CharField(max_length=10, choices=PRONOUNS, default='they')
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True,
        default='profile_pics/default_avatar.png'
    )
    is_author = models.BooleanField(default=False)
    skill_level = models.CharField(
        max_length=20, 
        choices=SKILL_LEVELS, 
        null=True, 
        blank=True
    )
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        validators=[MinLengthValidator(10)]
    )
    website = models.URLField(blank=True)
    published_books = models.TextField(
        blank=True, 
        help_text="List of books you've published (separate with commas)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_pronoun_display()})"
    
    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'username': self.username})
    
    def get_age(self):
        """Calculate user's age based on date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def get_post_count(self):
        """Return the number of posts by this user"""
        return self.posts.count()
    
    def get_comment_count(self):
        """Return the number of comments by this user"""
        return self.comment_set.count()

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