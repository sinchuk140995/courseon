from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, pre_delete
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max

from comments.models import Comment
from cabinets.models import Cabinet
from .utils import transliterate


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    logo_url = models.URLField(default="http://res.cloudinary.com/dzmnskqms/image/upload/v1495731762/unknown_swxwii.png")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Course(models.Model):
    name = models.CharField(max_length=120, unique=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    slug = models.SlugField(unique=True)
    course_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    logo_url = models.URLField(default="http://res.cloudinary.com/dzmnskqms/image/upload/v1495731762/unknown_swxwii.png")
    describe = models.TextField()
    pub_date = models.DateField("date published", auto_now_add=True, auto_now=False)
    platform_name = models.CharField(max_length=120, null=True)
    platform_url = models.URLField(null=True)
    check_status = models.NullBooleanField(default=None)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            "category": self.category.slug,
            "slug": self.slug
        }
        return reverse("blog:course", kwargs=kwargs)

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance)
        return content_type

    def is_subscribed(self, user):
        instance = self
        content_type = instance.get_content_type
        obj_id = instance.id
        try:
            cabinet = Cabinet.objects.get(content_type=content_type,
                                          object_id=obj_id,
                                          user=user)
            print(cabinet)
            return cabinet
        except Cabinet.DoesNotExist:
            return False


def create_slug(sender, instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)
    try:
        obj = sender.objects.get(slug=slug)
        new_slug = "%s-%s" % (slug, obj.id)
        return create_slug(sender, instance, new_slug=new_slug)
    except sender.DoesNotExist:
        if slug is None or slug == "":
            slug = int(sender.objects.all().aggregate(Max(id))) + 1
        return slug


def pre_save_instance_receiver(sender, instance, *args, **kwargs):
    if instance.slug is None or instance.slug == "":
        name = instance.name.lower()
        translit_name = transliterate(name)
        if not translit_name:
            translit_name = name
        new_slug = slugify(translit_name)
        instance.slug = create_slug(sender, instance, new_slug=new_slug)

pre_save.connect(pre_save_instance_receiver, sender=Category)
pre_save.connect(pre_save_instance_receiver, sender=Course)


def target_cleanup(target, instance, *args, **kwargs):
    qs = target.objects.filter(object_id=instance.id,
                               content_type=instance.get_content_type
                               )
    if qs:
        qs.delete()


def course_relate_clean(sender, instance, *args, **kwargs):
    target_cleanup(Cabinet, instance)
    target_cleanup(Comment, instance)

pre_delete.connect(course_relate_clean, sender=Course)
pre_delete.connect(course_relate_clean, sender=Course)
