#!/bin/bash
cd /var/www/ResFormPRO
source venv/bin/activate
export PYTHONPATH="/var/www/ResFormPRO:$PYTHONPATH"
export FLASK_APP=run.py
export FLASK_ENV=production
exec gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 \
    --access-logfile /var/www/ResFormPRO/logs/access.log \
    --error-logfile /var/www/ResFormPRO/logs/error.log \
    --log-level info \
    run:app
