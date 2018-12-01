from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apyori import apriori

from blog import models as blog_models
from warehouse import models as warehouse_models


class Command(BaseCommand):
    help = 'Implement association rule mining for courses using the algorithm Apriori'

    def handle(self, *args, **kwargs):
        fact_cabinet_list = list()
        for student_id in get_user_model().objects.values_list('id', flat=True):
            fact_cabinet_list.append(list(
                warehouse_models.FactCabinet.objects
                .filter(dim_student__student_id=student_id)
                .values_list('dim_course__course_name', flat=True)[:1000]
            ))

        # print(fact_cabinet_list)
        # association_rules = apriori(fact_cabinet_list, min_support=0.0045, min_confidence=0.2, min_lift=1.5, min_length=2)
        association_rules = apriori(
            fact_cabinet_list,
            min_support=0.0045,
            min_confidence=0.2,
            min_lift=3,
            min_length=2,
        )
        association_results = list(association_rules)

        if len(association_results):
            for item in association_results:
                # first index of the inner list
                # Contains base item and add item
                pair = item[0]
                items = [x for x in pair]
                print("Rule: " + items[0] + " -> " + items[1])

                # second index of the inner list
                print("Support: " + str(item[1]))

                # third index of the list located at 0th
                # of the third index of the inner list

                print("Confidence: " + str(item[2][0][2]))
                print("Lift: " + str(item[2][0][3]))
                print("=====================================")

                course = blog_models.Course.objects.get(name=items[0])
                related_course = blog_models.Course.objects.get(name=items[1])
                course.related_courses.add(related_course)
