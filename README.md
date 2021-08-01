# FCS

Site du FC Saucisse.

Utiliser `./manage.py collectstatic/migrate/createsuperuser` et `./manage.py tailwind install` (npm doit être installé) avant de déployer. Aussi à chaque màj, `./manage.py migrate`, `./manage.py collectstatic` et `./manage.py tailwind build`.

# TODO

* Résoudre le problème de timezone en l'intégrant à la DB et en ractivant use_tz
* https://stackoverflow.com/questions/66971594/auto-create-primary-key-used-when-not-defining-a-primary-key-type-warning-in-dja Django 3.2
* https://www.tailwindtoolbox.com/components/accordion
