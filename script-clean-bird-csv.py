
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

# On fixe le seuil à 200 km (peut être modifié)
treshold = 200

## Helpers
def check_date(distance, date, date_in_a_week):
    """ 
    Check if the date taken 3 rows after (date_in_a_week) is well 4 days (3 days + a margin to take the hours into account) 
    after the date of the current row (date)
    """
    if pd.to_datetime(date_in_a_week) < pd.to_datetime(date) + datetime.timedelta(days=4):
        return distance
    return 0

def compute_distance(x):
    """
    Compute distance in km between two points given by their coordinates
    """
    if math.isnan(x["location-lat"]) or math.isnan(x["lat_in_a_week"]) or math.isnan(x["location-long"]) or math.isnan(x["long_in_a_week"]):
        return 0
    return geopy.distance.distance((x["location-lat"], x["location-long"]), (x["lat_in_a_week"], x["long_in_a_week"])).km







for one_file in files:
    filename = path + one_file
    print("-----------------------")
    data = pd.read_csv(filename, sep=',', engine='python')
    input_shape = data.shape
    nb_birds = len(data["tag-local-identifier"].value_counts())
    print(one_file)


    """ 2. Data cleaning """
    ## 2.1. Suppression des lignes et colonnes inutiles

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


    ## 2.2. On enlève les oiseaux qui ne migrent pas (en se basant sur leurs positions)
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





    """ 3. Keep migration periods """

    # On change le type du timestamp et on met le timestamp en index
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data.set_index("timestamp", drop=False, inplace=True)
    data["date"] = data["timestamp"].astype(str)
    data.head()

    ## 3.1. Calcul des distances sur les 3 prochains jours

    # Group by bird > year > semester > month > day
    df_distance = data.groupby(["tag-local-identifier", lambda x: x.year, lambda x: math.trunc(x.month/6-0.1), lambda x: x.month, lambda x: x.day])                   .agg({"ground-speed": 'mean', "location-lat": 'median', "location-long": 'median', 'date': 'max', 'tag-local-identifier': 'min'})
    print(df_distance.shape)

    # Calcul de la distance parcourue sur les 3 jours glissants suivants
    df_distance["lat_in_a_week"] =  df_distance.shift(-3)["location-lat"]
    df_distance["long_in_a_week"] =  df_distance.shift(-3)["location-long"]
    df_distance["date_in_a_week"] =  df_distance.shift(-3)["date"]
    df_distance["distance"] = df_distance.apply(lambda x : compute_distance(x), axis=1)
    # On met la distance à 0 si il y a un trou dans les dates (la date est discontinue entre la ligne et 3 lignes en dessous)
    df_distance["distance"] = df_distance.apply(lambda x: check_date(x["distance"], x["date"], x["date_in_a_week"]), axis=1)

    df_distance.fillna(0, inplace=True)
  

    ## 3.2. Affichage de la répartition des distances, si on veut affiner le seuil
    df_distance["distance"].describe(np.arange(0,1,0.05))

    # On va garder un seuil de distance parcourue sur 3 jours à **200 km**, qui correspond presque au seuil des percentiles à 95%.

    ## 3.3. Suppression des données sur les jours hors migration
    print("Treshold: ", treshold)

    # On itère par oiseau
    for bird_id, df1 in df_distance.groupby(level=0):
        # On itère par année
        for year, df2 in df1.groupby(level=1):
            # On itère par semestre (pour certains oiseaux on a la migration aller et la migration retour)
            for semester, df3 in df2.groupby(level=2):
                print("Bird id : ", bird_id, " | Année : ", year, " | Semestre : ", semester)
                print("Jours en migration : ", df3[df3["distance"] > treshold].shape[0])
                # On fixe les dates des périodes sur lesquelles on va enlever des données (sur le semestre, avant et après la migration)
                # Il nous faut donc les dates de début et fin de semestre
                if semester == 0:
                        semester_start = str(year) + "-01-01"
                        semester_end = str(year) + "-07-01"
                else:
                    semester_start = str(year) + "-07-01"
                    semester_end = str(year+1) + "-01-01"
                # Et les dates de début et fin de période de migration
                if df3[df3["distance"] > treshold].shape[0] > 0:
                    min_date = df3[df3["distance"] > treshold]["date"].min()
                    max_date = pd.to_datetime(df3[df3["distance"] > treshold]["date"].max()) + datetime.timedelta(days=3)
                    print("Dates de migration : ", str(min_date)[:11], " - ", str(max_date)[:11])
                else:
                    # Si sur ce semestre il n'y a pas de migration, la période à supprimer est le semestre en entier
                    min_date = semester_end
                    max_date = semester_start
                    print("Dates de migration : --")
                
                # On supprime les données hors période
                data = data[~((data["tag-local-identifier"] == bird_id) & (((data["timestamp"] >= semester_start) & (data["timestamp"] < min_date)) |
                                                                        ((data["timestamp"] > max_date) & (data["timestamp"] < semester_end))))]
                print("-------------------------------------------------")


    # On supprime la colonne date, dont on n'a plus besoin (on a toujours timestamp)
    if "date" in data:
        data.drop("date", axis=1, inplace=True)



    """ 4. Export du fichier en csv """

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







