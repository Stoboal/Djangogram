from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm

from .models import Post, Comment, User


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Input your username'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Provide your e-mail address'
    }))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'placeholder': 'Provide your password'
    }))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat your password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Input your username'
    }))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'placeholder': 'Provide your password'
    }))

    class Meta:
        model = User
        fields = ['username', 'password']


class PostForm(forms.ModelForm):
    image = forms.ImageField()
    description = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Photo description'})
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'})
    )

    class Meta:
        model = Post
        fields = ['image', 'description', 'tags']


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Put your comment here'})
    )

    class Meta:
        model = Comment
        fields = ['text']


class UserUpdateForm(UserChangeForm):
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Input your username'
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Input your name'
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Input your last name'
    }))
    biography = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Tell the world about yourself'
    }))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        'placeholder': 'Fill this field if you want to change your email'
    }))
    image = forms.ImageField(required=False)

    password = None

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'biography', 'email', 'image']


class AddPostTagsForm(forms.Form):
    tags = forms.CharField(
        required=False,
        label='Tags',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'})
    )


class PostDescriptionForm(forms.Form):
    description = forms.CharField(
        required=False,
        label='Description',
        max_length=512,
        widget=forms.TextInput(attrs={'placeholder': 'Enter new description'})
    )
