from django.contrib import admin
from .models import Recipe, Category, Comment

# Basic admin registrations for Recipe and Category
admin.site.register(Recipe)
admin.site.register(Category)

# Customized admin for Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'approved')
    list_editable = ('approved',)
