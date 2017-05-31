from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "cabinets"

urlpatterns = [
    url(r"^$", login_required(views.CabinetView.as_view()), name="index"),
    url(r"^certificates/$", login_required(views.CertificateList.as_view()), name="certificates"),
    url(r"^certificate/(?P<slug>[\w-]+)$",
        login_required(views.CertificateUpload.as_view()),
        name="certificate_upload"),
    url(r"^cabinet/(?P<slug>[\w-]+)/unsubscribe/$",
        login_required(views.CourseUnsubscribe.as_view()),
        name="course_unsubscribe"),
]
