from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Comment
from .forms import CommentForm


@method_decorator(login_required, name="post")
class CommentThread(View):
    template_name = "comments/thread.html"
    title = "Вітка"

    def get(self, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs["id"])
        initial_data = {
            "content_type": comment.content_type,
            "object_id": comment.id,
        }
        comment_form = CommentForm(initial=initial_data)
        context = {
            "title": self.title,
            "comment": comment,
            "comment_form": comment_form,
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        comment_form = CommentForm(self.request.POST)
        if comment_form.is_valid() and self.request.user.is_authenticated():
            c_type = comment_form.cleaned_data.get("content_type")
            content_type = ContentType.objects.get(model=c_type)
            obj_id = comment_form.cleaned_data.get("object_id")
            text = comment_form.cleaned_data.get("text")
            parent_obj = None
            try:
                parent_id = int(self.request.POST.get("parent_id"))
            except KeyError:
                parent_id = None

            parent_obj = get_object_or_404(Comment, pk=parent_id)

            new_comment, created = Comment.objects.get_or_create(
                                    user=self.request.user,
                                    content_type=content_type,
                                    object_id=obj_id,
                                    text=text,
                                    parent=parent_obj
                                )
            return redirect(parent_obj.get_absolute_url())
        else:
            return redirect(reverse("blog:index"))


class CommentDelete(View):
    template_name = "comments/confirm_delete.html"
    title = "Видалення коментаря"

    def get(self, *args, **kwargs):
        comment_obj = get_object_or_404(Comment, pk=kwargs['id'])

        if comment_obj.user != self.request.user:
            response = HttpResponse("Недостатньо прав.")
            response.status_code = 403
            return response

        context = {
            "title": self.title,
            "comment": comment_obj,
        }

        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['id'])

        if comment.user != self.request.user:
            messages.error(self.request, "Видалення не доступне.")
            raise Http404

        if comment.content_object is None:
            parent_obj_url = comment.parent.content_object.get_absolute_url()
        else:
            parent_obj_url = comment.content_object.get_absolute_url()

        comment.delete()
        messages.success(self.request, "Коментар видалено.")
        return redirect(parent_obj_url)
