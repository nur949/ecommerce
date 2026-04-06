from django.urls import path

from .views import UserLoginView, UserLogoutView, dashboard, register_view

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
]
