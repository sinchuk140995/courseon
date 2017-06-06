from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "accounts"

urlpatterns = [
    url(r"^profile/update/$", login_required(views.ProfileManage.as_view()), name="profile_manage"),
    url(r"^profile/(?P<user>\w+)/$", login_required(views.ProfileView.as_view()), name="profile"),
]

