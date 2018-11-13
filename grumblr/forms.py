from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django import forms
from grumblr.models import *


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': "Username"}))
    password = forms.CharField(max_length=20,
                               widget=forms.PasswordInput(attrs={'class': "form-control",
                                                                 'placeholder': "Password"}))


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': "Username"}))
    first_name = forms.CharField(max_length=20,
                                 widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': "First name"}))
    last_name = forms.CharField(max_length=20,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': "Last name"}))
    email = forms.EmailField(max_length=40,
                             widget=forms.EmailInput(attrs={'class': 'form-control',
                                                            'placeholder': "E-mail"}))
    password = forms.CharField(max_length=20,
                               widget=forms.PasswordInput(attrs={'class': "form-control",
                                                                 'placeholder': "Password"}))
    password2 = forms.CharField(max_length=20,
                                widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'placeholder': "Password confirm"}))

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        username = cleaned_data['username']
        if len(User.objects.filter(username=username)) > 0:
            raise forms.ValidationError("Username is already taken.")

        password = cleaned_data['password']
        password2 = cleaned_data['password2']
        if len(password) < 6 or len(password) > 20:
            raise forms.ValidationError("Password length should be between 6 and 20.")
        if password != password2:
            raise forms.ValidationError("Password did not match.")

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('header_photo', 'jumbotron_title', 'jumbotron_content', 'picture', 'description',
                  'age', 'location')
        widgets = {
            'header_photo': forms.FileInput(attrs={'class': "form-control-file"}),
            'jumbotron_title': forms.TextInput(attrs={'class': "form-control"}),
            'jumbotron_content': forms.Textarea(attrs={'class': "form-control", 'rows': '2'}),
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': '2'}),
            'first_name': forms.TextInput(attrs={'class': "form-control"}),
            'last_name': forms.TextInput(attrs={'class': "form-control"}),
            'age': forms.TextInput(attrs={'class': "form-control"}),
            'email': forms.EmailInput(attrs={'class': "form-control"}),
            'location': forms.TextInput(attrs={'class': "form-control"}),
            'picture': forms.FileInput(attrs={'class': "form-control-file"}),
        }
        labels = {
            'header_photo': _('Upload your header-photo'),
            'jumbotron_title': _('Header title'),
            'jumbotron_content': _('Header content'),
            'picture': _('Upload your photo'),
            'description': _('Bio'),
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'age': _('Age'),
            'email': _('E-mail'),
            'location': _('Address'),
        }

    def clean_age(self):
        age = self.cleaned_data['age']
        if age and not age.isdigit():
            raise forms.ValidationError("Invalid age")
        return age


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': "form-control"}),
            'last_name': forms.TextInput(attrs={'class': "form-control"}),
            'email': forms.EmailInput(attrs={'class': "form-control"}),
        }
        labels = {
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'email': _('Email'),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'class': "form-control",
                                             "rows": '3',
                                             "maxlength": "42",
                                             "placeholder": 'Your post should be less than 42 characters.'})
        }


class ResetForm(forms.Form):
    password = forms.CharField(max_length=20,
                               widget=forms.PasswordInput(attrs={'class': "form-control",
                                                                 'placeholder': "New password"}))
    password2 = forms.CharField(max_length=20,
                                widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'placeholder': "New password confirm"}))

    def clean(self):
        cleaned_data = super(ResetForm, self).clean()

        password = cleaned_data['password']
        password2 = cleaned_data['password2']
        if len(password) < 6 or len(password) > 20:
            raise forms.ValidationError("Password length should be between 6 and 20.")
        if password != password2:
            raise forms.ValidationError("Password did not match.")

        return cleaned_data
