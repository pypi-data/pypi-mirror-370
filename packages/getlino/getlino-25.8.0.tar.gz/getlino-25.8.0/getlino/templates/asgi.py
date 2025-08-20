import os, sys
{% if python_path %}
sys.path.insert(0, '{{python_path}}')
{% endif %}
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{django_settings_module}}")
from lino.modlib.linod.routing import application
