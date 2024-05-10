from rest_framework.renderers import BaseRenderer
from json import JSONEncoder
from datetime import datetime

class ServerSentEventRenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'sse'
    charset = None
    content_type = 'text/event-stream'

    def render(self, data, media_type=None, renderer_context=None):
        return "data: {}\n\n".format(data)
    

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)