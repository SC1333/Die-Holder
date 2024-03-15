from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    firstname = forms.CharField(max_length=100, label='First Name')
    lastname = forms.CharField(max_length=100, label='Last Name')
    email = forms.EmailField(max_length=254, label='Email')
    team_colour = forms.ChoiceField(choices=[('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], label='Team Colour')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email')
