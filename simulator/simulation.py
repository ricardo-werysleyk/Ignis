import numpy as np
import pandas as pd

from simulator.sensors.load_cell import LoadCell
from simulator.sensors.termopar import Termopar
from simulator.sensors.infrared import InfraRed

class Simulation():
    def __init__(self, frequency_hz = 860.0, total_time = 13.0, t_ignition = 0.5, burn_duration = 10.5, initial_mass = 70.0):        
        self.frequency_hz = frequency_hz
        self.total_time = total_time
        self.t_ignition = t_ignition
        self.burn_duration = burn_duration
        self.initial_mass = initial_mass

        # vetor de passo do gráfico "dt"
        self.time_vector = np.arange(0, self.total_time, 1.0/self.frequency_hz)        

    def simulate_data(self):
        self.balance = LoadCell(initial_mass = self.initial_mass)
        self.tp_start = Termopar(peak_time = 2.5, heating_hate = 12.0, temp_max = 1025.0)
        self.tp_mid = Termopar(peak_time = 8.5, heating_hate = 22.0, temp_max = 1040.0)
        self.pirometro = InfraRed()
        
        self.test_data = list()
        
        for t in self.time_vector:
            current_mass = self.balance.signal_read(t, self.t_ignition, self.burn_duration)
            t1 = self.tp_start.signal_read(t)
            t2 = self.tp_mid.signal_read(t)
            pyro_temp = self.pirometro.signal_read(t, self.t_ignition, self.burn_duration)
            
            linha = {
                "time" : t,
                "mass" : current_mass,
                "termopar_start": t1,
                "termopar_mid": t2,
                "infrared" : pyro_temp
            }
            
            self.test_data.append(linha)

        estructured_data = pd.DataFrame(self.test_data)

        try: 
            estructured_data.to_csv('data/dados_simulados.csv', index=False)
            return True
        except Exception as e:
            print(e)
            return False