from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


def upload_certificate_location(instance, filename):
    return "certificates/%s/%s" % (instance.user, filename)


class CabinetManager(models.Manager):
    def filter_by_user(self, user):
        qs = super(CabinetManager, self).filter(user=user)
        return qs


class Cabinet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    timestamp = models.DateTimeField("subscribe date", auto_now_add=True)
    is_passed = models.NullBooleanField()
    certificate = models.URLField()
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    is_subscribe = models.BooleanField(default=True)

    objects = CabinetManager()

    def __str__(self):
        return self.user.last_name
