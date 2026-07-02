import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

import core.filters as filter

DATA_ARQUIVE_PATH = 'dados_simulados.csv'
FREQUENCY_HZ = 860.0
FC = 1.0  
NYQUIST = FREQUENCY_HZ / 2.0

def data_arquive_load(data_path):
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        time = df["time"].values
        mass = df["mass"].values
        return time, mass
    else:
        raise FileNotFoundError(f"Erro Crítico: O arquivo {data_path} não foi localizado na pasta.")

def mass_derivate(mass, fs):
    dt = 1.0/fs
    delta_mass = -np.gradient(mass, dt)
    return np.clip(delta_mass, 0, None)

def graffic_plot(time, mass_raw, mass_filtered, delta_mass_raw, delta_mass_filtered):
    # Gráfico 1: Comparativo de Massa (Bruta vs Filtrada)
    plt.subplot(2, 1, 1)
    plt.plot(time, mass_raw, color='gray', alpha=0.5, label='Massa Bruta (Com Ruído)')
    plt.plot(time, mass_filtered, color='blue', linewidth=2, label='Massa Filtrada (Butterworth)')
    plt.ylabel('Massa do Propelente (g)')
    plt.title('Análise de Sinais da Queima KNSU - Ignis')
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--')

    # Gráfico 2: Comparativo de Taxa Balística (Bruta vs Filtrada)
    plt.subplot(2, 1, 2)
    plt.plot(time, delta_mass_raw, color='salmon', alpha=0.4, label='Taxa Bruta (Inviável)')
    plt.plot(time, delta_mass_filtered, color='darkred', linewidth=2, label='Taxa de Queima Tratada (g/s)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Variação mássica (g/s)')
    
    pico_taxa_real = np.max(delta_mass_filtered)
    plt.ylim(-0.5, pico_taxa_real * 1.4)
    
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--')

    plt.tight_layout()
    plt.savefig('variacao_massa.png', dpi=300)
    plt.show()
    
def main():
    time, mass = data_arquive_load(DATA_ARQUIVE_PATH)
    filtered_mass = filter.butterworth_filter(FC, NYQUIST, mass)
    delta_mass_raw = mass_derivate(mass, FREQUENCY_HZ)
    delta_mass_filtered = mass_derivate(filtered_mass, FREQUENCY_HZ)
    
    graffic_plot(time, mass, filtered_mass, delta_mass_raw, delta_mass_filtered)

main()