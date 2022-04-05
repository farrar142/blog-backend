from django import forms
from .models import *

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['name']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title','context']
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['context']
        
class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['context']