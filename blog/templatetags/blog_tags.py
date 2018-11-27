from django import template

from blog.models import Course
from cabinets.models import Cabinet


register = template.Library()


@register.inclusion_tag('blog/recommended_courses.html')
def recommended_courses(user):
    user_cabinet_course_ids = list(user.cabinet_set.all().values_list('object_id', flat=True))
    user_cabinet_courses = Course.objects.filter(id__in=user_cabinet_course_ids)
    return {'user_cabinet_courses': user_cabinet_courses}
