web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn chatbot_project.wsgi --bind 0.0.0.0:$PORT --timeout 120 --log-level debug
