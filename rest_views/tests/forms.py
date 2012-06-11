from django import forms
from rest_views.tests.models import Foo

class FooForm(forms.ModelForm):

    class Meta:
        model = Foo
