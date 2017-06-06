from django import forms
from django.contrib.auth import (
                                authenticate,
                                get_user_model,
                            )

from .models import Profile

User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField(label="Ім'я користувача")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Невірно введено логін або пароль.")
            if not user.is_active:
                raise forms.ValidationError("Користувач не активний.")
        else:
            raise forms.ValidationError("Не введено логін або пароль.")

        return super(UserLoginForm, self).clean()


class UserRegistrationForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        ]

    email = forms.EmailField(label="Електронна пошта", required=True)
    username = forms.CharField(label="Логін",
                               help_text="Не більше 150 символів. "
                                         "Дозволено букви, цифри і символи @/./+/-/_.")
    first_name = forms.CharField(label="Ім'я", required=True)
    last_name = forms.CharField(label="Прізвище", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_rpt = forms.CharField(widget=forms.PasswordInput, label="Повторіть пароль")

    def clean_username(self):
        username = self.cleaned_data.get("username")

        try:
            User.objects.get(username=username)
            raise forms.ValidationError("Користувач з таким логіном вже зареєстрований.")
        except User.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data.get("email")

        try:
            User.objects.get(email=email)
            raise forms.ValidationError("Користувач з такою електронною поштою вже зареєстрований.")
        except User.DoesNotExist:
            return email

    def clean_password_rpt(self):
        password = self.cleaned_data.get("password")
        password_rpt = self.cleaned_data.get("password_rpt")

        if not password == password_rpt:
            raise forms.ValidationError("Паролі повинні співпадати.")

        return password


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = [
            "university",
            "faculty",
            "social_link",
            "describe",
        ]

        labels = {
            "university": "Навчальний заклад",
            "faculty": "Факультет",
            "social_link": "Посилання на профіль в соціальних мережах",
        }

    describe = forms.CharField(label="Про себе",
                               widget=PagedownWidget(show_preview=False),
                               required=False,
                               )
