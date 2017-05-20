from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "comments"

urlpatterns = [
    url(r"^(?P<id>[\d]+)/$", views.CommentThread.as_view(), name="thread"),
    url(r"^(?P<id>[\d]+)/delete/$", login_required(views.CommentDelete.as_view()), name="delete"),
]
