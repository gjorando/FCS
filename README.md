# FCS

Site du FC Saucisse.

Utiliser `./manage.py collectstatic/migrate/createsuperuser` et `./manage.py tailwind install` (npm doit être installé) avant de déployer. Aussi à chaque màj, `./manage.py migrate`, `./manage.py collectstatic` et `./manage.py tailwind build`.

# TODO

* Ajouter un booléen pour mentionner si le match s'est fini suite à un forfait
* Lister les saisons jouées pour la sélection de saison, et l'afficher dans l'interface de résultats (séparation par saison sur la page d'accueil, et affichage de la saison sur la page de game)
* Résoudre le problème de timezone en l'intégrant à la DB et en réactivant use_tz
* https://stackoverflow.com/questions/66971594/auto-create-primary-key-used-when-not-defining-a-primary-key-type-warning-in-dja Django 3.2
* https://www.tailwindtoolbox.com/components/accordion
* Implémenter la mise en cache avec Redis
* Ne pas utiliser de CDN pour ChartJS
