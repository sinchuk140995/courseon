from django.views import View
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import RedirectView
# API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
# cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

from .models import Category, Course
from .forms import CourseForm, CategoryForm
from comments.forms import CommentForm
from comments.models import Comment
from cabinets.forms import SubscribeForm


class IndexView(View):
    template_name = "blog/index.html"
    title = "Головна"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        context = {
            "title": self.title,
            "category_list": category_list,
        }

        return render(self.request, self.template_name, context)


class CategoryView(View):
    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        category_obj = get_object_or_404(Category, slug=kwargs["slug"])
        course_list = Course.objects.filter(category=category_obj)

        paginator = Paginator(course_list, 10)  # Show 10 contacts per page
        page_request_var = "page"
        page = self.request.GET.get(page_request_var)
        try:
            course_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            course_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            course_list = paginator.page(paginator.num_pages)

        context = {
            "title": category_obj.name,
            "category": category_obj,
            "category_list": category_list,
            "course_list": course_list,
            "page_request_var": page_request_var,
        }

        return render(self.request, 'blog/category.html', context)


class CategoryCreate(View):
    template_name = "blog/add_content_form.html"
    title = "Додавання категорії"

    def get(self, *args, **kwargs):
        category_form = CategoryForm()
        context = {
            'create_form': category_form,
            'title': self.title,
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        category_form = CategoryForm(self.request.POST)

        if category_form.is_valid():
            category_obj = category_form.save(commit=False)

            try:
                logotype = self.request.FILES["logotype"]
                upload_dict = cloudinary.uploader.upload(logotype)
                category_obj.logo_url = upload_dict['url']
                category_obj.public_id = upload_dict['public_id']
            except KeyError:
                category_obj.logo_url = "http://res.cloudinary.com/dzmnskqms/image/upload/v1495641140/unknown_j8ydbn.png"

            category_obj.save()
            messages.success(self.request, "Категорію додано.")
            return redirect("blog:index")
        else:
            messages.warning(self.request, "Невірні дані.")
            context = {
                "create_form": category_form
            }
            return render(self.request, self.template_name, context)


class CategoryUpdate(View):
    template_name = "blog/add_content_form.html"
    title = "Редагування категорії"

    def get(self, *args, **kwargs):
        category_obj = get_object_or_404(Category, slug=kwargs["slug"])

        category_form = CategoryForm(instance=category_obj)
        context = {
            "title": self.title,
            "category": category_obj,
            "create_form": category_form,
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        category_obj = get_object_or_404(Category, slug=kwargs["slug"])

        category_form = CategoryForm(self.request.POST, instance=category_obj)
        if category_form.is_valid():
            category_obj = category_form.save(commit=False)

            try:
                logotype = self.request.FILES["logotype"]
                upload_dict = cloudinary.uploader.upload(logotype)
                category_obj.logo_url = upload_dict['url']
                category_obj.public_id = upload_dict['public_id']
            except KeyError:
                pass

            category_obj.save()
            messages.success(self.request, "Зміни збережено.")
            return redirect(category_obj.get_absolute_url())
        else:
            messages.warning(self.request, "Невірні дані.")
            context = {
                "create_form": category_obj,
            }
            return render(self.request, self.template_name, context)


@method_decorator(login_required, name='post')
class CourseDetail(View):
    template_name = "blog/course.html"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        course_obj = get_object_or_404(Course, slug=kwargs["slug"])
        comments = course_obj.comments
        initial_data = {
            "content_type": course_obj.get_content_type,
            "object_id": course_obj.id,
        }

        comment_form = CommentForm(initial=initial_data)
        subscribe_form = SubscribeForm(initial=initial_data)

        is_subscribed = False
        is_passed = False
        is_author = False
        if self.request.user.is_authenticated():
            cabinet = Course.is_subscribed(course_obj, self.request.user)
            if cabinet:
                is_subscribed = True

            if hasattr(cabinet, 'is_passed') or \
                    isinstance(getattr(type(cabinet), 'is_passed', None), property):
                is_passed = cabinet.is_passed
            if self.request.user == course_obj.author:
                is_author = True

        context = {
            "title": course_obj.name,
            "category_list": category_list,
            "course": course_obj,
            "comments": comments,
            "comment_form": comment_form,
            "subscribe_form": subscribe_form,
            "is_subscribed": is_subscribed,
            "is_passed": is_passed,
            "is_author": is_author,
        }

        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        course_obj = get_object_or_404(Course, slug=kwargs["slug"])
        comment_form = CommentForm(self.request.POST, self.request.FILES)
        if comment_form.is_valid():
            c_type = comment_form.cleaned_data.get("content_type")
            content_type = ContentType.objects.get(model=c_type)
            obj_id = comment_form.cleaned_data.get("object_id")
            text = comment_form.cleaned_data.get("text")
            parent_obj = None
            try:
                parent_id = int(self.request.POST.get('parent_id'))
            except KeyError:
                parent_id = None
            except TypeError:
                parent_id = None

            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    parent_obj = parent_qs.first()

            new_obj, created = Comment.objects.get_or_create(
                                    user=self.request.user,
                                    content_type=content_type,
                                    object_id=obj_id,
                                    text=text,
                                    parent=parent_obj
                                )

            if created:
                return redirect(new_obj.content_object.get_absolute_url())

        return redirect(course_obj.get_absolute_url())


class CourseLikeToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        course_obj = get_object_or_404(Course, slug=kwargs["slug"])
        user = self.request.user

        if user in course_obj.likes.all():
            course_obj.likes.remove(user)
        else:
            course_obj.likes.add(user)

        return course_obj.get_absolute_url()


class LikeAPIToggle(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None, *args, **kwargs):
        course_obj = get_object_or_404(Course, slug=kwargs["slug"])
        user = self.request.user

        if user in course_obj.likes.all():
            liked = False
            course_obj.likes.remove(user)
        else:
            liked = True
            course_obj.likes.add(user)
        likes_count = course_obj.likes.count()
        data = {
            "liked": liked,
            "likes_count": likes_count,
        }
        return Response(data)


class CourseCreate(View):
    template_name = "blog/add_content_form.html"
    title = "Додавання курсу"

    def get(self, *args, **kwargs):
        course_form = CourseForm()
        context = {
            "title": self.title,
            "create_form": course_form,
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        course_form = CourseForm(self.request.POST, self.request.FILES)

        if course_form.is_valid():
            course_obj = course_form.save(commit=False)

            try:
                logotype = self.request.FILES["logotype"]
                upload_dict = cloudinary.uploader.upload(logotype)
                course_obj.logo_url = upload_dict['url']
                course_obj.public_id = upload_dict['public_id']
            except KeyError:
                pass

            course_obj.author = self.request.user
            if self.request.user.is_staff or self.request.user.is_superuser:
                course_obj.check_status = True
            else:
                course_obj.check_status = False

            course_obj.save()
            messages.success(self.request, "Курс додано.")
            return redirect(course_obj.get_absolute_url())
        else:
            messages.warning(self.request, "Невірні дані.")
            context = {
                "create_form": course_form
            }
            return render(self.request, self.template_name, context)


class CourseUpdate(View):
    template_name = "blog/add_content_form.html"
    title = "Редагування курсу"

    def get(self, *args, **kwargs):
        course_obj = get_object_or_404(Course, slug=kwargs["slug"])

        if course_obj.author != self.request.user:
            response = HttpResponse()
            response.status_code = 403
            return response

        course_form = CourseForm(instance=course_obj)
        context = {
            "title": self.title,
            # "course": course_obj,
            "create_form": course_form,
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        course_obj = get_object_or_404(Course, slug=kwargs["slug"])

        course_form = CourseForm(self.request.POST, instance=course_obj)
        if course_form.is_valid():
            course_obj = course_form.save(commit=False)

            try:
                logotype = self.request.FILES["logotype"]
                upload_dict = cloudinary.uploader.upload(logotype)
                course_obj.logo_url = upload_dict['url']
                course_obj.public_id = upload_dict['public_id']
            except KeyError:
                pass

            course_obj.save()
            messages.success(self.request, "Зміни збережено.")
            return redirect(course_obj.get_absolute_url())
        else:
            messages.warning(self.request, "Невірні дані.")
            context = {
                # "course": course_obj,
                "create_form": course_form,
            }
            return render(self.request, self.template_name, context)


class CourseDelete(View):
    def get(self, *args, **kwargs):
        course_obj = get_object_or_404(Course, slug=kwargs["slug"])

        if course_obj.author != self.request.user:
            response = HttpResponse()
            response.status_code = 403
            return response

        category = course_obj.category
        course_obj.delete()
        messages.success(self.request, "Курс видалено.")
        return redirect(category.get_absolute_url())


class Search(View):
    template_name = "blog/search_result.html"
    title = "Пошук"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        course_list = Course.objects.all()
        query = self.request.GET.get("q")
        if query:
            course_list = course_list.filter(
                Q(name__icontains=query) |
                Q(describe__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(author__last_name__icontains=query)
            ).distinct()

        context = {
            "title": self.title,
            "category_list": category_list,
            "course_list": course_list,
        }

        return render(self.request, self.template_name, context)
