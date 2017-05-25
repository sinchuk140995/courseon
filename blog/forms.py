from django import forms
from pagedown.widgets import PagedownWidget

from .models import Course, Category


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category

        fields = [
            "name",
        ]
        labels = {
            "name": "Назва",
        }


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course

        fields = [
            "name",
            "category",
            "course_url",
            "describe",
            "platform_name",
            "platform_url",
        ]
        labels = {
            "name": "Назва",
            "category": "Категорія",
            "course_url": "URL адреса",
        }

    describe = forms.CharField(label="Опис", widget=PagedownWidget(show_preview=False))
    platform_name = forms.CharField(label="Назва платформи курсу",
                                    help_text="Наприклад: Прометеус, Курсера",
                                    required=False,
                                    )
    platform_url = forms.URLField(label="Посилання на платформу курсу",
                                  help_text="Наприклад: https://prometheus.org.ua/",
                                  required=False,
                                  )
