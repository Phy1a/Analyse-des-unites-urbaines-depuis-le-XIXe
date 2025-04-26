import pandas as pd #pandas
import os #os
import re
import requests
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from io import StringIO


import warnings
warnings.filterwarnings('ignore')

def simplify_city(libgeo):
    '''remove useless "Arrondissement" particule ''' 
    match = re.match(r"^(.*?)(?: \d{1,2}(?:er|e)? Arrondissement)$", libgeo)
    if match:
        return match.group(1)  # Keep simple city
    return libgeo


directory=os.getcwd()


if not(os.path.exists("output/organised_city_data.xlsx")):

    # INPUT EXCEL FILE 1
    
    df_uu_2024 = pd.read_excel("input/UU2020_au_01-01-2024.xlsx", engine='openpyxl', sheet_name="Composition_communale")
    df_uu_2024 = df_uu_2024[4:] # Delete first useless lines
    df_uu_2024.columns = df_uu_2024.iloc[0]      # set first line as column
    df_uu_2024 = df_uu_2024[1:]                  # delete first line
    

    df_uu_2024 = df_uu_2024[df_uu_2024.iloc[:,4] == "Unité urbaine"][["LIBGEO","LIBUU2020","DEP"]] # Remove useless data
    df_uu_2024 = df_uu_2024.sort_values(by=["LIBUU2020", "LIBGEO"], ascending=[True, True])
    df_uu_2024 = df_uu_2024[(pd.to_numeric(df_uu_2024.iloc[:, 2], errors="coerce") <= 95) ] # only keep Metropolitan France
    df_uu_2024.reset_index(drop=True, inplace=True)  # reset index

    #  INPUT EXCEL FILE 2

    df_pop_histo = pd.read_excel("input/base-pop-historiques-1876-2022.xlsx", engine='openpyxl')

    df_pop_histo = df_pop_histo[4:] # Delete first useless lines
    df_pop_histo.columns = df_pop_histo.iloc[0]      # set first line as column
    df_pop_histo = df_pop_histo[1:]                  # delete first line
    df_pop_histo.reset_index(drop=True, inplace=True)  # reset index

    df_pop_histo = df_pop_histo.iloc[:,2:] #remove useless columns
    df_pop_histo["LIBGEO"] = df_pop_histo["LIBGEO"].apply(simplify_city) # uniform city names to duplicates
    df_pop_histo = df_pop_histo.groupby(["DEP", "LIBGEO"], as_index=False)[df_pop_histo.columns[3:]].sum() # sum duplicates

    # Complete the DataFrame for the missing years 1875 - 1801

    url = "http://cassini.ehess.fr/"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            dep_dico = { # only Metropolitain France, code on the used website for GET requests
                "01": "36", "02": "20", "03": "55", "04": "106", "05": "58", "06": "104","07": "62", "08": "74",
                "09": "114","10": "19","11": "115","12": "4", "13": "125", "14": "22", "15": "120", "16": "40",
                "17": "94", "18": "66", "19": "86", "21": "38", "22": "119", "23": "101", "24": "39", "25": "21",
                "26": "123", "27": "72", "28": "54", "29": "138", "30": "99", "31": "78", "32": "59", "33": "60",
                "34": "33", "35": "71", "36": "117", "37": "32", "38": "56", "39": "18", "40": "97", "41": "135",
                "42": "47", "43": "96", "44": "16", "45": "65", "46": "17", "47": "89", "48": "127", "49": "132",
                "50": "73", "51": "43", "52": "91", "53": "100", "54": "13", "55": "6", "56": "130", "57": "26",
                "58": "69", "59": "11", "60": "14", "61": "128", "62": "42", "63": "111", "64": "2", "65": "76",
                "66": "103", "67": "64", "68": "30", "69": "87", "70": "10", "71": "35", "72": "107", "73": "109",
                "74": "51", "75": "129", "76": "8", "77": "68", "78": "24", "79": "80", "80": "27", "81": "98",
                "82": "5", "83": "81", "84": "133", "85": "116", "86": "82", "87": "113", "88": "45", "89": "61",
                "90": "136", "91": "25", "92": "137", "93": "141", "94": "46", "95": "44"
            }



            backup = df_pop_histo

            for year in range(1871,1800,-5):
                df_year = pd.DataFrame()
                for dep in dep_dico:
                    url = f"http://cassini.ehess.fr/fr/PHP/exportPopCSV.php?csv=1&valider=validation&departement={dep_dico[dep]}&popBorneInf=0&popBorneSup=10000000&annee={year}"
                    filename = f"output/cassini_dep_{dep}_{year}.csv"

                    try:
                        # send GET request
                        response = requests.get(url)
                        
                        # Check request success
                        if response.status_code == 200:
                                df_temp = pd.read_csv(StringIO(response.text), sep=";", encoding="utf-8", on_bad_lines='skip')
                                
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

                df_year = df_year.drop_duplicates(subset=["LIBGEO", "DEP"], keep="first") # remove duplicates
                df_pop_histo = df_pop_histo.merge(df_year, on=["LIBGEO","DEP"], how="left")

                duplicates = df_year.duplicated(subset=["LIBGEO", "DEP"]).sum()
                if duplicates > 0:
                    print(f"⚠️  {duplicates} duplicates in df_year for {year} on LIBGEO+DEP")

                    
                    
            new_cols = [col for col in df_pop_histo if col not in backup.columns] # Identify new columns
            df_pop_histo = df_pop_histo[[*backup.columns, *new_cols]] # Réorganize columns

        else:
            print(f"Website answered with the code : {response.status_code} ❌")
            print("Unable to load datas before 1876 because the website isn't accessible")

    except requests.exceptions.RequestException as e:
        print(f"Connexion error : {e} ❌")
        print("Unable to load datas before 1876 because the website isn't accessible")


    df_total = df_uu_2024.merge(df_pop_histo, on=["LIBGEO","DEP"], how="inner") # fusion
    df_total.to_excel("output/organised_city_data.xlsx", index=False, engine='openpyxl') # OUTPUT 1

else:
    df_total = pd.read_excel("output/organised_city_data.xlsx", engine='openpyxl')


if not(os.path.exists("output/organised_uu_data.xlsx")):
    df_sum_uu = df_total.groupby("LIBUU2020", as_index=False)[df_total.columns[3:]].sum()
    df_sum_uu.to_excel("output/organised_uu_data.xlsx", index=False, engine='openpyxl') # OUTPUT 2

else:
    df_sum_uu = pd.read_excel("output/organised_uu_data.xlsx", engine='openpyxl')


if not(os.path.exists("output/top_per_year.xlsx")):
    df_top_per_year = pd.DataFrame()
    for col in df_sum_uu.columns[1:]:
        df_top_per_year[col[-4:]] = df_sum_uu[["LIBUU2020",col]].sort_values(by=col, ascending=False).reset_index(drop=True).iloc[:24,0]
    df_top_per_year.to_excel("output/top_per_year.xlsx", index=False, engine='openpyxl') # OUTPUT 3

    wb = load_workbook("output/top_per_year.xlsx")
    ws = wb.active

    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = 25

    wb.save("output/top_per_year.xlsx")
