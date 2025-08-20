# -*- coding: UTF-8 -*-
from {{app_settings_module}} import *
from {{local_prefix}}.settings import *

{% if site_domain == "localhost" %}
DEBUG = True
# ALLOWED_HOSTS = ['{{server_domain}}']
{% else %}
DEBUG = False  # "{{server_domain}}"
ALLOWED_HOSTS = ['{{site_domain}}']
{% endif %}

SECRET_KEY = '{{secret_key}}'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{{db_engine}}',
        'NAME': '{{db_name}}',
        {%- if db_engine != "sqlite3" %}
            'USER': '{{db_user}}',
            'PASSWORD': '{{db_password}}',
            'HOST': '{{db_host}}',
            'PORT': {{db_port}},
        {% endif -%}
        {%- if db_engine == "mysql" %}
        'OPTIONS': {
           "init_command": "SET default_storage_engine=MyISAM",
        }
        {% endif -%}
    }
}

EMAIL_SUBJECT_PREFIX = '[{{prjname}}] '
