import numpy as np
import pandas as pd

from sensors.load_cell import LoadCell

# Configuração Firebox
FREQUENCY_HZ = 860.0 # frequência do ads1115
total_time = 16.0
t_ignition = 0.5
burn_duration = 13.5

# vetor de passo do gráfico "dt"
time_vector = np.arange(0, total_time, 1.0/FREQUENCY_HZ)

balance = LoadCell(initial_mass = 70.0)

test_data = list()

for t in time_vector:
    current_mass = balance.signal_read(t, t_ignition, burn_duration)
    
    linha = {
        "time" : t,
        "mass" : current_mass
    }
    
    test_data.append(linha)

print(test_data)

estructured_data = pd.DataFrame(test_data)

print(estructured_data)