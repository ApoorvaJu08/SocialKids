from django import forms
from models import SignUpModel, PostModel, LikeModel


# kldfsnj
class SignUpForm(forms.ModelForm):
    class Meta:
        model = SignUpModel
        fields = ['name', 'email', 'username', 'password']


#akjsbfkj
class LoginForm(forms.ModelForm):
    class Meta:
        model = SignUpModel
        fields = ['username', 'password']


# c
class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['user', 'image', 'image_url', 'caption']


# d
class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

