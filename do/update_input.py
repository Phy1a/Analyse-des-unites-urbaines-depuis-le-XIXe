import pandas as pd
import os 
import re
import requests
from io import StringIO


def simplify_city(libgeo):
    '''remove useless "Arrondissement" particule ''' 
    match = re.match(r"^(.*?)(?: \d{1,2}(?:er|e)? Arrondissement)$", libgeo)
    if match:
        return match.group(1)  # Keep simple city
    return libgeo

if os.path.exists("input/base-pop-historiques-1876-2022-updated.xlsx"):
    exit(1)

if not(os.path.exists("input/base-pop-historiques-1876-2022.xlsx")):
    print("Missing File : input/base-pop-historiques-1876-2022.xlsx")
    print('Code ended, please try redownloading Github package')
    exit(1)


df_pop_histo = pd.read_excel("input/base-pop-historiques-1876-2022.xlsx", engine='openpyxl')

df_pop_histo = df_pop_histo[4:] # Delete first useless lines
df_pop_histo.columns = df_pop_histo.iloc[0]      # set first line as column
df_pop_histo = df_pop_histo[1:]                  # delete first line
df_pop_histo.reset_index(drop=True, inplace=True)  # reset index

df_pop_histo = df_pop_histo.iloc[:,2:]#remove useless columns
df_pop_histo["LIBGEO"] = df_pop_histo["LIBGEO"].apply(simplify_city) # uniform city names to duplicates
df_pop_histo = df_pop_histo.groupby(["DEP", "LIBGEO"], as_index=False)[df_pop_histo.columns[3:]].sum() # sum duplicates

url = "http://cassini.ehess.fr/"

# Complete the input file for Corsica (missing info)
try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200: 
        dep_dico2 = { # only Corsica, code on the used website for GET requests
                "2A" : "84", "2B" : "92"
                }
        cols_to_update= ["PTOT1931","PTOT1926","PTOT1921","PTOT1911","PTOT1906","PTOT1901", "PTOT1896","PTOT1891","PTOT1886","PTOT1881","PTOT1876"]

        for col in cols_to_update:
            year = col[-4:]
            df_year = pd.DataFrame()
            for dep in dep_dico2:
                url = f"http://cassini.ehess.fr/fr/PHP/exportPopCSV.php?csv=1&valider=validation&departement={dep_dico2[dep]}&popBorneInf=0&popBorneSup=10000000&annee={year}"

                try:
                    # send GET request
                    response = requests.get(url)
                    
                    # Check request success
                    if response.status_code == 200:
                        df_temp = pd.read_csv(StringIO(response.text), sep=";", encoding="utf-8", on_bad_lines='skip') #transfort response into df
                        
                        if df_temp.shape[1] != 4:
                            print(f"Badly formed data for dep {dep} in {year}, columns = {df_temp.columns}")
                        else:
                            df_temp.columns = ["INSEE", "LIBGEO", "PTOT"+str(year), "Year"]
                            df_temp = df_temp[["LIBGEO", "PTOT"+str(year)]]
                            df_temp["DEP"] = dep
                            df_year = pd.concat([df_year, df_temp], ignore_index=True)

                    else:
                        print(f"Error for {dep} in {year}: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"Connection error for {dep} in {year}: {e}")
                
            
            print(f"\n>>> Merging year {year}")
            print(f"    df_year shape: {df_year.shape}")
            print(f"    df_pop_histo shape after merge: {df_pop_histo.shape}")

            df_year = df_year.drop_duplicates(subset=["LIBGEO", "DEP"], keep="first")

            duplicates = df_year.duplicated(subset=["LIBGEO", "DEP"]).sum()
            if duplicates > 0:
                print(f"⚠️  {duplicates} duplicates in df_year for {year} on LIBGEO+DEP")
            

            df_pop_histo.set_index("LIBGEO", inplace=True)
            df_year.set_index("LIBGEO", inplace=True)

            for libgeo in df_year.index:
                if libgeo in df_pop_histo.index:
                    if col in df_pop_histo.columns:
                        df_pop_histo.at[libgeo, col] = df_year.at[libgeo, col]

            df_pop_histo.reset_index(inplace=True)
        
        df_pop_histo.to_excel("input/base-pop-historiques-1876-2022-updated.xlsx", index=False, engine='openpyxl') # OUTPUT 1

except requests.exceptions.RequestException as e:
    print(f"Connexion error : {e} ❌")
    print("Unable to update datas for Corsica  because the website isn't accessible")
