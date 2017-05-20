from django.conf.urls import url

from .views import (ApplicantList,
                    ApplicantView,
                    AcceptApplicant,
                    DeclineApplicant,
                    StatisticsView)

app_name = "moderator"

urlpatterns = [
    url(r"^$", ApplicantList.as_view(), name="applicants_list"),
    url(r"^statistics/$", StatisticsView.as_view(), name="statistic"),
    url(r"^applicants/(?P<slug>[\w-]+)/$", ApplicantView.as_view(), name="applicant_view"),
    url(r"^applicants/(?P<slug>[\w-]+)/accept/$", AcceptApplicant.as_view(), name="accept"),
    url(r"^applicants/(?P<slug>[\w-]+)/decline/$", DeclineApplicant.as_view(), name="decline"),
]
