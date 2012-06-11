from django.db import models


class Foo(models.Model):
    name = models.CharField(max_length=100)
    bar = models.IntegerField()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def dict_repr(self):
        return {
            "name": self.name,
            "bar": self.bar,
        }
