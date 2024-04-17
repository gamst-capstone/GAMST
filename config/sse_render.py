from rest_framework.renderers import BaseRenderer

class ServerSentEventRenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'sse'
    charset = None
    content_type = 'text/event-stream'

    def render(self, data, media_type=None, renderer_context=None):
        return "data: {}\n\n".format(data)