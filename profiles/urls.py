from django.urls import path

from .views import profile_edit, profile_view

app_name = 'profiles'

urlpatterns = [
    path('', profile_view, name='profile'),
    path('edit/', profile_edit, name='profile_edit'),
]
