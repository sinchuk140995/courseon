from django.contrib.auth.models import Group, Permission


author_group, created = Group.objects.get_or_create(Group, name="authors")
if created:
    add_permission = Permission.objects.get(name="Can add course")
    author_group.permissions = [add_permission]