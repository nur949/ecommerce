from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User

from orders.models import Address

from .models import UserProfile


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})

    def clean_username(self):
        email = self.cleaned_data.get('username', '').strip().lower()
        user = User.objects.filter(email__iexact=email).only('username').first()
        return user.username if user else email


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Full Name', required=True)
    phone = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'email', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'Full Name',
            'email': 'Email Address',
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

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].strip().lower()
        user.email = email
        user.username = email
        user.first_name = self.cleaned_data['first_name'].strip()
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ('avatar', 'phone')

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        initial = kwargs.pop('initial', {})
        if user:
            initial.update({'name': user.get_full_name() or user.first_name or user.username, 'email': user.email})
        super().__init__(*args, initial=initial, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control', 'accept': 'image/*'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Phone number'})
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Full name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email address'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        queryset = User.objects.filter(email__iexact=email)
        if self.user:
            queryset = queryset.exclude(pk=self.user.pk)
        if queryset.exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['name'].strip()
            self.user.email = self.cleaned_data['email']
            self.user.username = self.cleaned_data['email']
            if commit:
                self.user.save(update_fields=['first_name', 'email', 'username'])
                profile.user = self.user
                profile.save()
        return profile


class AccountPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'old_password': 'Current password',
            'new_password1': 'New password',
            'new_password2': 'Confirm new password',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': placeholders.get(name, field.label)})


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('full_name', 'phone', 'city', 'area', 'address_line', 'postcode', 'delivery_type', 'is_default')
        labels = {
            'full_name': 'Recipient name',
            'address_line': 'Street address',
            'postcode': 'Postal code',
            'is_default': 'Set as default address',
        }
        widgets = {
            'address_line': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_default':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})
