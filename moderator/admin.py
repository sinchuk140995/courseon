from django.contrib import admin

from .models import (CategoryStatistic,
                     AuthorStatistic,
                     CoursePopularity,
                     )

admin.site.register(CategoryStatistic)
admin.site.register(AuthorStatistic)
admin.site.register(CoursePopularity)
