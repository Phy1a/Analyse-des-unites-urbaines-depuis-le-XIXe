import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

df_pop_histo = pd.read_excel('input/base-pop-historiques-1876-2022.xlsx', engine='openpyxl', header=5)

columns_of_interest = ['LIBGEO', 'PMUN2021']
df_pop_histo_filtered = df_pop_histo[columns_of_interest]

df_pop_histo_filtered.loc[:, 'PMUN2021'] = pd.to_numeric(df_pop_histo_filtered['PMUN2021'], errors='coerce')

df_pop_histo_filtered = df_pop_histo_filtered.dropna(subset=['PMUN2021'])

df_pop_histo_filtered = df_pop_histo_filtered[df_pop_histo_filtered['PMUN2021'] > 0]

df_pop_histo_filtered_sorted = df_pop_histo_filtered.sort_values(by='PMUN2021', ascending=False)

df_pop_histo_filtered_sorted['Rank'] = range(1, len(df_pop_histo_filtered_sorted) + 1)

df_pop_histo_filtered_sorted['log_population'] = np.log(df_pop_histo_filtered_sorted['PMUN2021'])
df_pop_histo_filtered_sorted['log_rank'] = np.log(df_pop_histo_filtered_sorted['Rank'])

# Exclure les 10 premières villes (celles avec les populations les plus grandes)
df_pop_histo_filtered_sorted_excluded = df_pop_histo_filtered_sorted.iloc[10:]

coefficients = np.polyfit(df_pop_histo_filtered_sorted_excluded['log_rank'], df_pop_histo_filtered_sorted_excluded['log_population'], 1)

regression_line = np.polyval(coefficients, df_pop_histo_filtered_sorted_excluded['log_rank'])

plt.figure(figsize=(10,6))
plt.scatter(df_pop_histo_filtered_sorted_excluded['log_rank'], df_pop_histo_filtered_sorted_excluded['log_population'], alpha=0.7, color='blue', label='Données')
plt.plot(df_pop_histo_filtered_sorted_excluded['log_rank'], regression_line, color='red', linewidth=2, label='Droite de régression')

plt.title("Loi de Zipf pour les villes en 2021", fontsize=16)
plt.xlabel("Log(Rang)", fontsize=12)
plt.ylabel("Log(Population)", fontsize=12)
plt.grid(True)
plt.legend()

output_dir = 'output/zipf'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
file_path = os.path.join(output_dir, 'zipf_law_graph_without_top_10_cities.png')
plt.savefig(file_path)

plt.show()
