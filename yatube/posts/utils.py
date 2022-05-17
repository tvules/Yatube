from django.shortcuts import redirect
from django.views.generic.detail import SingleObjectMixin


class AuthorRequiredMixin(SingleObjectMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect(obj)
        return super().dispatch(request, *args, **kwargs)
