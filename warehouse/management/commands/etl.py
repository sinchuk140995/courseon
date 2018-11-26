from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from blog import models as blog_models
from cabinets import models as cabinets_models
from warehouse import models


class Command(BaseCommand):
    help = 'Extract, transform and load a data to the warehouse'

    def handle(self, *args, **kwargs):
        last_cabinet_id = self.get_last_cabinet_id()
        cabinets = cabinets_models.Cabinet.objects.filter(id__gt=last_cabinet_id)

        for cabinet in cabinets:
            course = cabinet.content_object
            student = cabinet.user
            cabinet_date = cabinet.timestamp
            dim_category = self.get_or_create_dim_category(course.category)
            dim_author = self.get_or_create_dim_author(course.author)

            dim_course = models.DimCourse.objects.create(
                course_id=course.id,
                course_name=course.name,
                course_pub_date=course.pub_date,
                category=dim_category,
                author=dim_author,
                platform_name=course.platform_name,
                platform_url=course.platform_url,
            )

            dim_student = models.DimStudent.objects.create(
                student_id=student.id,
                student_username=student.username,
                student_first_name=student.first_name,
                student_last_name=student.last_name,
                student_email=student.email,
            )

            dim_date = models.DimDate.objects.create(
                date=cabinet_date.date(),
                day_of_week=cabinet_date.weekday(),
                month=cabinet_date.strftime('%B'),
                year=cabinet_date.year,
                month_of_year=cabinet_date.month,
                week_of_year=cabinet_date.isocalendar()[1],
                day_of_year=cabinet_date.timetuple().tm_yday,
            )

            students_count = cabinets_models.Cabinet.objects.filter(
                content_type=ContentType.objects.get_for_model(course),
                object_id=course.id,
            ).count()
            fact_cabinet = models.FactCabinet.objects.create(
                dim_course=dim_course,
                dim_student=dim_student,
                dim_date=dim_date,
                cabinet_id=cabinet.id,
                likes_count=course.likes.count(),
                students_count=students_count,
            )
            self.stdout.write("Saved: student {}'s course {}".format(student, course))
        else:
            self.stdout.write("New students cabinets wasn't found")


    @staticmethod
    def get_or_create_dim_category(category):
        try:
            dim_category = models.DimCategory.objects.get(category_id=category.id)
        except models.DimCategory.DoesNotExist:
            dim_category = models.DimCategory.objects.create(
                category_id=category.id,
                category_name=category.name,
            )

        return dim_category

    @staticmethod
    def get_or_create_dim_author(author):
        try:
            dim_author = models.DimAuthor.objects.get(author_id=author.id)
        except models.DimAuthor.DoesNotExist:
            dim_author = models.DimAuthor.objects.create(
                author_id=author.id,
                author_username=author.username,
                author_first_name=author.first_name,
                author_last_name=author.last_name,
                author_email=author.email,
            )

        return dim_author

    @staticmethod
    def get_last_cabinet_id():
        fact_cabinet = models.FactCabinet.objects.all().order_by('-cabinet_id').first()
        try:
            return fact_cabinet.cabinet_id
        except AttributeError:
            return 0
