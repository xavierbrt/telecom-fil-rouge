# Projet fil rouge

## Notebooks

### Préprocesser les fichiers des traces GPS individuellement
* **1-clean-bird-csv** : Ce notebook permet de pré-processer les fichiers contenant les traces GPS des oiseaux ; fichiers issus de Movebank. Il enlève 
 les colonnes que l'on utilisera pas et supprime les oiseaux qui ne migrent pas.

* **2-clean-migration-periods** : Ce notebook permet d'extraire d'un fichier de points GPS, les points GPS qui sont au cours d'une migration.<br />

* **3-compute-gps-surface** : Ce notebook calcule les surfaces couvertes par les oiseaux d'un fichier de tracking GPS provenant de Movebank. 

> Ces notebooks ont chacun un équivalent en **scripts python**, qui permet d'appliquer les mêmes opérations que les notebooks mais sur tous les fichiers présents dans un dossier en une seule exécution.

### Rassembler ces fichiers
* **4-concatenate-bird** : Ce notebook permet de concaténer plusieurs fichiers *bird csv*, après qu'ils aient chacun été cleanés par le notebook *2-clean-migration-periods*.

* **5-concatenate-gps-surface** : Ce notebook permet de concaténer plusieurs fichiers *migrations*, après qu'ils aient été produits par le notebook *3-compute-gps-surface*.

* **6-summarize-all-gps-surface** : Ce notebook calcule les périodes de migration par semestre et par année. Ces périodes proviennent du csv produit par le notebook *5-concatenate-gps-surface*.

### Exploration des données
* **explore-bird-csv** : Ce notebook permet d'explorer des traces GPS d'oiseaux d'un fichier de données provenant de Movebank. 

* **explore-weather-data** : Ce notebook permet d'explorer des fichiers au format netCDF4 contenant des données météo.


## TODO

**Notes**: pour nos modèles il faudra penser à changer les types de données (ex: float64 -> float32) pour économiser de la mémoire

## Illustrations

![png](images/trace_gps.png)

![png](images/distances2_3jours.png)

![png](images/distances_3jours.png)