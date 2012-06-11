import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_views.tests.models import Foo


class RESTViewTest(TestCase):
    urls = 'rest_views.tests.test_urls'

    def get_parsed_json_respone(self, response):
        return json.loads(response.content)

    def test_list(self):
        url = reverse("rest_views-foo-collection")
        response = self.client.get(url)
        parsed_content = self.get_parsed_json_respone(response)
        self.assertEqual(len(parsed_content["object_list"]), 20)
        self.assertTrue(parsed_content["not_all"])

        load_more_response = self.client.get(reverse("rest_views-foo-collection"), data={
            "exclude": list(Foo.objects.all()[:20].values_list("pk", flat=True))
        })

        parsed_lost_more_content = self.get_parsed_json_respone(load_more_response)
        self.assertEqual(len(parsed_lost_more_content["object_list"]), 5)
        self.assertFalse(parsed_lost_more_content["not_all"])

        self.assertEqual(Foo.objects.count(), 25)

    def test_create(self):
        foo = Foo.objects.all()[0]
        url = reverse("rest_views-foo-collection")
        response = self.client.put(url, data={
            "bar": 100,
            "name": "new_foo"
        })
        self.assertEqual(response.status_code, 405)
        response = self.client.post(url, data={
            "bar": 100,
            "name": "new_foo"
        })
        parsed_content = self.get_parsed_json_respone(response)
        self.assertDictEqual(parsed_content, {u'object': {u'bar': 100, u'name': u'new_foo'}})

    def test_details(self):
        foo = Foo.objects.all()[0]
        url = reverse("rest_views-foo-resource", args=[foo.pk])
        response = self.client.get(url)
        parsed_content = self.get_parsed_json_respone(response)
        self.assertDictEqual(parsed_content, {u'object': {u'bar': 1, u'name': u'foo1'}})

    def test_edit(self):
        foo = Foo.objects.all()[0]
        url = reverse("rest_views-foo-resource", args=[foo.pk])
        response = self.client.post(url, data={
            "bar": 100,
            "name": "changed foo1"
        })
        self.assertEqual(response.status_code, 405)
        response = self.client.put(url, data={
            "bar": 100,
            "name": "changed foo1"
        })
        parsed_content = self.get_parsed_json_respone(response)
        self.assertDictEqual(parsed_content, {u'object': {u'bar': 100, u'name': u'changed foo1'}})
        foo = Foo.objects.get(pk=foo.pk)
        self.assertEqual(foo.name, u'changed foo1')
        self.assertEqual(foo.bar, 100)

    def test_delete(self):
        foo = Foo.objects.all()[0]
        url = reverse("rest_views-foo-resource", args=[foo.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, '')
        self.assertFalse(Foo.objects.filter(pk=foo.pk).exists())
