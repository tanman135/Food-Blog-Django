from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Recipe, Category, Comment, Rating
from .forms import RecipeForm, CommentForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class AboutView(TemplateView):
    template_name = 'food/about.html'

class ContactView(TemplateView):
    template_name = 'food/contact.html'


class HomeView(ListView):
    model = Recipe
    template_name = 'food/home.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        return Recipe.objects.filter(status='published').order_by('-created_at')[:6]


class RecipeListView(ListView):
    model = Recipe
    template_name = 'food/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 6

    def get_queryset(self):
        return Recipe.objects.filter(status='published').order_by('-created_at')




class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'food/recipe_detail.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()

        avg = recipe.average_rating()
        full_stars = int(avg)
        half_star = (avg - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)

        user = self.request.user
        user_has_rated = False
        if user.is_authenticated:
            user_has_rated = recipe.ratings.filter(user=user).exists()

        context.update({
            'form': CommentForm(),
            'average_rating': avg,
            'full_stars': range(full_stars),
            'half_star': half_star,
            'empty_stars': range(empty_stars),
            'user_has_rated': user_has_rated,
        })

        if user.is_staff:
            context['comments'] = recipe.comments.all().order_by('-created_at')
        else:
            context['comments'] = recipe.comments.filter(rejected=False).order_by('-created_at')

        return context





class AddRecipeView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    success_url = reverse_lazy('recipe_list')
    model = Recipe
    form_class = RecipeForm
    template_name = 'food/add_recipe.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        draft = Recipe.objects.filter(status='draft', is_autosaved=True, author=self.request.user).order_by('-updated_at').first()
        if draft:
            kwargs['instance'] = draft
            self.draft = draft
        else:
            self.draft = None
        return kwargs


    def form_valid(self, form):
        save_action = self.request.POST.get('save_action')

        if save_action == 'draft':
            form.instance.status = 'draft'
            form.instance.is_autosaved = True
            form.instance.author = self.request.user
            return super().form_valid(form)

        # Else it's publish, check for full fields
        form.instance.status = 'published'
        form.instance.is_autosaved = False
        form.instance.author = self.request.user

        # Enforce required fields for publish
        required_fields = ['title', 'description', 'prep_time']
        for field in required_fields:
            if not form.cleaned_data.get(field):
                form.add_error(field, "This field is required for publishing.")
                return self.form_invalid(form)

        return super().form_valid(form)

    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     form.instance.created_at = timezone.now()

    #     if 'save_draft' in self.request.POST:
    #         form.instance.status = 'draft'
    #         form.instance.is_autosaved = True
    #     else:
    #         form.instance.status = 'published'
    #         form.instance.is_autosaved = False

    #     return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['draft_id'] = self.draft.id if self.draft else ''
        return context


class EditRecipeView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'recipe_detail'
    model = Recipe
    form_class = RecipeForm
    template_name = 'food/edit_recipe.html'

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise PermissionDenied
        return Recipe.objects.filter(author=self.request.user)
    

    def get_success_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.object.pk})


class DeleteRecipeView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = 'food/delete_recipe.html'
    success_url = reverse_lazy('recipe_list')
    login_url = '/login/'

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise PermissionDenied
        return Recipe.objects.filter(author=self.request.user)


