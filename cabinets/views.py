from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

from blog.models import Category
from .models import Cabinet, Certificate
from .forms import SubscribeForm, UnsubscribeForm
from blog.models import Course


class CabinetView(View):
    template_name = "cabinets/cabinet.html"
    title = "Кабінет"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        user = self.request.user
        cabinet_list = Cabinet.objects.filter_by_user(user)

        paginator = Paginator(cabinet_list, 10)  # Show 10 contacts per page
        page_request_var = "page"
        page = self.request.GET.get(page_request_var)
        try:
            cabinet_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            cabinet_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            cabinet_list = paginator.page(paginator.num_pages)

        context = {
            "title": self.title,
            "category_list": category_list,
            "cabinet_list": cabinet_list,
            "page_request_var": page_request_var
        }

        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        subscribe_form = SubscribeForm(self.request.POST)
        if subscribe_form.is_valid():
            c_type = subscribe_form.cleaned_data.get("content_type")
            obj_id = subscribe_form.cleaned_data.get("object_id")
            content_type = ContentType.objects.get(model=c_type)

            new_obj, created = Cabinet.objects.get_or_create(
                user=self.request.user,
                content_type=content_type,
                object_id=obj_id,
            )
            if created:
                return redirect(new_obj.content_object.get_absolute_url())

        return redirect(reverse("cabinets:index"))


class CourseUnsubscribe(View):
    template_name = "cabinets/confirm_unsubscribe.html"
    title = "Відписка"

    def get(self, *args, **kwargs):
        subscribed_course = get_object_or_404(Course, slug=kwargs["slug"])
        initial_data = {
            "content_type": subscribed_course.get_content_type,
            "object_id": subscribed_course.id
        }
        unsubscribe_form = UnsubscribeForm(initial=initial_data)
        context = {
            "title": self.title,
            "subscribed_course": subscribed_course,
            "unsubscribe_form": unsubscribe_form
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        unsubscribe_form = UnsubscribeForm(self.request.POST)
        if unsubscribe_form.is_valid():
            user = self.request.user
            c_type = unsubscribe_form.cleaned_data.get("content_type")
            content_type = ContentType.objects.get(model=c_type)
            obj_id = unsubscribe_form.cleaned_data.get("object_id")
            subscribed_course = get_object_or_404(Cabinet,
                                                  content_type=content_type,
                                                  object_id=obj_id,
                                                  user=user
                                                  )
            subscribed_course.delete()
            course_url = subscribed_course.content_object.get_absolute_url()
            messages.success(self.request, "Відписка успішна.")
            return redirect(course_url)
        else:
            return redirect(reverse("cabinets:index"))


class CertificateList(View):
    template_name = "cabinets/certificates.html"
    title = "Сертифікати"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        user = self.request.user
        certificate_list = Certificate.objects.filter(cabinet__user=user)

        paginator = Paginator(certificate_list, 10)  # Show 10 contacts per page
        page_request_var = "page"
        page = self.request.GET.get(page_request_var)
        try:
            certificate_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            certificate_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            certificate_list = paginator.page(paginator.num_pages)

        context = {
            "title": self.title,
            "category_list": category_list,
            "certificate_list": certificate_list,
            "page_request_var": page_request_var,
        }
        return render(self.request, self.template_name, context)


class CertificateUpload(View):
    template_name = "cabinets/certificate_form.html"
    title = "Вивантаження сертифікату"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()

        course_obj = get_object_or_404(Course, slug=kwargs["slug"])

        user = self.request.user
        content_type = course_obj.get_content_type
        obj_id = course_obj.id
        cabinet = get_object_or_404(Cabinet,
                                    user=user,
                                    content_type=content_type,
                                    object_id=obj_id,
                                    )

        try:
            certificate_obj = Certificate.objects.get(
                                            cabinet=cabinet
                                            )
        except Certificate.DoesNotExist:
            certificate_obj = False

        print(certificate_obj)

        context = {
            "title": self.title,
            "category_list": category_list,
            "course": course_obj,
            "certificate": certificate_obj,
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        course = get_object_or_404(Course, slug=kwargs["slug"])
        content_type = course.get_content_type
        obj_id = course.id
        user = self.request.user
        cabinet = get_object_or_404(Cabinet,
                                    content_type=content_type,
                                    object_id=obj_id,
                                    user=user,
                                    )

        try:
            certificate = self.request.FILES["certificate"]
            upload_data = cloudinary.uploader.upload(certificate)
            certificate_url = upload_data['url']
            public_id = upload_data['public_id']
            certificate_type = upload_data['format']

            try:
                certificate_obj = Certificate.objects.get(cabinet=cabinet)
                certificate_obj.url = certificate_url
                certificate_obj.type = certificate_type
                certificate_obj.public_id = public_id
                certificate_obj.save()
            except Certificate.DoesNotExist:
                Certificate.objects.create(
                    cabinet=cabinet,
                    url=certificate_url,
                    type=certificate_type,
                    public_id=public_id,
                )
                cabinet.is_passed = True
                cabinet.save()

            messages.success(self.request, "Сертифікат вивантажено.")
            return redirect(reverse("cabinets:certificates"))
        except KeyError:
            messages.warning(self.request, "Не вдалося вивантажити сертифікат.")

        params = {
            "slug": cabinet.content_object.slug,
        }
        return redirect(reverse("cabinets:certificate_upload", kwargs=params))
