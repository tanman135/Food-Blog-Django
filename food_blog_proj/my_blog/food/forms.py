from django import forms
from .models import Recipe, Comment
from ckeditor.widgets import CKEditorWidget

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'title',
            'description',
            'category',
            'ingredients',
            'instructions',
            'image',
            'video_link',
            'servings',
            'prep_time',
            'status',
        ]
        widgets = {
            'ingredients': forms.Textarea(attrs={'rows': 4}),
            'instructions': forms.Textarea(attrs={'rows': 6}),
            'prep_time': forms.NumberInput(attrs={'class': 'form-control', 'min': '5'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Let all fields be non-required by default, required only on publish
        for field in self.fields.values():
            field.required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': CKEditorWidget(),
        }