class CategoryRecipeListView(ListView):
    model = Recipe
    template_name = 'food/category_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 4

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['category_id'])
        return Recipe.objects.filter(category=self.category).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Manual pagination (this is the fix)
        recipe_list = self.get_queryset()
        paginator = Paginator(recipe_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['recipes'] = page_obj
        context['paginator'] = paginator
        context['is_paginated'] = page_obj.has_other_pages()
        context['category'] = self.category
        return context



class CategoryListView(ListView):
    model = Category
    template_name = 'food/category_list.html'
    context_object_name = 'categories'


# -------------------- Comments --------------------

@login_required
def add_comment_to_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            comment.created_at = timezone.now()
            comment.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = CommentForm()
    return render(request, 'food/comment_form.html', {'form': form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff:
        recipe_id = comment.recipe.id
        comment.delete()
        return redirect('recipe_detail', pk=recipe_id)
    else:
        raise PermissionDenied


# ✅ NEW: Approve comment
@user_passes_test(lambda u: u.is_staff)
def approve_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approved = True
    comment.save()
    return redirect('recipe_detail', pk=comment.recipe.pk)


# ✅ NEW: Reject comment (deletes it)
@user_passes_test(lambda u: u.is_staff)
def reject_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.rejected = True
    comment.save()
    return redirect('recipe_detail', pk=comment.recipe.pk)


# -------------------- Search & Auth --------------------

def search_results(request):
    query = request.GET.get('q', '')
    min_rating = request.GET.get('min_rating')
    max_prep_time = request.GET.get('max_prep_time')

    recipe_list = Recipe.objects.all()

    if query:
        recipe_list = recipe_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(category__name__icontains=query)
        )

    if max_prep_time and max_prep_time.isdigit():
        max_prep_val = int(max_prep_time)
        recipe_list = recipe_list.filter(prep_time__lte=max_prep_val)

    # Now convert to list for rating filter
    recipe_list = list(recipe_list)

    if min_rating and min_rating.isdigit():
        min_rating_val = int(min_rating)
        recipe_list = [r for r in recipe_list if r.average_rating() >= min_rating_val]

    # Sort by created_at descending (in Python, since recipe_list is a list now)
    recipe_list.sort(key=lambda r: r.created_at, reverse=True)

    # Paginate the list (works with list)
    paginator = Paginator(recipe_list, 4)
    page = request.GET.get('page')
    try:
        recipes = paginator.page(page)
    except PageNotAnInteger:
        recipes = paginator.page(1)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)

    context = {
        'recipes': recipes,
        'query': query,
        'min_rating': min_rating or '',
        'max_prep_time': max_prep_time or '',
    }
    return render(request, 'food/search_results.html', context)



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def toggle_like(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user in recipe.likes.all():
        recipe.likes.remove(request.user)
    else:
        recipe.likes.add(request.user)
    return redirect('recipe_detail', pk=recipe_id)


@login_required
def rate_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    rating_value = int(request.POST.get('rating', 0))

    if rating_value < 1 or rating_value > 5:
        messages.error(request, "Invalid rating value.")
        return redirect('recipe_detail', pk=pk)

    rating, created = Rating.objects.update_or_create(
        recipe=recipe,
        user=request.user,
        defaults={'value': rating_value},
    )

    if created:
        messages.success(request, "Thanks for rating!")
    else:
        messages.success(request, "Your rating has been updated!")

    return redirect('recipe_detail', pk=pk)



@login_required
def autosave_recipe(request):
    if request.method == 'POST':
        recipe_id = request.POST.get('id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        prep_time = request.POST.get('prep_time')
        servings = request.POST.get('servings')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        category = request.POST.get('category')
        video_link = request.POST.get('video_link')

        if recipe_id:
            try:
                recipe = Recipe.objects.get(id=recipe_id, author=request.user)
            except Recipe.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Recipe not found'})
        else:
            recipe = Recipe(author=request.user)

        recipe.title = title
        recipe.description = description
        recipe.prep_time = prep_time if prep_time else None
        recipe.servings = servings if servings else None
        recipe.ingredients = ingredients
        recipe.instructions = instructions
        recipe.video_link = video_link
        recipe.is_autosaved = True
        recipe.status = 'draft'

        if category:
            try:
                from .models import Category
                recipe.category = Category.objects.get(id=category)
            except Category.DoesNotExist:
                pass

        recipe.save()

        return JsonResponse({'success': True, 'id': recipe.id})

    return JsonResponse({'success': False, 'error': 'Invalid request'})