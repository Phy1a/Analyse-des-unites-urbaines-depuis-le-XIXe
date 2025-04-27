import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

df_pop_histo = pd.read_excel('input/base-pop-historiques-1876-2022.xlsx', engine='openpyxl', header=5)

columns_of_interest = ['LIBGEO', 'PMUN2021', 'PMUN2020']
df_pop_histo_filtered = df_pop_histo[columns_of_interest]

df_pop_histo_filtered['PMUN2021'] = pd.to_numeric(df_pop_histo_filtered['PMUN2021'], errors='coerce')
df_pop_histo_filtered['PMUN2020'] = pd.to_numeric(df_pop_histo_filtered['PMUN2020'], errors='coerce')

df_pop_histo_filtered = df_pop_histo_filtered.dropna(subset=['PMUN2021', 'PMUN2020'])

df_pop_histo_filtered['delta_log_population'] = np.log(df_pop_histo_filtered['PMUN2021']) - np.log(df_pop_histo_filtered['PMUN2020'])

df_pop_histo_filtered['log_population'] = np.log(df_pop_histo_filtered['PMUN2021'])

plt.figure(figsize=(10,6))
plt.scatter(df_pop_histo_filtered['log_population'], df_pop_histo_filtered['delta_log_population'], alpha=0.5, color='blue', s=10, label='Données')
plt.axhline(0, color='black', linestyle='--', label="Variation nulle")

plt.title("Loi de Gibrat (2021 vs 2020)", fontsize=16)
plt.xlabel("Log(Population en 2021)", fontsize=12)
plt.ylabel("Variation du log de la population", fontsize=12)
plt.grid(True)
plt.legend()

output_dir = 'output/gibrat'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
file_path = os.path.join(output_dir, 'gibrat_law_graph.png')
plt.savefig(file_path)

plt.show()
