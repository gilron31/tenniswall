import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sounddevice as sd

BASE_SAMPLE_FREQUENCY_HZ = 44100*8
DEFAULT_RECORDING_DURATION_S = 10
STFT_N_SAMPLES_PER_SEG = 100
STFT_OVERLAP_PER_SEG = 90
STFT_HPF_BIN_THRES = 3

def record_signal_with_sounddevice(fs, duration):
	input(f"Will start recording for {duration} seconds")
	s = sd.rec(fs*duration, fs, channels = 1)
	sd.wait()
	t = np.linspace(0, duration, fs*duration)
	print("Done recording")
	return t, [x[0] for x in s] #sd returns a vector of singletons, reformatting. 

def detect_bangs(s, fs, duration):
	assert(len(s) == fs*duration)

	f, t, zxx = signal.stft(s, fs, nperseg = STFT_N_SAMPLES_PER_SEG, noverlap = STFT_OVERLAP_PER_SEG)
	hpf_power_signal = np.sum(abs(zxx[STFT_HPF_BIN_THRES:])**2, axis = 0)

	## this is for testing, in the end the function should return timestamps
	plt.figure()
	plt.subplot(2,1,1)
	plt.plot(t, hpf_power_signal, 'x')
	plt.subplot(2,1,2)
	plt.plot(np.linspace(0, duration, fs*duration), s, 'x')
	plt.show()





if __name__ == "__main__":
	t, s = record_signal_with_sounddevice(BASE_SAMPLE_FREQUENCY_HZ, DEFAULT_RECORDING_DURATION_S)
	detect_bangs(s, BASE_SAMPLE_FREQUENCY_HZ, DEFAULT_RECORDING_DURATION_S)