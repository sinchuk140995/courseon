from django import forms
from django.contrib.auth import (
                                authenticate,
                                get_user_model,
                            )


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
    email = forms.EmailField(label="Електронна адреса")
    username = forms.CharField(label="Логін",
                               help_text="Довжина 150 символів або менше."
                                         "Дозволено букви, цифри і символи @/./+/-/_ тільки.")
    first_name = forms.CharField(label="Ім'я")
    last_name = forms.CharField(label="Прізвище")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_rpt = forms.CharField(widget=forms.PasswordInput, label="Повторіть пароль")

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'password_rpt'
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        try:
            User.objects.get(email=email)
            raise forms.ValidationError("This email has already been registered.")
        except User.DoesNotExist:
            return email

    def clean_password_rpt(self):
        password = self.cleaned_data.get("password")
        password_rpt = self.cleaned_data.get("password_rpt")

        if not password == password_rpt:
            raise forms.ValidationError("Passwords must match.")

        return password
