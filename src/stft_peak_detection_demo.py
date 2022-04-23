import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sounddevice as sd
from matplotlib.widgets import Slider, Button


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

def findPeaks(sig,cutoff,amountOfSamplesRequired,amountOfStrikesAllowed,minTimeBetweenPeaks):
	highsFound = []
	amountAbove = 0
	curAmountOfStrikes = amountOfStrikesAllowed
	for sampleInd,sample in enumerate(sig):
		if sample > cutoff:
			amountAbove += 1
			if amountAbove == amountOfSamplesRequired:
				peakInd = sampleInd - amountOfSamplesRequired - (amountOfStrikesAllowed - curAmountOfStrikes)+1
				if len(highsFound) == 0 or peakInd - highsFound[-1] > minTimeBetweenPeaks: 
					highsFound.append(sampleInd - amountOfSamplesRequired - (amountOfStrikesAllowed - curAmountOfStrikes)+1)
				amountAbove = 0
				curAmountOfStrikes = amountOfStrikesAllowed
		else:
			curAmountOfStrikes -= 1
			if curAmountOfStrikes < 0 or amountAbove == 0:
				amountAbove = 0
				curAmountOfStrikes = amountOfStrikesAllowed
	return highsFound

def putPeakLines(ax,sig,cutoff,amountOfSamplesRequired,amountOfStrikesAllowed = 0,minTimeBetweenPeaks = -1):
	peaks = findPeaks(sig,cutoff,amountOfSamplesRequired,amountOfStrikesAllowed,minTimeBetweenPeaks)
	hor_line = ax.axhline(cutoff,color='r')
	vert_lines = []
	for peak in peaks:
		vert_lines.append(ax.axvline(peak,color='r'))
	return hor_line,vert_lines

def detect_bangs(fileName,ax,fs = BASE_SAMPLE_FREQUENCY_HZ, duration=DEFAULT_RECORDING_DURATION_S):
	s = np.genfromtxt(fileName,delimiter = DELIMITER)
	assert(len(s) == fs*duration)

	f, t, zxx = signal.stft(s, fs, nperseg = STFT_N_SAMPLES_PER_SEG/10, noverlap = STFT_OVERLAP_PER_SEG)
	hpf_power_signal = np.sum(abs(zxx[STFT_HPF_BIN_THRES:])**2, axis = 0)
	energy_no_hpf = np.sum(abs(zxx)**2, axis = 0)

	## this is for testing, in the end the function should return timestamps
	plt.figure()
	plt.subplot(2,1,1)
	plt.plot(hpf_power_signal,'o')
	# You need to insert a cutoff and amountOfSamples according to the behaviour
	putPeakLines(ax,hpf_power_signal,cutoff = 0.0001,amountOfSamplesRequired= 20,amountOfStrikesAllowed=3,minTimeBetweenPeaks=1000)
	plt.subplot(2,1,2)
	plt.plot(energy_no_hpf,'o')
	# You need to insert a cutoff and amountOfSamples according to the behaviour
	putPeakLines(ax,energy_no_hpf,cutoff = 0.015,amountOfSamplesRequired= 10,amountOfStrikesAllowed=3,minTimeBetweenPeaks=1000)
	plt.show()


def slidersForParameters(fileName,fs = BASE_SAMPLE_FREQUENCY_HZ, duration=DEFAULT_RECORDING_DURATION_S):
	s = np.genfromtxt(fileName,delimiter = DELIMITER)

	f, t, zxx = signal.stft(s, fs, nperseg = STFT_N_SAMPLES_PER_SEG, noverlap = STFT_OVERLAP_PER_SEG)
	s = np.sum(abs(zxx[STFT_HPF_BIN_THRES:])**2, axis = 0)
	# energy_no_hpf = np.sum(abs(zxx)**2, axis = 0)

	fig,ax = plt.subplots()
	ax.plot(s,'o')
	init_cutoff = np.median(s) / 2
	init_amountOfSamples = 20
	init_amountOfStrikes = 3
	init_minTimeBetweenPeaks = 1000
	fig.subplots_adjust(bottom=0.21)

	hor_line,vert_lines = putPeakLines(ax,s,init_cutoff,init_amountOfSamples,init_amountOfStrikes,init_minTimeBetweenPeaks)
	axcutoff = plt.axes([0.25, 0.01, 0.65, 0.03])
	cutoff_slider = Slider(
		ax=axcutoff,
		label='Cutoff',
		valmin=0,
		valmax= np.percentile(s,99),
		valinit=init_cutoff,
	)
	axamountOfSamples = plt.axes([0.25, 0.06, 0.65, 0.03])
	amountOfSamples_slider = Slider(
		ax=axamountOfSamples,
		label='Amount Of Samples',
		valmin=5,
		valmax=500,
		valinit=init_amountOfSamples
	)

	axamountOfStrikes = plt.axes([0.25, 0.1, 0.65, 0.03])
	amountOfStrikes_slider = Slider(
		ax=axamountOfStrikes,
		label='Amount of Strikes',
		valmin=0,
		valmax=50,
		valinit=init_amountOfStrikes,
	)

	def update(val,lines):
	
	# print(vert_lines)
		lines.hor_line.remove()
		for vert_line in lines.vert_lines:
			vert_line.remove()
		lines.hor_line,lines.vert_lines = putPeakLines(ax,s,cutoff_slider.val,int(amountOfSamples_slider.val),int(amountOfStrikes_slider.val),init_minTimeBetweenPeaks)

	saveax = plt.axes([0.35, 0.9, 0.3, 0.04])
	button = Button(saveax, 'Save Parameters', hovercolor='0.975')


	def saveParameters(event):
		open('Parameters.txt','w').write(f"cutoff = {cutoff_slider.val}\namountOfSamples = {amountOfSamples_slider.val}\namountOfStrikes = {amountOfStrikes_slider.val}")
	button.on_clicked(saveParameters)
	
	
	class allLines:
		def __init__(self,hor_line,vert_lines):
			self.hor_line = hor_line
			self.vert_lines = vert_lines
	lines = allLines(hor_line,vert_lines)
	cutoff_slider.on_changed(lambda val: update(val,lines))
	amountOfSamples_slider.on_changed(lambda val: update(val,lines))
	amountOfStrikes_slider.on_changed(lambda val: update(val,lines))
	plt.show()
	
	
 
	
if __name__ == "__main__":
	# record_signal_with_sounddevice('10BallsOnWalls.csv')
	# detect_bangs('5ballsOnWall.csv')
	slidersForParameters('10BallsOnWalls.csv')