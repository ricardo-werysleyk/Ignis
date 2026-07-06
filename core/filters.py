from scipy.signal import butter, filtfilt

def butterworth_filter(fc, nyquist, raw_mass):
    b, a = butter(N=4, Wn=fc/nyquist, btype='low')
    return filtfilt(b, a, raw_mass)