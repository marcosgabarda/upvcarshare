#!/bin/sh
python3 manage.py compilemessages
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8888
