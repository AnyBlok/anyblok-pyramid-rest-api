from pyramid.renderers import JSON
from datetime import datetime
import pytz
import time
from uuid import UUID


def datetime_adapter(obj, request):
    if obj is not None:
        if obj.tzinfo is None:
            timezone = pytz.timezone(time.tzname[0])
            obj = timezone.localize(obj)
    return obj.isoformat()

def uuid_adapter(obj, request):
    return str(obj.hex)

def largebinary_adapter(obj, request):
    return str(obj.encode('utf-8'))

def declare_json_data_adapter(config):
    json_renderer = JSON()
    json_renderer.add_adapter(datetime, datetime_adapter)
    json_renderer.add_adapter(UUID, uuid_adapter)
    json_renderer.add_adapter(bytes, largebinary_adapter)
    config.add_renderer('json', json_renderer)
