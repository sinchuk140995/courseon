from django import forms
from pagedown.widgets import PagedownWidget

from .models import Course, Category


class CourseForm(forms.ModelForm):
    describe = forms.CharField(widget=PagedownWidget(show_preview=False))
    slug = forms.SlugField(label="Транслітерація",
                           required=False,
                           help_text="Якщо назва кирилицею. "
                                     "Всі літери повинні бути малі. "
                                     "Замість пробілів має бути знак тире.")

    class Meta:
        model = Course

        fields = [
            "name",
            "slug",
            "course_url",
            "category",
            "logotype",
            "describe",
        ]
        labels = {
            "name": "Назва",
            "slug": "Транслітерація",
            "course_url": "URL",
            "category": "Категорія",
            "logotype": "Логотип",
            "describe": "Опис",
        }


class CategoryForm(forms.ModelForm):
    slug = forms.SlugField(label="Транслітерація",
                           required=False,
                           help_text="Якщо назва кирилицею. "
                                     "Всі літери повинні бути малі. "
                                     "Замість пробілів має бути знак тире.")

    class Meta:
        model = Category

        fields = [
            "name",
            "slug",
            "logotype",
        ]
        labels = {
            "name": "Назва",
            "logotype": "Логотип",
        }
