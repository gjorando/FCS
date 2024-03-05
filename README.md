# FCS

Site du FC Saucisse.

Utiliser `./manage.py collectstatic/migrate/createsuperuser` et `./manage.py tailwind install` (npm doit être installé) avant de déployer. Aussi à chaque màj, `./manage.py migrate`, `./manage.py collectstatic` et `./manage.py tailwind build`.

# TODO

* Intégrer aussi les statistiques avancées en optionel (Damage done/taken/healed, faciles à scraper sur uniteapi.dev)
* Trouver un moyen de bindmount settings\_production.py (Podman n'autorise pas le bindmount de fichier sous CentOS/Rhel/Fedora, peut-être bouger ce dossier dans un sous module et bind mount ce dernier?)
* Résoudre le problème de timezone en l'intégrant à la DB et en réactivant use\_tz
* https://stackoverflow.com/questions/66971594/auto-create-primary-key-used-when-not-defining-a-primary-key-type-warning-in-dja Django 3.2
* https://www.tailwindtoolbox.com/components/accordion
* Implémenter la mise en cache avec Redis
* Ne pas utiliser de CDN pour ChartJS
* Documentation
* Refactoriser (code plus compliant avec la dernière version de Django)
