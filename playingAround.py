import numpy as np
import sounddevice as sd
from matplotlib import pyplot as plt
from time import sleep

def energyOfSlot(signal,slotSize):
    cutoffedSignal = signal[:len(signal) - (len(signal) % slotSize)]
    print(cutoffedSignal.shape)
    reshapedSignal = cutoffedSignal.reshape([-1,slotSize])
    reshapedSignal **= 2
    reshapedSignal = np.sum(reshapedSignal,axis = 1)
    return reshapedSignal

def recordAndSave(filename,duration=5,fs = 44100):
    myrecording = sd.rec(int(duration * fs), samplerate=fs,channels=1)
    print("Started recording!")
    sleep(duration)
    print("Finished recording!")
    np.savetxt(filename,myrecording,delimiter = ',')

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


def playingWithRecording():
    sig = np.genfromtxt('5ballsOnWall.csv',delimiter = ',')
    energy = energyOfSlot(sig,10)
    energy = np.log(energy + 1)
    plt.plot(energy,'o')
    cutoff = 0.1
    amount = 5
    peaks = findContinuousHigh(energy,cutoff,amount)
    for peak in peaks:
        plt.axvline(peak)
    plt.show()
if __name__ == '__main__':
    playingWithRecording()
    # recordAndSave('5ballsOnWall.csv',duration= 10)