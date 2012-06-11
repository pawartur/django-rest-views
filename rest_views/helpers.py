import abc
import json
import datetime
from django.db import models
from django.utils.timezone import is_aware, localtime


__all__ = ["CustomEncoder"]


class EncodableResource(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def __subclasshook__(cls, other_cls):
        if cls is EncodableResource and hasattr(other_cls, "dict_repr"):
            return True
        return NotImplemented


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, EncodableResource):
            return obj.dict_repr
        if isinstance(obj, datetime.datetime):
            if is_aware:
                return localtime(obj).strftime('%Y-%m-%d %H:%M')
            return obj.strftime('%Y-%m-%d %H:%M')
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, models.query.QuerySet):
            return list(obj)
        return super(CustomEncoder, self).default(obj)
