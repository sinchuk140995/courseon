from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class CabinetManager(models.Manager):
    def filter_by_user(self, user):
        qs = super(CabinetManager, self).filter(user=user)
        return qs


class Cabinet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    timestamp = models.DateTimeField("subscribe_date", auto_now_add=True)
    is_passed = models.BooleanField(default=False)

    objects = CabinetManager()

    def __str__(self):
        return self.user.last_name


class Certificate(models.Model):
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE)
    url = models.URLField()
    type = models.CharField(max_length=30)
    public_id = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField("upload_date", auto_now_add=True)
