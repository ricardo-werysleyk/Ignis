import numpy as np

class InfraRed():
    def __init__(self, temp_max = 1010.0, latency = 5.0):
        self.temp_max = temp_max
        self.latency = latency
        self.temp_environment = 24.5
        
    def signal_read(self, t, t_ingnition, t_duration):
        t_end = t_ingnition + t_duration
        noise = np.random.normal(0, 6.0)
        
        if t_ingnition < t < t_end:
            return self.temp_max * (1 - np.exp(-self.latency * (t - t_ingnition))) + noise
        elif t > t_end:
            return self.temp_max * np.exp(-0.8 * (t - t_end)) + noise
        else:
            return self.temp_environment + np.random.normal(0, 0.4)