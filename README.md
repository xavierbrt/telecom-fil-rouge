# Projet fil rouge

## Notebooks

* **clean-bird-csv.ipynb** : Ce notebook permet de pré-processer les fichiers contenant les traces GPS des oiseaux ; fichiers issus de Movebank. On enlève notamment les colonnes que l'on utilisera pas et on supprimer les oiseaux qui ne migrent pas.
* **compute-gps-surface.ipynb** : Ce notebook calcule les surfaces couvertes par les oiseaux d'un fichier de tracking GPS provenant de Movebank. On calcule ces surfaces selon une certaine granularité temporelle (par année par défaut). L'objectif est de savoir quels seront les besoins en données météo pour couvrir les traces GPS de ces oiseaux.
* **explore-bird-csv.ipynb** : Ce notebook permet d'explorer des traces GPS d'oiseaux d'un fichier de données provenant de Movebank. L'exploration de ces traces GPS donne des informations sur le type de traces GPS que nous avons (nombre d'oiseaux, répartitions dans le temps, positions, vitesses, directions, etc.). Ce notebook est utile pour voir les périodes de migrations d'un oiseau et ainsi réduire la plage de données météo nécessaires, sur les dates de migration.


## TODO

**Notes**: pour nos modèles il faudra penser à changer les types de données (ex: float64 -> float32) pour économiser de la mémoire

## Illustrations

![png](images/trace_gps.png)

![png](images/distances2_3jours.png)

![png](images/distances_3jours.png)