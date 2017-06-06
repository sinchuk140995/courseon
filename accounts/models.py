from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.CharField(max_length=120)
    faculty = models.CharField(max_length=120, null=True) # delete null=True
    social_link = models.URLField(null=True)
    describe = models.TextField()

    def get_absolute_url(self):
        kwargs = {
            "user": self.user.username,
        }
        return reverse("accounts:profile", kwargs=kwargs)
