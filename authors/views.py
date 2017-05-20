from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views import View
from django.contrib import messages

from blog.forms import CourseForm


class ApplicantView(View):
    template_name = "blog/course_form.html"

    def get(self, *args, **kwargs):
        course_form = CourseForm()
        context = {
            "course_form": course_form
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        course_form = CourseForm(self.request.POST, self.request.FILES)

        if course_form.is_valid():
            course_obj = course_form.save(commit=False)
            course_obj.author = self.request.user
            course_obj.check_status = None
            course_obj.save()
            messages.success(self.request, "Курс відправлено на перевірку.")
            return redirect(reverse("blog:index"))
        else:
            print(course_form.errors)
            messages.error(self.request, "Невірні дані.")

        context = {
            "course_form": course_form
        }
        return render(self.request, self.template_name, context)
