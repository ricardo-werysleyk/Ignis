import numpy as np

class Termopar:
    def __init__(self, peak_time, heating_hate = 15.0, temp_max = 1025.0):
        self.t_peak = peak_time
        self.heating_hate = heating_hate
        self.temp_max = temp_max
        self.temp_environment = 25.0
        self.upswing_window = 0.5
        
        # tempo da frente de chama atingir termopar
        self.t_starter_jump = self.t_peak - self.upswing_window
    
    def signal_read(self, t):
        noise = np.random.normal(0, 1.0)
        if t < self.t_starter_jump:
            return self.temp_environment + (t * self.heating_hate) + noise
        elif self.t_starter_jump <= t <= self.t_peak:
            proportion = (t - self.t_starter_jump) / self.upswing_window
            return self.temp_environment + (self.temp_max - self.temp_environment) * proportion + noise
        else:
            return (self.temp_max * np.exp(-0.2 * (t - self.t_peak))) + noise 