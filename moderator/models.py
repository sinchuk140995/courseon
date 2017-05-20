from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class BaseCountStat(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    course_count = models.IntegerField()


class AuthorStatistic(BaseCountStat):
    pass


class CategoryStatistic(BaseCountStat):
    pass


class CoursePopularity(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    users_count = models.IntegerField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)


# class CategoryStatistic(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#     course_count = models.IntegerField()
#
#
# class AuthorStatistic(CategoryStatistic):
#     pass


# class BasePopularityStat(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#     users_count = models.IntegerField()
#     author = models.ForeignKey(User, on_delete=models.CASCADE, null=True) # delete null=True
