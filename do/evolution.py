import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# Fonction pour simplifier les noms de ville (supprimer "Arrondissement" s'il y en a)
def simplify_city(libgeo):
    '''remove useless "Arrondissement" particule''' 
    match = re.match(r"^(.*?)(?: \d{1,2}(?:er|e)? Arrondissement)$", libgeo)
    if match:
        return match.group(1)  # Keep simple city
    return libgeo

# Assurer que le répertoire d'entrée existe
directory = os.getcwd()

# Charger le fichier des UU
df_uu_2024 = pd.read_excel("input/UU2020_au_01-01-2024.xlsx", engine='openpyxl', sheet_name="Composition_communale")
df_uu_2024 = df_uu_2024[4:]  # Supprimer les premières lignes inutiles
df_uu_2024.columns = df_uu_2024.iloc[0]  # Utiliser la première ligne comme colonne
df_uu_2024 = df_uu_2024[1:]  # Supprimer la première ligne après

# Charger les données historiques de population
df_pop_histo = pd.read_excel("input/base-pop-historiques-1876-2022.xlsx", engine='openpyxl')

# Nettoyer les données historiques
df_pop_histo = df_pop_histo[4:]  # Supprimer les lignes inutiles
df_pop_histo.columns = df_pop_histo.iloc[0]  # Utiliser la première ligne comme colonne
df_pop_histo = df_pop_histo[1:]  # Supprimer la première ligne après

# Reset index
df_pop_histo.reset_index(drop=True, inplace=True)

# Supprimer les colonnes inutiles et uniformiser les noms de villes
df_pop_histo = df_pop_histo.iloc[:, 2:]  # Garder uniquement les colonnes de population
df_pop_histo["LIBGEO"] = df_pop_histo["LIBGEO"].apply(simplify_city)  # Simplifier les noms de villes
df_pop_histo = df_pop_histo.groupby(["DEP", "LIBGEO"], as_index=False)[df_pop_histo.columns[3:]].sum()  # Agréger les populations par ville

# Sélectionner les UU les plus grandes (top_uu) pour la courbe d'évolution
top_uu = ['Paris', 'Lyon', 'Marseille-Aix-en-Provence', 'Toulouse', 'Lille', 'Nantes', 'Nice', 'Strasbourg', 'Rennes', 'Montpellier']

# Filtrer les données pour ces UU
df_pop_histo_filtered = df_pop_histo[df_pop_histo['LIBGEO'].isin(top_uu)]

# Sélectionner toutes les années disponibles dans le fichier (de 1801 à 2022)
columns_of_interest = ['LIBGEO'] + [col for col in df_pop_histo.columns if 'PTOT' in col or 'PMUN' in col]

# Garder les colonnes pertinentes
df_pop_histo_filtered = df_pop_histo_filtered[columns_of_interest]

# Convertir les colonnes de population en type numérique
for column in df_pop_histo_filtered.columns[1:]:
    df_pop_histo_filtered[column] = pd.to_numeric(df_pop_histo_filtered[column], errors='coerce')

# Mettre à jour les noms des colonnes pour qu'elles contiennent les années
df_pop_histo_filtered.columns = [col.split('PMUN')[-1] if 'PMUN' in col else col.split('PTOT')[-1] for col in df_pop_histo_filtered.columns]

# Tracer les courbes d'évolution des populations pour les UU sélectionnées
plt.figure(figsize=(14, 8))
for uu in top_uu:
    # Extraire les données de chaque UU
    uu_data = df_pop_histo_filtered[df_pop_histo_filtered['LIBGEO'] == uu]
    
    if not uu_data.empty:  # Vérifier que uu_data n'est pas vide
        # Tracer la courbe
        plt.plot(uu_data.columns[1:], uu_data.iloc[0, 1:], label=uu)

# Ajouter des titres et légendes
plt.title('Courbes d\'évolution des populations des grandes unités urbaines (UU)', fontsize=16)
plt.xlabel('Année', fontsize=12)
plt.ylabel('Population', fontsize=12)
plt.xticks(rotation=45)

# Ajouter la légende
plt.legend(title="Unités Urbaines", loc='upper left')
plt.tight_layout()

# Afficher le graphique
plt.show()
