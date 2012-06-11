import httplib
from django import http
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import MultipleObjectMixin
from rest_views.mixins import EnhancedModelFormMixin, JSONMixin, LoadMoreMixin
  

class BaseRESTView(EnhancedModelFormMixin, MultipleObjectMixin, View):
    def _fix_put_request(self, request):
        request.method = "POST"
        request._load_post_and_files()
        request.method = "PUT"
        request.PUT = request.POST
        request.POST = http.QueryDict('', encoding=request._encoding)
        return request

    def dispatch(self, request, *args, **kwargs):
        self._action = None
        # For django "PUT" requests are "POST" request
        # with empty content (but properly set content-lenght)
        if request.method == "PUT":
            request = self._fix_put_request(request)
        return super(BaseRESTView, self).dispatch(request, *args, **kwargs)

    def currently_available_methods(self, without=None):
        test = lambda m: hasattr(self, m) if without is None else lambda m: hasattr(self, m) and m not in without
        return filter(test, self.http_method_names)

    def get(self, request, *args, **kwargs):
        if self.pk_url_kwarg in kwargs:
            self._action = "get_object"
            return self.get_single(request, *args, **kwargs)
        self._action = "get_object_list"
        return self.get_list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.pk_url_kwarg in kwargs:
            return http.HttpResponseNotAllowed(self.currently_available_methods(without=("post")))
        self._action = "create_object"
        self.object = None
        return self._process_form_action()

    def put(self, request, *args, **kwargs):
        if self.pk_url_kwarg not in kwargs:
            return http.HttpResponseNotAllowed(self.currently_available_methods(without=("put")))
        self._action = "update_object"
        self.object = self.get_object()
        return self._process_form_action()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.render_to_response({}, status=httplib.NO_CONTENT)

    def get_single(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_list(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        if self._action == "get_object_list":
            return self._get_list_context_data(**kwargs)
        else:
            return self._get_single_context_data(**kwargs)

    def _process_form_action(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def _get_single_context_data(self, **kwargs):
        context = kwargs
        context_object_name = self.get_context_object_name(self.object)
        if context_object_name:
            context[context_object_name] = self.object
        return context

    def _get_list_context_data(self, **kwargs):
        queryset = kwargs.pop('object_list')
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            }
        context.update(kwargs)
        if context_object_name is not None:
            context[context_object_name] = queryset
        return context


class RESTView(TemplateResponseMixin, BaseRESTView):
    success_url = None
    create_success_url = None
    update_success_url = None
    delete_success_url = None

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        if self._action == "delete_object":
            return self.get_delete_success_url()
        if self._action == "update_object":
            return self.get_update_success_url()
        if self._action == "create_object":
            return self.get_create_success_url()           

    def get_update_success_url(self):
        if self.update_success_url:
            return self.update_success_url
        return self._get_absolute_url_form_object(self.object)

    def get_create_success_url(self):
        if self.create_success_url:
            return self.update_success_url
        return self._get_absolute_url_form_object(self.object)

    def get_delete_success_url(self):
        if self.delete_success_url:
            return self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url or delete_success_url.")

    def _get_absolute_url_form_object(self, object):
        try:
            object.get_absolute_url()
        except AttributeError:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")


class JSONRestView(JSONMixin, LoadMoreMixin, BaseRESTView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.render_to_response({}, status=httplib.NO_CONTENT)

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_response(self.get_context_data(object=self.object))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(errors=form.errors), status=httplib.BAD_REQUEST)
