import pandas as pd #pandas
import os #os
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely


lost_line = pd.DataFrame([{"DEP" : "01", "LIBGEO":"Ozan", "longitude" : "4.91667", "latitude" :"46.3833"}])
print(lost_line.head())