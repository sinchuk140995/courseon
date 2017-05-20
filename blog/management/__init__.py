from django.contrib.auth.models import Permission, Group


def create_author_group():
    add_permission = Permission.objects.get(name="Can add course")
    author_group, created = Group.objects.get_or_create(name="authors")
    if created:
        author_group.permissions = [add_permission]
    return author_group
