import setuptools


setuptools.setup(
    name='django-cms-qe',
    version='3.7.1',
    packages=setuptools.find_packages(exclude=[
        '*.tests',
        '*.tests.*',
        'tests.*',
        'tests',
        'test_utils.*',
        'test_utils',
        '*.migrations',
        '*.migrations.*',
    ]),
    include_package_data=True,
    description=(
        'Django CMS Quick & Easy provides all important modules to run new page without'
        'a lot of coding. Aims to do it very easily and securely.'
    ),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://websites.pages.nic.cz/django-cms-qe',
    author='CZ.NIC, z.s.p.o.',
    author_email='kontakt@nic.cz',
    license='BSD License',

    python_requires='>=3.9',  # https://docs.python.org/3.9/library/typing.html#module-contents
    install_requires=[
        # Restrict Django version because cms 3.11 doesn't have it and it's not compatible with 5.0. This version
        # throuws exception ImportError: cannot import name 'get_storage_class' from 'django.core.files.storage'
        # in cms/utils/__init__.py
        'django~=4.2',
        'django-cms~=3.11',
        'easy-thumbnails[svg]~=2.10',
        'djangocms-frontend~=1.1',  # https://github.com/django-cms/djangocms-frontend/blob/1.1.4/setup.py#L6-L15
        'django-csp~=3.7',
        'djangocms-picture~=4.0',
        'django-axes~=6.0',
        'django-constance[database]~=2.9',
        'djangocms-file~=3.0',
        'django-import-export~=3.2',
        'django-mail-queue==3.2.5',  # Fix TypeError: FileField.storage must be a subclass/instance of django.core.files.storage.base.Storage
        'djangocms-icon~=2.0',
        'djangocms-googlemap~=2.0',
        'django-tablib~=3.2',  # Used by cms_qe/export.py
        'mailchimp3~=3.0',
        'argon2-cffi~=21.3',
        'djangocms-aldryn-forms[captcha]~=7.7',
        'djangocms-aldryn-search~=2.0',
        'django-haystack~=3.2',
        'pymemcache~=4.0',
        'whoosh~=2.7',
        'djangorestframework~=3.16',
        'markdown~=3.8',
        'django-filter~=25.1',
        'django-rest-knox~=5.0',
        'drf-spectacular~=0.28',
    ],
    # Do not use test_require or build_require, because then it's not installed and is
    # able to be used only by setup.py util. We want to use it manually.
    # Actually it could be all in dev-requirements.txt but it's good to have it here
    # next to run dependencies and have it separated by purposes.
    extras_require={
        'dev': [
            'django-debug-toolbar~=4.1',
            'django-extensions~=3.2',
        ],
        'test': [
            'flake8',
            'isort',
            'mypy',
            'pylint',
            'pylint-django',
            'pytest~=6.2',
            'pytest-data~=0.4',
            'pytest-django~=3.9',
            'pytest-env~=0.6',
            'pytest-pythonpath~=0.7',
            'pytest-sugar~=0.9',
            'pytest-watch~=4.2',
            'PyVirtualDisplay~=1.3',
            'webdriverwrapper~=2.8',
            'django-simple-captcha~=0.5',
            'testfixtures',
            'tzdata',
        ],
        'build': [
            'Jinja2<3.1.0',
            'Sphinx==1.8.5',
        ],
        'psql': [
            'psycopg2',
        ],
        'mysql': [
            'mysqlclient~=2.2',
        ],
        'newsblog': [
            'djangocms-aldryn-newsblog~=3.3',
        ]
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords=['django', 'cms'],
)
