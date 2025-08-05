from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    ingredients = models.TextField()
    instructions = models.TextField()
    image = models.ImageField(upload_to='recipe_images/')
    video_link = models.URLField(blank=True, null=True)
    servings = models.PositiveIntegerField(null=True, blank=True)
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_recipes', blank=True)
    is_autosaved = models.BooleanField(default=False)



    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()
    

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.value for r in ratings) / ratings.count(), 1)
        return 0
    
    



class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = RichTextField()
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.recipe.title}'



class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField()

    class Meta:
        unique_together = ('recipe', 'user') 

    def __str__(self):
        return f"{self.user} rated {self.recipe} as {self.value}"