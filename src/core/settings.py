"""generalised settings for the Lax project.

per-instance settings are in /path/to/app/app.cfg
example settings can be found in /path/to/lax/elife.cfg

./install.sh will create a symlink from dev.cfg -> lax.cfg if lax.cfg not found."""

import os
from os.path import join
from datetime import datetime
import ConfigParser as configparser
from pythonjsonlogger import jsonlogger
import yaml
from et3.render import render_item
from et3.extract import path as p

PROJECT_NAME = 'lax'

# Build paths inside the project like this: os.path.join(SRC_DIR, ...)
SRC_DIR = os.path.dirname(os.path.dirname(__file__)) # ll: /path/to/lax/src/
PROJECT_DIR = os.path.dirname(SRC_DIR) # ll: /path/to/lax/

CFG_NAME = 'app.cfg'
DYNCONFIG = configparser.SafeConfigParser(**{
    'allow_no_value': True,
    'defaults': {'dir': SRC_DIR, 'project': PROJECT_NAME}})
DYNCONFIG.read(join(PROJECT_DIR, CFG_NAME)) # ll: /path/to/lax/app.cfg

def cfg(path, default=0xDEADBEEF):
    lu = {'True': True, 'true': True, 'False': False, 'false': False} # cast any obvious booleans
    try:
        val = DYNCONFIG.get(*path.split('.'))
        return lu.get(val, val)
    except (configparser.NoOptionError, configparser.NoSectionError): # given key in section hasn't been defined
        if default == 0xDEADBEEF:
            raise ValueError("no value/section set for setting at %r" % path)
        return default
    except Exception as err:
        print 'error on %r: %s' % (path, err)

