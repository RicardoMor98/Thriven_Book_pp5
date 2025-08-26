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
    """Model for book ideas/posts created by authors"""
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts',
        limit_choices_to={'is_author': True}
    )
    title = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(5)]
    )
    genre = models.CharField(max_length=20, choices=GENRES)
    age_rating = models.CharField(max_length=10, choices=AGE_RATINGS)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS)
    image = models.ImageField(
        upload_to='book_images/', 
        null=True, 
        blank=True,
        default='book_images/default_book.jpg'
    )
    description = models.TextField(
        validators=[MinLengthValidator(50), MaxLengthValidator(2000)]
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this post is active and visible to users."
    )
    comment_section_closed = models.BooleanField(
        default=False,
        help_text="If checked, users cannot add new comments to this post."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['genre']),
            models.Index(fields=['age_rating']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
    
    def get_like_count(self):
        """Return the number of likes for this post"""
        return self.likes.count()
    
    def get_comment_count(self):
        """Return the number of comments for this post"""
        return self.comments.count()
    
    def get_pinned_comments(self):
        """Return pinned comments for this post"""
        return self.comments.filter(is_pinned=True).order_by('-importance_level', 'created_at')
    
    def can_user_comment(self, user):
        """Check if a user can comment on this post"""
        return self.is_active and not self.comment_section_closed and user.is_authenticated


class Comment(models.Model):
    """Model for comments on book posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        BookPost, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    text = models.TextField(
        validators=[MinLengthValidator(10), MaxLengthValidator(1000)]
    )
    is_pinned = models.BooleanField(default=False)
    importance_level = models.IntegerField(
        choices=COMMENT_IMPORTANCE, 
        default=2,
        help_text="How important is this comment for the author?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-importance_level', 'created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure only authors can pin comments"""
        if self.is_pinned and not self.post.author == self.user:
            # Only the post author can pin comments
            self.is_pinned = False
        super().save(*args, **kwargs)


class SavedPost(models.Model):
    """Model for users to save posts they're interested in"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='saved_posts'
    )
    post = models.ForeignKey(
        BookPost, 
        on_delete=models.CASCADE, 
        related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.post.title}"


class PostLike(models.Model):
    """Model for users to like posts"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='liked_posts'
    )
    post = models.ForeignKey(
        BookPost, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    liked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-liked_at']
    
    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"


class Notification(models.Model):
    """Model for user notifications"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.CharField(max_length=255)
    related_post = models.ForeignKey(
        BookPost, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"


class UserFollow(models.Model):
    """Model for users to follow each other"""
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following'
    )
    followed = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'followed']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
    
    def save(self, *args, **kwargs):
        """Prevent users from following themselves"""
        if self.follower == self.followed:
            raise ValueError("Users cannot follow themselves.")
        super().save(*args, **kwargs)