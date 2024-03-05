from lib.microdot import Response
from lib.microdot.utemplate import Template

from config import conf


async def index(request):
    return Template('../templates/index.html').render(infos=conf)
