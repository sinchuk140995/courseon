from django.contrib import admin

from .models import Category, Course


class CourseModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "pub_date"]
    list_filter = ["category", "pub_date"]
    search_fields = ["name", "describe"]

    class Meta:
        model = Course


admin.site.register(Category)
admin.site.register(Course, CourseModelAdmin)
