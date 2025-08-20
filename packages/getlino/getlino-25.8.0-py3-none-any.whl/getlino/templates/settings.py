# -*- coding: UTF-8 -*-
{# # fmt: off #}

from {{app_settings_module}} import *
from {{local_prefix}}.settings import *


class Site(Site):
    title = "{{prjname}}"
    server_url = "{{server_url}}"
    {% if webdav -%}
    webdav_protocol = 'wdav'
    {%- endif %}
    {% if languages -%}
    languages = '{{languages}}'
    {%- endif %}
    default_ui = '{{front_end}}'
    show_internal_field_names = True
    log_each_action_request = False
    {% if asgi_server -%}
    use_systemd = True
    {%- endif %}

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        # example of local plugin settings:
        # yield ('periods', 'start_year', 2018)
        yield 'help', 'make_help_pages', True

SITE = Site(globals())

{% if site_domain == "localhost" -%}
DEBUG = True
# ALLOWED_HOSTS = ['{{server_domain}}']
{%- else -%}
DEBUG = False  # "{{server_domain}}"
ALLOWED_HOSTS = ['{{site_domain}}']
{%- endif %}

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
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        }
        {% endif -%}
    }
}

EMAIL_SUBJECT_PREFIX = '[{{prjname}}] '
