import os
import sys
import site

site.addsitedir('/var/www/envs/example/lib/python2.6/site-packages')

sys.path.append('/var/www/django')
sys.path.append('/var/www/django/example)

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
