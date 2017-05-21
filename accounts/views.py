from django.contrib.auth import (
                                authenticate,
                                login,
                                logout
                            )
from django.shortcuts import render, redirect
from django.views import View
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group, Permission

from .forms import UserLoginForm, UserRegistrationForm


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

            # author status
            author_group = Group.objects.get(name="authors")
            user.groups.add(author_group)

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
