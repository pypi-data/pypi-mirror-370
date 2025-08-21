import os
from pathlib import Path

site_resolver = Path(__file__).resolve()

PROJECT_DIR = site_resolver.parent.parent.parent.parent

HAYSTACK_ROUTERS = ['aldryn_search.router.LanguageRouter']
HAYSTACK_ENGINE = 'cms_qe.whoosh.backend.AnalyzerWhooshEngine'
_HAYSTACK_PATH = os.path.normpath(os.path.join(PROJECT_DIR, 'whoosh_index'))
HAYSTACK_CONNECTIONS = {
    'default': {'ENGINE': HAYSTACK_ENGINE, 'PATH': os.path.join(_HAYSTACK_PATH, 'default')},
    'en': {'ENGINE': HAYSTACK_ENGINE, 'PATH': os.path.join(_HAYSTACK_PATH, 'en')},
}
HAYSTACK_CUSTOM_HIGHLIGHTER = "cms_qe.haystack.highlighting.HaystackHighlighter"
