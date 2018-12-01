from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType

import csv

from blog import forms as blog_forms
from blog import models as blog_models
from cabinets import models as cabinets_models


class Command(BaseCommand):
    help = 'Export courses, students and cabinets from CSV format'

    def handle(self, *args, **kwargs):
        with open(kwargs['CSV file path']) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print('Column names are {}'.format(", ".join(row)))
                    line_count += 1
                else:
                    code_module = row[0]
                    try:
                        category = blog_models.Category.objects.get(name=code_module)
                    except blog_models.Category.DoesNotExist:
                        category_form = blog_forms.CategoryForm({"name": code_module})
                        if category_form.is_valid():
                            category = category_form.save()
                        else:
                            print('Category Error:')
                            for key, value in category_form.errors.items():
                                print('\t{}: {}'.format(key, value))
                            continue

                    code_presentation = row[1]
                    try:
                        course = blog_models.Course.objects.get(
                            name='{} {}'.format(code_module, code_presentation)
                        )
                    except blog_models.Course.DoesNotExist:
                        course_form = blog_forms.CourseForm({
                            "name": '{} {}'.format(code_module, code_presentation),
                            "category": category.id,
                            "course_url": 'https://{}.com'.format(code_module),
                            "describe": 'Description of {} is {}'.format(code_module, code_presentation),
                        })
                        if course_form.is_valid():
                            course = course_form.save()
                        else:
                            print('Course Error:')
                            for key, value in course_form.errors.items():
                                print('\t{}: {}'.format(key, value))
                            continue

                    id_student = row[2]
                    # gender = row[3]
                    # region = row[4]
                    # highest_education = row[5]
                    # imd_band = row[6]
                    # age_band = row[7]
                    # num_of_prev_attempts = row[8]
                    # studied_credits = row[9]
                    # disability = row[10]
                    # final_result = row[11]
                    try:
                        user = get_user_model().objects.get(username=id_student)
                    except get_user_model().DoesNotExist:
                        user_creation_form = UserCreationForm({
                            'username': id_student,
                            'password1': 'Password123',
                            'password2': 'Password123',
                        })
                        if user_creation_form.is_valid():
                            user = user_creation_form.save()
                        else:
                            print('User Error:')
                            for key, value in user_creation_form.errors.items():
                                print('\t{}: {}'.format(key, value))
                            continue

                    try:
                        cabinet = cabinets_models.Cabinet.objects.create(
                            user=user,
                            content_type=ContentType.objects.get_for_model(course),
                            object_id=course.id,
                        )
                    except Exception as e:
                        print('Cabinet error: ' + e)

                    # print('\t{} works in the {} department, and was born in {}.'.format(row[0], row[1], row[2]))
                    line_count += 1
                    print('Created cabinet {}.'.format(cabinet))
            print('Processed {} lines.'.format(line_count))

    def add_arguments(self, parser):
        parser.add_argument('CSV file path', type=str)
