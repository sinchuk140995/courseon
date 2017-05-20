from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType

from comments.models import Comment
from cabinets.models import Cabinet


class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)
    logotype = models.URLField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Course(models.Model):
    name = models.CharField(max_length=30)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    slug = models.SlugField(unique=True)
    course_url = models.URLField("url", max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    logotype = models.URLField()
    describe = models.TextField()
    pub_date = models.DateField("date published", auto_now_add=True, auto_now=False)
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
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = sender.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(sender, instance, new_slug=new_slug)
    return slug


def pre_save_instance_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(sender, instance)

pre_save.connect(pre_save_instance_receiver, sender=Category)
pre_save.connect(pre_save_instance_receiver, sender=Course)
