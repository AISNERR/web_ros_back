#!/bin/sh

# python manage.py flush --no-input

python manage.py migrate
python manage.py loaddata pub_review_actions
python manage.py loaddata status_types
python manage.py loaddata events_formats
python manage.py loaddata events_types
python manage.py loaddata subjects
python manage.py loaddata tags
python manage.py loaddata rss_catalog_groups
python manage.py loaddata rss_catalog_data
python manage.py loaddata layer_groups
python manage.py loaddata layer_types
python manage.py loaddata services
python manage.py loaddata layer_view_set
python manage.py loaddata sci_pub_sources
python manage.py loaddata sci_pub_types
python manage.py loaddata project_types
python manage.py loaddata sci_pop_formats

exec "$@"