# FCS

Site du FC Saucisse.

Utiliser `./manage.py collectstatic/migrate/createsuperuser` avant de déployer. Aussi `./manage.py tailwind install` (npm doit être installé). Et `python manage.py tailwind build`.

# TODO

* Résoudre le problème de timezone en l'intégrant à la DB et en ractivant use_tz
* https://django-tailwind.readthedocs.io/en/latest/docker.html déployer pour Docker