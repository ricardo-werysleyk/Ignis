import numpy as np

class LoadCell():
    def __init__(self, initial_mass = 70.0, natural_frequency = 35.0, damping = 4.0):
        self.initial_mass = initial_mass
        self.fn = natural_frequency
        self.gamma = damping
        self.noise_amplitude = 0.15
    
    def current_mass_calc(self, t, t_ingnition, t_duration):
        if t < t_ingnition:
            return self.initial_mass
        elif t > t_duration:
            return 0.0
        else:
            normalized_time = (t - t_ingnition)/t_duration #varia de 0 a 1
            # cosseno varia de -1 a 1, fazendo uma curva sigmoidal trigonométrica
            # curva provisória aproximada ate ter uma mais fiel a realidade pela literatura
            # r = a * p_atm ** n , bucando valores de a e n para queima livre fora do motor
            return self.initial_mass * (0.5 + 0.5 * np.cos(normalized_time * np.pi))
    
    # calcula o efeito mola em decorrer do alivio de massa no final da queima
    # causado pelo retorno da célula de carga para posição original
    def spring_effect_calc(self, t, t_end):
        if t >= t_end:
            t_elapsed = t_end - t
            # o efeito mola terá um "coice" iniciar configuravel, nesse caso de 5%
            # efeito sub amortecido - e**gamma*t faz a função decair para zero
            # o gráfico de amortecimento e efeito mola seguirá a função seno de 2pi de acordo com a frequencia e tempo passado
            return (self.initial_mass * 0.05) * np.exp(-self.gamma * t_elapsed) * np.sin(2 * np.pi * self.fn * t_elapsed)
        return 0.0
    
    def signal_read(self, t, t_ingnition, t_duration):
        t_end = t_ingnition + t_duration
        current_mass = self.current_mass_calc(t, t_ingnition, t_duration)
        spring = self.spring_effect_calc(t, t_end)
        white_noise = np.random.normal(0, self.noise_amplitude) #ruído eletrônico
        
        # somo os vetores de dados, e os limite entre -0.5 e massa inicial mais 2g
        return np.clip(current_mass + spring + white_noise, -0.5, self.initial_mass + 2.0)
        