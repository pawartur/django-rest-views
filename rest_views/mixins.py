import httplib
import json
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import ModelFormMixin
from django.utils.translation import ugettext_lazy as _
from rest_views.forms import LoadMoreForm
from rest_views.helpers import CustomEncoder


__all__ = ["EnhancedModelFormMixin", "JSONMixin", "LoadMoreMixin"]


class EnhancedModelFormMixin(ModelFormMixin):
    def get_form_kwargs(self):
        kwargs = super(EnhancedModelFormMixin, self).get_form_kwargs()
        kwargs["data"] = self.request.POST if self._action == "create_object" else self.request.PUT
        return kwargs


class JSONMixin(object):
    def get_context_object_name(self, object_list):
        '''
        We don't want to get querysets or model objects serialized
        twice in our json responses
        '''
        return None

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(JSONMixin, self).dispatch(request, *args, **kwargs)
        except PermissionDenied, e:
            return HttpResponse(content=unicode(e), status=httplib.FORBIDDEN, mimetype="application/json")
        except Http404, e:
            return HttpResponse(content=unicode(e), status=httplib.NOT_FOUND, mimetype="application/json")

    def render_to_response(self, context={}, status=httplib.OK):
        if status in [httplib.NO_CONTENT, httplib.RESET_CONTENT]:
            content = ""
        else:
            content = json.dumps(context, cls=CustomEncoder)
        return HttpResponse(content=content, status=status, mimetype="application/json")


class LoadMoreMixin(object):
    load_more_form_class = LoadMoreForm
    limit = None

    def _get_qs_and_not_all_info(self, queryset):
        load_more_form = self.load_more_form_class(queryset=queryset, limit=self.limit, data=self.request.GET)
        if load_more_form.is_valid():
            return load_more_form.get_qs_and_not_all_info() 
        else:
            raise Http404(_("Wrong exclude query param given"))

    def _get_list_context_data(self, **kwargs):
        context = super(LoadMoreMixin, self)._get_list_context_data(**kwargs)
        context.pop("paginator")
        context.pop("page_obj")
        context.pop("is_paginated")

        if self.limit is None:
            return context
        
        queryset = context["object_list"]
        context["object_list"], context["not_all"] = self._get_qs_and_not_all_info(queryset)
        return context
