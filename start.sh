rm -rf static
python3 manage.py collectstatic
celery -A base worker -l info