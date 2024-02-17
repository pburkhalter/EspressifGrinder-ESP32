from lib.microdot import Response
from lib.microdot.utemplate import Template


Response.default_content_type = 'text/html'


async def index(request):
    return Template('../templates/index.html').render(name=name)
