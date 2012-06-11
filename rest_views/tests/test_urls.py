from django.conf.urls.defaults import *

from rest_views.tests.models import Foo
from rest_views.tests.forms import FooForm
from rest_views.views import JSONRestView

urlpatterns = patterns('',
    url(r'^foos/$', JSONRestView.as_view(model=Foo, form_class=FooForm, limit=20), name="rest_views-foo-collection"),
    url(r'^foos/(?P<pk>\d+)/$', JSONRestView.as_view(model=Foo, form_class=FooForm), name="rest_views-foo-resource"),
)
