from django import forms
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'name@example.com',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': placeholders.get(name, field.label)})
            if name == 'email':
                field.required = True

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        queryset = User.objects.filter(email__iexact=email)
        if self.user:
            queryset = queryset.exclude(pk=self.user.pk)
        if queryset.exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].strip().lower()
        if user.email:
            user.username = user.email
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'bio', 'phone', 'address', 'website')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'bio': 'Write a short customer profile or team bio.',
            'phone': '+880 1711 111111',
            'address': 'House, road, area, city',
            'website': 'https://example.com',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': placeholders.get(name, field.label)})
        self.fields['profile_picture'].widget.attrs.update({'accept': 'image/*'})

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        normalized = phone.replace('+', '', 1).replace('-', '').replace(' ', '')
        if phone and (not normalized.isdigit() or len(normalized) < 8):
            raise forms.ValidationError('Enter a valid phone number.')
        return phone