PRIMARY_JOURNAL = {
    'name': cfg('journal.name'),
    'inception': datetime.strptime(cfg('journal.inception'), "%Y-%m-%d")
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = cfg('general.secret-key')

DEBUG = cfg('general.debug')
assert isinstance(DEBUG, bool), "'debug' must be either True or False as a boolean, not %r" % (DEBUG, )

DEV, TEST, PROD = 'dev', 'test', 'prod'
ENV = cfg('general.env', DEV)

ALLOWED_HOSTS = cfg('general.allowed-hosts', '').split(',')

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_markdown2', # landing page is rendered markdown
    'explorer', # sql creation
    #'django_db_logger', # logs certain entries to the database

    'rest_framework',
    'rest_framework_swagger', # gui for api

    'publisher',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'core.middleware.KongAuthentication', # sets a header if it looks like an authenticated request
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(SRC_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': cfg('general.debug'),
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Testing
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_DIR = 'build'
TEST_OUTPUT_FILE_NAME = 'junit.xml'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': cfg('database.engine'),
        'NAME': cfg('database.name'),
        'USER': cfg('database.user'),
        'PASSWORD': cfg('database.password'),
        'HOST': cfg('database.host'),
        'PORT': cfg('database.port')
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(SRC_DIR, 'media')
STATIC_ROOT = os.path.join(PROJECT_DIR, 'collected-static')

STATICFILES_DIRS = (
    os.path.join(SRC_DIR, "static"),
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    #'DEFAULT_PERMISSION_CLASSES': [
    #    'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    #],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    #'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'publisher.negotiation.eLifeContentNegotiation',
    'DEFAULT_RENDERER_CLASSES': (
        'publisher.negotiation.ArticleListVersion1',
        'publisher.negotiation.POAArticleVersion1',
        'publisher.negotiation.VORArticleVersion1',
        'publisher.negotiation.ArticleHistoryVersion1',
        'rest_framework.renderers.JSONRenderer',
        #'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

SWAGGER_SETTINGS = {
    'api_version': '1',
    'exclude_namespaces': ['proxied'], # swagger docs are broken, but this gives them the right namespace
}

#
# sql explorer
#

EXPLORER_S3_BUCKET = cfg('general.reporting-bucket', None)

#
# API opts
#

SCHEMA_PATH = join(PROJECT_DIR, 'schema/api-raml/dist')
SCHEMA_IDX = {
    'poa': join(SCHEMA_PATH, 'model/article-poa.v1.json'),
    'vor': join(SCHEMA_PATH, 'model/article-vor.v1.json'),
    'history': join(SCHEMA_PATH, 'model/article-history.v1.json'),
    'list': join(SCHEMA_PATH, 'model/article-list.v1.json')
}
API_PATH = join(SCHEMA_PATH, 'api.raml')

def _load_api_raml(path):
    # load the api.raml file, ignoring any "!include" commands
    yaml.add_multi_constructor('', lambda *args: '[disabled]')
    return yaml.load(open(path, 'r'))['traits']['paged']['queryParameters']

API_OPTS = render_item({
    'per_page': [p('per-page.default'), int],
    'min_per_page': [p('per-page.minimum'), int],
    'max_per_page': [p('per-page.maximum'), int],

    'page_num': [p('page.default'), int],

    'order_direction': [p('order.default')],

}, _load_api_raml(API_PATH))

# KONG gateway options

KONG_AUTH_HEADER = 'KONG-Authenticated'
INTERNAL_NETWORK = '10.0.2.0/24'

#
# notification events
#

EVENT_BUS = {
    'region': cfg('bus.region'),
    'subscriber': cfg('bus.subscriber'),
    'name': cfg('bus.name'),
    'env': cfg('bus.env')
}

# Lax settings

# when ingesting an article version and the EIF has no 'update' value,
# should we fail and raise an error? if not, the article pub-date is used instead.
FAIL_ON_NO_UPDATE_DATE = cfg('ingest.fail-on-no-update-date', False)

LOG_NAME = '%s.log' % PROJECT_NAME # ll: lax.log
LOG_FILE = join(PROJECT_DIR, LOG_NAME) # ll: /path/to/lax/log/lax.log

INGESTION_LOG_NAME = 'ingestion-%s.log' % PROJECT_NAME
INGESTION_LOG_FILE = join(PROJECT_DIR, INGESTION_LOG_NAME)

if ENV != DEV:
    LOG_FILE = join('/var/log/', LOG_NAME) # ll: /var/log/lax.log
    INGESTION_LOG_FILE = join('/var/log/', INGESTION_LOG_NAME) # ll: /var/log/lax.log

# whereever our log files are, ensure they are writable before we do anything else.
def writable(path):
    os.system('touch ' + path)
    # https://docs.python.org/2/library/os.html
    assert os.access(path, os.W_OK), "file doesn't exist or isn't writable: %s" % path
map(writable, [LOG_FILE, INGESTION_LOG_FILE])

ATTRS = ['asctime', 'created', 'levelname', 'message', 'filename', 'funcName', 'lineno', 'module', 'pathname']
FORMAT_STR = ' '.join(map(lambda v: '%(' + v + ')s', ATTRS))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'json': {
            '()': jsonlogger.JsonFormatter,
            'format': FORMAT_STR,
        },
        'brief': {
            'format': '%(levelname)s - %(message)s'
        },
    },

    'handlers': {
        # entries go to standard lax.log file
        'lax.log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'json',
        },

        # entries go to stderr
        'stderr': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
        },

        # entries go to the lax-ingestion.log file
        'ingestion.log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': INGESTION_LOG_FILE,
            'formatter': 'json',
        },

        # entries go to the database
        # incomplete. I need the django-db-logger a little bit cleverer first
        #'database': {
        #    'level': 'DEBUG',
        #    'class': 'django_db_logger.db_log_handler.DatabaseLogHandler',
        #    'formatter': 'json',
        #},
    },

    'loggers': {
        '': {
            'handlers': ['stderr', 'lax.log'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['lax.log'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

module_loggers = [
    'publisher.eif_ingestor',
    'publisher.ejp_ingestor',
    'publisher.ajson_ingestor',
    'publisher.management.commands.import',
    'publisher.management.commands.ingest',
]
logger = {
    'level': 'INFO',
    #'handlers': ['database', 'ingestion.log', 'lax.log', 'stderr'],
    'handlers': ['ingestion.log', 'lax.log', 'stderr'],
    'propagate': False, # don't propagate up to root logger
}
LOGGING['loggers'].update(dict(zip(module_loggers, [logger] * len(module_loggers))))
