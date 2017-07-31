from django import forms
from models import SignUpModel


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

