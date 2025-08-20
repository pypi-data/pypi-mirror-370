# Django settings.
import os
import json
from enum import Enum

import structlog

from django.core.serializers.json import DjangoJSONEncoder


PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Prague'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'cs'

LANGUAGES = [
    ('cs', 'czech'),
    ('en', 'english'),
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATE_FORMAT = 'j. E Y'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATICFILES_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_ROOT = STATICFILES_ROOT

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (

)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xe8vyy&0cw*&za++fq(%w6cx=)k53*m-@$1&pst=*oe(b#zgo+'


MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'security.middleware.LogMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # apps
    'django_celery_extensions',
    'security',
    'security.backends.sql.app.SecuritySQLBackend',
    'security.backends.logging.app.SecurityLoggingBackend',
    'security.backends.elasticsearch.app.SecurityElasticsearchBackend',
    'security.backends.testing.app.SecurityTestingBackend',
    'apps.test_security',
)


def _json_serializer(data, **kwargs):
    serialized_data = {}
    for k, v in data.items():
        if isinstance(v, Enum):
            serialized_data[k] = v.name
        else:
            serialized_data[k] = v
    return json.dumps(serialized_data, cls=DjangoJSONEncoder)


structlog.configure(
    processors=[
        structlog.processors.EventRenamer("message"),
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer(_json_serializer),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'security.input_request_logger': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'security.output_request': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'security.command': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'security.celery': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'security.task': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ]
        }
    }
]

CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'
CELERY_DEFAULT_QUEUE = 'default'

DJANGO_CELERY_EXTENSIONS_AUTO_GENERATE_TASKS_DJANGO_COMMANDS = {
    'check': {},
    'create_user': {},
}

SECURITY_ELASTICSEARCH_DATABASE = dict(
    hosts=[{'host': 'localhost', 'port': 9200}],
)
SECURITY_RAISE_WRITER_EXCEPTIONS = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
