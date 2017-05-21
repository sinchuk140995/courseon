from django.views import View
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

from blog.models import Course, Category
from cabinets.models import Cabinet
from .models import CategoryStatistic, AuthorStatistic, CoursePopularity


class SuperuserOrStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class ApplicantList(SuperuserOrStaffMixin, View):
    template_name = "moderator/applicants.html"
    title = "Заявки"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        applicant_courses = Course.objects.filter(check_status=None)

        paginator = Paginator(applicant_courses, 10)  # Show 10 contacts per page
        page_request_var = "page"
        page = self.request.GET.get(page_request_var)
        try:
            applicants = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            applicants = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            applicants = paginator.page(paginator.num_pages)

        context = {
            "title": self.title,
            "category_list": category_list,
            "applicants": applicants,
            "page_request_var": page_request_var
        }

        return render(self.request, self.template_name, context)


class ApplicantView(SuperuserOrStaffMixin, View):
    template_name = "moderator/applicant.html"
    title = "Заявка"

    def get(self, *args, **kwargs):
        category_list = Category.objects.all()
        applicant = get_object_or_404(Course, slug=kwargs["slug"])

        context = {
            "category_list": category_list,
            "applicant": applicant,
        }

        return render(self.request, self.template_name, context)


class AcceptApplicant(SuperuserOrStaffMixin, View):
    def post(self, *args, **kwargs):
        applicant = get_object_or_404(Course, slug=kwargs["slug"])
        applicant.check_status = True
        applicant.save()
        # author = User.objects.get(id=applicant.author.id)

        # author_group = Group.objects.get(name="authors")
        # if created:
        #     add_permission = Permission.objects.get(name="Can add course")
        #     author_group.permissions = [add_permission]

        # author.groups.add(author_group)
        return redirect(reverse("moderator:applicants_list"))


class DeclineApplicant(SuperuserOrStaffMixin, View):
    def post(self, *args, **kwargs):
        applicant = get_object_or_404(Course, slug=kwargs["slug"])
        applicant.check_status = False
        applicant.save()
        return redirect(reverse("moderator:applicants_list"))


class StatisticsView(SuperuserOrStaffMixin, View):
    template_name = "moderator/statistics.html"
    title = "Статистика"

    def get(self, *args, **kwargs):
        category_stat = CategoryStatistic.objects.all()
        author_stat = AuthorStatistic.objects.all()
        course_popular = CoursePopularity.objects.all()

        category_list = Category.objects.all()

        # author_popularity
        # users = User.objects.filter(groups__name="authors")
        users = User.objects.all()
        author_popular = dict()
        for user in users:
            count = CoursePopularity.objects.filter(author=user).aggregate(count=Sum('users_count'))
            author_popular[user.last_name] = count['count']

        context = {
            "title": self.title,
            "category_list": category_list,
            "category_stat": category_stat,
            "author_stat": author_stat,
            "course_popular": course_popular,
            "author_popular": author_popular
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        self.popularity_statistic_generate()
        self.count_statistic_generate(User, AuthorStatistic)
        self.count_statistic_generate(Category, CategoryStatistic)
        return redirect(reverse("moderator:statistic"))


    @staticmethod
    def popularity_statistic_generate():
        courses = Course.objects.all()
        content_type = ContentType.objects.get_for_model(Course)
        for course in courses:
            obj_id = course.id
            author = course.author
            users_count = Cabinet.objects.filter(object_id=obj_id).count()
            statistic_obj, created = CoursePopularity.objects.get_or_create(content_type=content_type,
                                                                            object_id=obj_id,
                                                                            users_count=users_count,
                                                                            author=author)
            if not created:
                statistic_obj.users_count = users_count

    @staticmethod
    def count_statistic_generate(model, model_to_save):
        if model == User:
            # objects = model.objects.filter(groups__name__contains="authors")
            objects = model.objects.filter()
        elif model == Category:
            objects = Category.objects.all()

        content_type = ContentType.objects.get_for_model(model)

        for obj in objects:
            obj_id = obj.id
            course_count = obj.course_set.count()
            statistic_obj, created = model_to_save.objects.get_or_create(content_type=content_type,
                                                                         object_id=obj_id,
                                                                         course_count=course_count)
            if not created:
                statistic_obj.count = course_count

