from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
# from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import (
                                authenticate,
                                login,
                                logout
                            )

from .forms import (
                    UserLoginForm,
                    UserRegistrationForm,
                    ProfileForm,
                    )
from .models import Profile


class IsLoginMixin(UserPassesTestMixin):
    login_url = "/"

    def test_func(self):
        return self.request.user.is_anonymous


class Login(IsLoginMixin, View):
    template_name = "accounts/form.html"
    title = "Авторизація"

    def get(self, *args, **kwargs):
        form = UserLoginForm()
        context = {
            "title": self.title,
            "form": form,
            "login": True,
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        form = UserLoginForm(self.request.POST)
        next = self.request.GET.get("next")
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            login(self.request, user)
            if next:
                return redirect(next)
            else:
                return redirect(reverse("blog:index"))

        context = {
            "form": form,
            "title": self.title
        }
        return render(self.request, self.template_name, context)


class Register(IsLoginMixin, View):
    template_name = "accounts/form.html"
    title = "Реєстрація"

    def get(self, *args, **kwargs):
        form = UserRegistrationForm()
        context = {
            "title": "Реєстрація",
            "form": form
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        form = UserRegistrationForm(self.request.POST)
        next = self.request.GET.get("next")
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            user.set_password(password)
            user.save()

            new_user = authenticate(username=user.username, password=password)
            login(self.request, new_user)
            if next:
                return redirect(next)
            else:
                return redirect(reverse("blog:index"))

        context = {
            "title": self.title,
            "form": form
        }
        return render(self.request, self.template_name, context)


class Logout(View):
    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse("login"))


class ProfileManage(View):
    template_name = "accounts/form.html"
    title = "Профіль"

    def get(self, *args, **kwargs):
        try:
            user = self.request.user
            profile_obj = Profile.objects.get(user=user)
            form = ProfileForm(instance=profile_obj)
        except Profile.DoesNotExist:
            form = ProfileForm()

        context = {
            "title": "Інформація профілю",
            "submit": "Зберегти",
            "form": form
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        user = self.request.user
        profile_obj = None
        try:
            profile_obj = Profile.objects.get(user=user)
            profile_form = ProfileForm(self.request.POST, instance=profile_obj)
        except Profile.DoesNotExist:
            profile_form = ProfileForm(self.request.POST)

        if profile_form.is_valid():
            if not profile_obj:
                profile_obj = profile_form.save(commit=False)
                profile_obj.user = user
                profile_obj.save()
            else:
                profile_form.save()
            messages.success(self.request, "Профіль збережено.")
            return redirect(profile_obj.get_absolute_url())
        else:
            messages.warning(self.request, "Невірні дані.")
            context = {
                "form": profile_form,
            }
            return render(self.request, self.template_name, context)


class ProfileView(View):
    template_name = "accounts/profile.html"
    title = "Профіль"

    def get(self, *args, **kwargs):
        profile_obj = None
        username = kwargs["user"]
        personal_profile = False

        try:
            user = User.objects.get(username=username)
            profile_obj = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            pass

        if self.request.user == user:
            personal_profile = True

        context = {
            "title": self.title,
            "profile": profile_obj,
            "personal_profile": personal_profile,
        }

        return render(self.request, self.template_name, context)
