from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "blog"

urlpatterns = [
    url(r"^$", views.IndexView.as_view(), name="index"),
    url(r"^create_category/$", login_required(views.CreateCategory.as_view()), name="create_category"),
    url(r"^create_course/$", login_required(views.CourseCreate.as_view()), name="create_course"),
    url(r"^search/", views.Search.as_view(), name="search"),
    url(r"^(?P<slug>[\w-]+)/$", views.CategoryView.as_view(), name="category"),
    url(r"^(?P<category>[\w-]+)/(?P<slug>[\w-]+)/$", views.CourseDetail.as_view(), name="course"),
    url(r"^(?P<category>[\w-]+)/(?P<slug>[\w-]+)/update/$", login_required(views.CourseUpdate.as_view()),
        name="course_update"),
    url(r"^(?P<category>[\w-]+)/(?P<slug>[\w-]+)/delete/$", login_required(views.CourseDelete.as_view()),
        name="course_delete"),
]
