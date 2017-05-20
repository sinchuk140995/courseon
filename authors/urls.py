from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import ApplicantView

urlpatterns = [
    url(r"^$", login_required(ApplicantView.as_view()), name="applicant"),
]
