from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='E-mail / Username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Full Name', required=True)
    phone = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'email', 'username', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'Full Name',
            'email': 'Email Address',
            'username': 'Username',
            'phone': 'Phone Number',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': placeholders.get(name, field.label)})

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone and not phone.replace('+', '', 1).replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError('Enter a valid phone number.')
        return phone
