"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r"^$", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r"^$", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r"^blog/", include("blog.urls"))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls import (
                            handler400,
                            handler403,
                            handler404,
                            handler500
                            )

from accounts.views import (Login, Logout, Register)

urlpatterns = [
    url(r"^login/", Login.as_view(), name="login"),
    url(r"^logout/$", Logout.as_view(), name="logout"),
    url(r"^register/$", Register.as_view(), name="register"),
    url(r"^admin/", admin.site.urls),
    url(r"^author/", include("authors.urls")),
    url(r"^cabinet/", include("cabinets.urls")),
    url(r"^comments/", include("comments.urls")),
    url(r"^moderator/", include("moderator.urls")),
    url(r"^", include("blog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = 'blog.views.bad_request'
handler403 = 'blog.views.permission_denied'
handler404 = 'blog.views.page_not_found'
handler500 = 'blog.views.server_error'
