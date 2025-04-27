import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Charger les données
df_pop_histo = pd.read_excel('input/base-pop-historiques-1876-2022.xlsx', engine='openpyxl', header=5)

# Sélectionner les colonnes d'intérêt : nom de la ville et population en 2021
columns_of_interest = ['LIBGEO', 'PMUN2021']
df_pop_histo_filtered = df_pop_histo[columns_of_interest]

# Convertir la colonne de population en numérique, en remplaçant les erreurs par NaN
df_pop_histo_filtered.loc[:, 'PMUN2021'] = pd.to_numeric(df_pop_histo_filtered['PMUN2021'], errors='coerce')

# Supprimer les lignes avec des valeurs NaN dans la colonne "PMUN2021"
df_pop_histo_filtered = df_pop_histo_filtered.dropna(subset=['PMUN2021'])

# Supprimer les villes ayant une population de zéro pour éviter le problème de log(0)
df_pop_histo_filtered = df_pop_histo_filtered[df_pop_histo_filtered['PMUN2021'] > 0]

# Trier les données par population en 2021, de la plus grande à la plus petite
df_pop_histo_filtered_sorted = df_pop_histo_filtered.sort_values(by='PMUN2021', ascending=False)

# Assigner un rang à chaque ville (rang 1 pour la ville la plus grande)
df_pop_histo_filtered_sorted['Rank'] = range(1, len(df_pop_histo_filtered_sorted) + 1)

# Calculer les logarithmes de la population et du rang
df_pop_histo_filtered_sorted['log_population'] = np.log(df_pop_histo_filtered_sorted['PMUN2021'])
df_pop_histo_filtered_sorted['log_rank'] = np.log(df_pop_histo_filtered_sorted['Rank'])

# Exclure les 10 premières villes (celles avec les populations les plus grandes)
df_pop_histo_filtered_sorted_excluded = df_pop_histo_filtered_sorted.iloc[10:]

# Ajouter une droite de régression sur les données restantes
# Effectuer un ajustement linéaire des données log-transformées sans les premières villes
coefficients = np.polyfit(df_pop_histo_filtered_sorted_excluded['log_rank'], df_pop_histo_filtered_sorted_excluded['log_population'], 1)

# Calculer les valeurs de la droite de régression
regression_line = np.polyval(coefficients, df_pop_histo_filtered_sorted_excluded['log_rank'])

# Tracer le graphique avec la droite de régression
plt.figure(figsize=(10,6))
plt.scatter(df_pop_histo_filtered_sorted_excluded['log_rank'], df_pop_histo_filtered_sorted_excluded['log_population'], alpha=0.7, color='blue', label='Données')
plt.plot(df_pop_histo_filtered_sorted_excluded['log_rank'], regression_line, color='red', linewidth=2, label='Droite de régression')

# Ajouter les labels et le titre
plt.title("Loi de Zipf pour les villes en 2021", fontsize=16)
plt.xlabel("Log(Rang)", fontsize=12)
plt.ylabel("Log(Population)", fontsize=12)
plt.grid(True)
plt.legend()

output_dir = 'output/zipf'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)  # Créer le dossier si nécessaire
file_path = os.path.join(output_dir, 'zipf_law_graph_without_top_10_cities.png')
plt.savefig(file_path)

# Afficher l'emplacement du fichier sauvegardé
print(f"Le graphique a été enregistré sous : {file_path}")

# Afficher le graphique
plt.show()
