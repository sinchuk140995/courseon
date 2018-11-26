from django.db import models

# from blog import models as blog_models


class FactCabinet(models.Model):
    dim_course = models.ForeignKey('DimCourse')
    dim_student = models.ForeignKey('DimStudent')
    dim_date = models.ForeignKey('DimDate')
    # required_date = models.DateTimeField(auto_now_add=True)
    cabinet_id = models.PositiveIntegerField()
    likes_count = models.PositiveIntegerField()
    students_count = models.PositiveIntegerField()


class DimAuthor(models.Model):
    author_id = models.PositiveIntegerField(primary_key=True)
    author_username = models.CharField(max_length=150)
    author_first_name = models.CharField(max_length=30)
    author_last_name = models.CharField(max_length=30)
    author_email = models.EmailField(blank=True)


class DimCategory(models.Model):
    category_id = models.PositiveIntegerField(primary_key=True)
    category_name = models.CharField(max_length=120)


class DimCourse(models.Model):
    course_id = models.PositiveIntegerField()
    course_name = models.CharField(max_length=120)
    course_pub_date = models.DateField()
    category = models.ForeignKey(DimCategory)
    author = models.ForeignKey(DimAuthor, null=True)
    platform_name = models.CharField(max_length=120, blank=True)
    platform_url = models.URLField(blank=True)


class DimStudent(models.Model):
    student_id = models.PositiveIntegerField()
    student_username = models.CharField(max_length=150)
    student_first_name = models.CharField(max_length=30)
    student_last_name = models.CharField(max_length=30)
    student_email = models.EmailField(blank=True)


class DimDate(models.Model):
    date = models.DateField()
    day_of_week = models.PositiveSmallIntegerField()
    month = models.CharField(max_length=16)
    year = models.PositiveSmallIntegerField()
    month_of_year = models.PositiveSmallIntegerField()
    week_of_year = models.PositiveSmallIntegerField()
    day_of_year = models.PositiveSmallIntegerField()
