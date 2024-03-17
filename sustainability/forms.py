from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    firstname = forms.CharField(max_length=100, label='First Name')
    lastname = forms.CharField(max_length=100, label='Last Name')
    dob = forms.CharField(max_length=100, label='Date of Birth')
    email = forms.EmailField(max_length=254, label='Email')
    team_colour = forms.ChoiceField(choices=[('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], label='Team Colour')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    confirmpassword = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors.clear()

