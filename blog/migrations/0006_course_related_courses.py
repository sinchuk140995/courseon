# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-11-27 11:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20181126_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='related_courses',
            field=models.ManyToManyField(related_name='_course_related_courses_+', to='blog.Course'),
        ),
    ]
