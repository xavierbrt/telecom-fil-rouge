
# # Clean migration periods
# 
# Ce notebook permet d'extraire d'un fichier de points GPS, les points GPS qui sont au cours d'une migration.<br />
# Pour cela, on ne garde que les jours pour lesquels sur les n jours suivants (n est un seuil à définir, par exemple 3 jours) l'oiseau parcourera plus de d km (d est un seuil à définir, par exemple 22 km).


import math
import pandas as pd
import numpy as np
import datetime
import geopy.distance
from os import listdir
from os.path import isfile, join



path = "./data/birds/"
files = [f for f in listdir(path) if isfile(join(path, f))]
print("Nombre de fichiers: ", len(files))

for one_file in files:
    filename = path + one_file
    print("-----------------------")
    data = pd.read_csv(filename, sep=',', engine='python')
    input_shape = data.shape
    nb_birds = len(data["tag-local-identifier"].value_counts())
    print(one_file)


    # # 2. Data cleaning
    # ## 2.1. Suppression des lignes et colonnes inutiles


    # Remove rows with invalid status (based on column status)
    if 'eobs:status' in data:
        data = data[(data['eobs:status'] == "A")]
        data.drop('eobs:status', axis=1, inplace=True)

    # If there is "unnamed" columns, we remove them
    cols = [c for c in data.columns if c.lower()[:4] != 'unnamed:']
    data = data[cols]



    columns_we_want = ['event-id', 'timestamp','location-long','location-lat','eobs:horizontal-accuracy-estimate', 
                    'height-above-ellipsoid','ground-speed','eobs:speed-accuracy-estimate','heading',
                    'tag-local-identifier']

    # List the columns we want to keep and which are available in the dataframe data
    columns_to_keep = []
    for col in columns_we_want:
        if col in data.columns:
            columns_to_keep.append(col)
    


    # Keep only interesting columns
    data = data[columns_to_keep]



    # ## 2.2. On enlève les oiseaux qui ne migrent pas (en se basant sur leurs positions)
    # Group birds by id
    if "ground-speed" in data:
        df_bird_grouped = data.groupby("tag-local-identifier").agg({"timestamp": ['min', 'max'], "location-long": ['min', 'max'], "location-lat": ['min', 'max'], "ground-speed": ['min', 'max']})
    else:
        df_bird_grouped = data.groupby("tag-local-identifier").agg({"timestamp": ['min', 'max'], "location-long": ['min', 'max'], "location-lat": ['min', 'max']})



    # Compute time and distance amplitude for each bird
    df_bird_grouped["timestamp", "diff"] = pd.to_datetime(df_bird_grouped["timestamp","max"]) - pd.to_datetime(df_bird_grouped["timestamp","min"])
    df_bird_grouped["location-long", "diff"] = df_bird_grouped["location-long", "max"] - df_bird_grouped["location-long", "min"]
    df_bird_grouped["location-lat", "diff"] = df_bird_grouped["location-lat", "max"] - df_bird_grouped["location-lat", "min"]



    # lists the birds that do not migrate
    id_birds_to_remove = df_bird_grouped[(df_bird_grouped["location-lat", "diff"] < 0.2) | (df_bird_grouped["location-long", "diff"] < 0.2)].index.to_list()


    # Remove the birds
    data = data[~data["tag-local-identifier"].isin(id_birds_to_remove)]


    # # 3. Export du fichier en csv

    nb_birds_end = len(data["tag-local-identifier"].value_counts())
    print("=== Données d'entrée ===")
    print("Dimensions du fichier: {}".format(input_shape))
    print("Nombre d'oiseaux:      {}".format(nb_birds))
    print("\n=== Données de sortie ===")
    print("Dimensions du fichier: {}".format(data.shape))
    print("Nombre d'oiseaux:      {}".format(nb_birds_end))

    output_filename = filename[:-4] + "-cleaned" + ".csv" 
    data.to_csv(output_filename, index=False)
    print("Fichier {:s} exporté !".format(output_filename))







