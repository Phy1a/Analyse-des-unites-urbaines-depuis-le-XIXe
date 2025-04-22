import pandas as pd #pandas
import geopandas as gpd #geopandas
import os #os
import matplotlib.pyplot as plt
import shapely
import re


#Cette fonction permet de reparer certains fichiers
from shapely import geometry
upcast_dispatch = {geometry.Point: geometry.MultiPoint, 
                   geometry.LineString: geometry.MultiLineString, 
                   geometry.Polygon: geometry.MultiPolygon}

def maybe_cast_to_multigeometry(geom):
    caster = upcast_dispatch.get(type(geom), lambda x: x[0])
    return caster([geom])

import warnings
warnings.filterwarnings('ignore')

def simplify_city(libgeo):
    '''remove useless particule such as "Arrondissement"''' 
    match = re.match(r"^(.*?)(?: \d{1,2}(?:er|e)? Arrondissement)$", libgeo)
    if match:
        return match.group(1)  # Keep simple city
    return libgeo


directory=os.getcwd()

# EXCEL FILE 1

df_uu_2024 = pd.read_excel("input/UU2020_au_01-01-2024.xlsx", engine='openpyxl', sheet_name="Composition_communale")
df_uu_2024 = df_uu_2024[4:] # Delete first useless lines
df_uu_2024.columns = df_uu_2024.iloc[0]      # set first line as column
df_uu_2024 = df_uu_2024[1:]                  # delete first line

df_uu_2024 = df_uu_2024[df_uu_2024.iloc[:,4] == "Unité urbaine"][["LIBGEO","LIBUU2020","DEP"]] # Remove useless data
df_uu_2024 = df_uu_2024.sort_values(by=["LIBUU2020", "LIBGEO"], ascending=[True, True])
df_uu_2024 = df_uu_2024[pd.to_numeric(df_uu_2024.iloc[:, 2], errors="coerce") <= 95] # only keep Metropolitan France
df_uu_2024.reset_index(drop=True, inplace=True)  # reset index

# EXCEL FILE 2

df_pop_histo = pd.read_excel("input/base-pop-historiques-1876-2022.xlsx", engine='openpyxl')

df_pop_histo = df_pop_histo[4:] # Delete first useless lines
df_pop_histo.columns = df_pop_histo.iloc[0]      # set first line as column
df_pop_histo = df_pop_histo[1:]                  # delete first line
df_pop_histo.reset_index(drop=True, inplace=True)  # reset index

df_pop_histo = df_pop_histo.iloc[:,2:]#remove useless columns
df_pop_histo["LIBGEO"] = df_pop_histo["LIBGEO"].apply(simplify_city) # uniform city names to duplicates


df_total = df_uu_2024.merge(df_pop_histo, on=["LIBGEO","DEP"], how="inner")
# if os.path.exists("output/organised_city_data.xlsx"):
#     os.remove("output/organised_city_data.xlsx")
# df_total.to_excel("output/organised_city_data.xlsx", index=False, engine='openpyxl') # OUTPUT 1

# EXCEL FILE 3

df_sum_uu = df_total.groupby("LIBUU2020", as_index=False)[df_total.columns[3:]].sum()
# if os.path.exists("output/organised_uu_data.xlsx"):
#     os.remove("output/organised_uu_data.xlsx")
# df_sum_uu.to_excel("output/organised_uu_data.xlsx", index=False, engine='openpyxl') # OUTPUT 2


df_top_per_year = pd.DataFrame()
for col in df_sum_uu.columns[1:]:
    df_top_per_year[col[-4:]] = df_sum_uu[["LIBUU2020",col]].sort_values(by=col, ascending=False).reset_index(drop=True).iloc[:24,0]

# if not(os.path.exists("output/top_per_year.xlsx")):
#     os.remove("output/top_per_year.xlsx")
# df_top_per_year.to_excel("output/top_per_year.xlsx", index=False, engine='openpyxl') # OUTPUT 3
