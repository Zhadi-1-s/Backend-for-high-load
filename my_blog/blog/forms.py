from django import forms
from .models import Post, Tag


class PostForm(forms.ModelForm):

    tags = forms.CharField(help_text='Enter tags separated by commas.')

    class Meta:
        model = Post
        fields = ['title', 'content']

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            tag_names = [name.strip() for name in self.cleaned_data['tags'].split(',')]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)
        return post    


from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']