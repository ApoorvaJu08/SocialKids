from django import forms
from models import SignUpModel, PostModel, LikeModel


# kldfsnj
class SignUpForm(forms.ModelForm):
    class Meta:
        model = SignUpModel
        fields = ['name', 'email', 'username', 'password']


#akjsbfkj
class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    fields = ['username', 'password']


# c
class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image', 'caption']


# d
class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

