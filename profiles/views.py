from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .forms import ProfileUpdateForm, UserUpdateForm
from .models import UserProfile


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class ProfileEditView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context.setdefault('profile', profile)
        context.setdefault('user_form', UserUpdateForm(instance=self.request.user))
        context.setdefault('profile_form', ProfileUpdateForm(instance=profile))
        return context

    def post(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profiles:profile')

        messages.error(request, 'Please fix the highlighted fields.')
        return self.render_to_response(
            self.get_context_data(profile=profile, user_form=user_form, profile_form=profile_form)
        )


profile_view = ProfileView.as_view()
profile_edit = ProfileEditView.as_view()
