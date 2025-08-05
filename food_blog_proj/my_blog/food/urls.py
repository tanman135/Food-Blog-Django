from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipe/new/', views.AddRecipeView.as_view(), name='add_recipe'),
    path('recipe/<int:pk>/edit/', views.EditRecipeView.as_view(), name='edit_recipe'),
    path('recipe/<int:pk>/delete/', views.DeleteRecipeView.as_view(), name='delete_recipe'),
    path('category/<int:category_id>/', views.CategoryRecipeListView.as_view(), name='category_recipes'),
    path('search/', views.search_results, name='search_results'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('recipe/<int:pk>/comment/', views.add_comment_to_recipe, name='add_comment'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('recipe/<int:recipe_id>/like/', views.toggle_like, name='toggle_like'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('comment/<int:pk>/approve/', views.approve_comment, name='approve_comment'),
    path('comment/<int:pk>/reject/', views.reject_comment, name='reject_comment'),
    path('recipe/<int:pk>/rate/', views.rate_recipe, name='rate_recipe'),
    path('autosave/', views.autosave_recipe, name='autosave_recipe'),
]
