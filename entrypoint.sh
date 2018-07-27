#!/bin/bash

./wait-for-it.sh db:5432 -- echo "Creating config file"

if [ ! -f manage.py ]; then
  cd bag-repository
fi

if [ ! -f ursa_major/config.py ]; then
    cp ursa_major/config.py.example ursa_major/config.py
fi

echo "Apply database migrations"
python manage.py migrate

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8005
