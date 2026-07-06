import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

import core.filters as filter
from simulator.simulation import Simulation

DATA_ARQUIVE_PATH = 'data/dados_simulados.csv'
# Configuração Firebox
FREQUENCY_HZ = 860.0 # frequência do ads1115
TOTAL_TIME = 16.0
T_IGNITION = 0.5
BURN_DURATION = 13.5
INITIAL_MASS = 70.0

# Frequencia de corte e constante para filtro
FC = 1.0  
NYQUIST = FREQUENCY_HZ / 2.0

def data_arquive_load(data_path):
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        time = df["time"].values.astype(float)
        mass = df["mass"].values.astype(float)
        t1 = df["termopar1"].values.astype(float)
        t2 = df["termopar2"].values.astype(float)
        pyro = df["infrared"].values.astype(float)
        return time, mass, t1, t2, pyro
    else:
        raise FileNotFoundError(f"Erro Crítico: O arquivo {data_path} não foi localizado na pasta.")

def mass_derivate(mass, fs):
    dt = 1.0/fs
    delta_mass = -np.gradient(mass, dt)
    return np.clip(delta_mass, 0, None)

def graffic_assembly(time, mass_raw, mass_filtered, delta_mass_raw, delta_mass_filtered, termopar1, termopar2, pyro):
    plt.close('all')
    plt.figure(figsize=(10,8))
    
    # Gráfico 1: Comparativo de Massa (Bruta vs Filtrada)
    plt.subplot(3, 1, 1)
    plt.plot(time, mass_raw, color='gray', alpha=0.5, label='Massa Bruta (Com Ruído)')
    plt.plot(time, mass_filtered, color='blue', linewidth=2, label='Massa Filtrada (Butterworth)')
    plt.ylabel('Massa do Propelente (g)')
    plt.title('Análise de Sinais da Queima KNSU - Ignis')
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--')

    # Gráfico 2: Comparativo de Taxa Balística (Bruta vs Filtrada)
    plt.subplot(3, 1, 2)
    plt.plot(time, delta_mass_raw, color='salmon', alpha=0.4, label='Taxa Bruta (Inviável)')
    plt.plot(time, delta_mass_filtered, color='darkred', linewidth=2, label='Taxa de Queima Tratada (g/s)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Variação mássica (g/s)')
    
    pico_taxa_real = np.max(delta_mass_filtered)
    plt.ylim(-0.5, pico_taxa_real * 1.4)
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--')
    
    # Gráfico 3: Comparativo da temperatura dos termopares e sensor infravermelho
    plt.subplot(3, 1, 3)
    plt.plot(time, termopar1, color='red', alpha=0.4, label='Termopar base')
    plt.plot(time, termopar2, color='darkred', linewidth=2, label='Termopar meio')
    plt.plot(time, pyro, color='darkblue', linewidth=2, label='Pirometro')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Temperatura (°C)')

    plt.tight_layout()
    plt.savefig('variacao_massa.png', dpi=300)
    plt.show()
    
def main():
    if os.path.exists(DATA_ARQUIVE_PATH):
        try:
            os.remove(DATA_ARQUIVE_PATH)
        except Exception as e:
            print(f"Aviso: Não foi possível limpar o arquivo antigo: {e}")
    
    simulation = Simulation(FREQUENCY_HZ, TOTAL_TIME, T_IGNITION, BURN_DURATION, INITIAL_MASS)
    
    if simulation.simulate_data():    
        time, mass, t1, t2, pyro = data_arquive_load(DATA_ARQUIVE_PATH)
        filtered_mass = filter.butterworth_filter(FC, NYQUIST, mass)
        delta_mass_raw = mass_derivate(mass, FREQUENCY_HZ)
        delta_mass_filtered = mass_derivate(filtered_mass, FREQUENCY_HZ)
        
        graffic_assembly(time, mass, filtered_mass, delta_mass_raw, delta_mass_filtered, t1, t2, pyro)
    else:
        print("Erro na simulação")

main()