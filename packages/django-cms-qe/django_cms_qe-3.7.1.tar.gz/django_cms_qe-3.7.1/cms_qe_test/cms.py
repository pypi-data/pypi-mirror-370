from cms import api
from cms.models import Placeholder
from cms.plugin_rendering import ContentRenderer
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from sekizai.context import SekizaiContext


def render_plugin(plugin, path='/', **data):
    placeholder = Placeholder.objects.create(slot='test')
    model_instance = api.add_plugin(placeholder, plugin, 'en', **data)
    request = generate_get_request(path)
    renderer = ContentRenderer(request=request)
    context = SekizaiContext()
    context.update({'request': request, })
    html = renderer.render_plugin(model_instance, context)
    return html


def generate_get_request(path):
    request = RequestFactory().get(path)
    request.user = AnonymousUser()
    request.session = {}
    return request


def generate_post_request(path='', body=None):
    request = RequestFactory().post(path, body)
    request.user = AnonymousUser()
    request.session = {}
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request


# pylint: disable=dangerous-default-value
def create_page(title, language='en', page_params={}):
    page_params.setdefault('published', True)
    page_params.setdefault('overwrite_url', page_params.get('slug'))
    return api.create_page(title, 'cms_qe/home.html', language, **page_params)


# pylint: disable=dangerous-default-value
def create_text_page(title, language='en', page_params={}, plugin_params={}):
    plugin_params.setdefault('body', 'shello')
    page = create_page(title, language, page_params)
    placeholder = page.placeholders.get(slot='content')
    api.add_plugin(placeholder, 'TextPlugin', language, **plugin_params)
    return page
