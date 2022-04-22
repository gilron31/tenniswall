import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sounddevice as sd

BASE_SAMPLE_FREQUENCY_HZ = 44100
DEFAULT_RECORDING_DURATION_S = 10
STFT_N_SAMPLES_PER_SEG = 100
STFT_OVERLAP_PER_SEG = 90
STFT_HPF_BIN_THRES = 3
DELIMITER = ','

def record_signal_with_sounddevice(fileName,fs = BASE_SAMPLE_FREQUENCY_HZ, duration=DEFAULT_RECORDING_DURATION_S):
	input(f"Will start recording for {duration} seconds")
	s = sd.rec(fs*duration, fs, channels = 1)
	sd.wait()
	print("Done recording")
	t = np.linspace(0, duration, fs*duration)
	np.savetxt(fileName,s,delimiter = DELIMITER)

def findContinuousHigh(sig,cutoff,amountOfSamplesRequired):
    highsFound = []
    amountAbove = 0
    for sampleInd,sample in enumerate(sig):
        if sample > cutoff:
            amountAbove += 1
            if amountAbove == amountOfSamplesRequired:
                highsFound.append(sampleInd - amountOfSamplesRequired)
                amountAbove = 0
        else:
            amountAbove = 0
    return highsFound

def putPeakLines(sig,cutoff,amountOfSamplesRequired):
	peaks = findContinuousHigh(sig,cutoff,amountOfSamplesRequired)
	for peak in peaks:
		plt.axvline(peak,color='r')

def detect_bangs(fileName,fs = BASE_SAMPLE_FREQUENCY_HZ, duration=DEFAULT_RECORDING_DURATION_S):
	s = np.genfromtxt(fileName,delimiter = DELIMITER)
	assert(len(s) == fs*duration)

	f, t, zxx = signal.stft(s, fs, nperseg = STFT_N_SAMPLES_PER_SEG, noverlap = STFT_OVERLAP_PER_SEG)
	hpf_power_signal = np.sum(abs(zxx[STFT_HPF_BIN_THRES:])**2, axis = 0)

	## this is for testing, in the end the function should return timestamps
	plt.figure()
	plt.subplot(2,1,1)
	plt.plot(hpf_power_signal)
	# You need to insert a cutoff and amountOfSamples according to the behaviour
	putPeakLines(hpf_power_signal,cutoff = 0.5,amountOfSamplesRequired= 10)
	plt.subplot(2,1,2)
	plt.plot(s)
	# You need to insert a cutoff and amountOfSamples according to the behaviour
	putPeakLines(s,cutoff = 0.5,amountOfSamplesRequired= 10)
	plt.show()




if __name__ == "__main__":
	# record_signal_with_sounddevice('3clapsGil.csv')
	detect_bangs('3clapsGil.csv')