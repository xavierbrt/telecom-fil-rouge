#!/usr/bin/env python
# coding: utf-8

# # Compute GPS Surface
# 
# Ce notebook calcule les surfaces couvertes par les oiseaux d'un fichier de tracking GPS provenant de Movebank. On calcule ces surfaces selon une certaine granularité temporelle (par semestre par défaut).<br />
# L'objectif est de savoir quels seront les besoins en données météo pour couvrir les traces GPS de ces oiseaux.

# Saisir le chemin d'accès du fichier:


# ### Imports

import math
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from os import listdir
from os.path import isfile, join

# ### Helpers

plotly_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b','#e377c2','#7f7f7f', '#bcbd22', '#17becf']
                  # blue,     orange,     green,      red,      purple,    brown,     pink,     gray,  yellow-green, blue-teal
   




path = "./data/birds/"
files = [f for f in listdir(path) if isfile(join(path, f))]
print("Nombre de fichiers: ", len(files))



for one_file in files:
    # # 1. Chargement et préparation des données
    # ## 1.1. Chargement des données
    filename = path + one_file
    data = pd.read_csv(filename)
    input_shape = data.shape
    nb_birds = len(data["tag-local-identifier"].value_counts())
    print("-----------------------")
    print("Dimensions du fichier: {}".format(input_shape))
    print("Nombre d'oiseaux: {}".format(nb_birds))


    # ## 1.2. Préparation des données


    # On supprime l'event-id, on change le type du timestamp et on met le timestamp en index
    if "event-id" in data:
        data.drop("event-id", axis=1, inplace=True)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data.set_index("timestamp", drop=False, inplace=True)


    # # 2. Groupement de données


    # Choisir une granularité, pour regrouper les données par an, semestre, mois.
    granularity = "half_year" # "year" (default), "half_year", "month"


    if granularity == "month":
        df_grouped = data.groupby([lambda x: x.year, lambda x: x.month]).agg({"location-long": ['min', 'max'], "location-lat": ['min', 'max'], "timestamp": ['min', 'max'], "tag-local-identifier": 'nunique'})
    elif  granularity == "half_year":
        df_grouped = data.groupby([lambda x: x.year, lambda x: math.trunc(x.month/6-0.1)]).agg({"location-long": ['min', 'max'], "location-lat": ['min', 'max'], "timestamp": ['min', 'max'], "tag-local-identifier": 'nunique'})
    else:
        df_grouped = data.groupby([lambda x: x.year]).agg({"location-long": ['min', 'max'], "location-lat": ['min', 'max'], "timestamp": ['min', 'max'], "tag-local-identifier": 'nunique'})


    #display_squares(df_grouped, 2015)

    # Affichage du résultat sur une carte (c'est optionnel, commentez la ligne si vous ne voulez pas)
    #display_squares(df_grouped)


    # # 3. Export du fichier en csv



    output_filename = filename[:-4] + "-surface" + ".csv"
    df_grouped["filename"] = output_filename
    df_grouped.to_csv(output_filename, index=False)
    print("Fichier '{:s}' exporté !".format(output_filename))




