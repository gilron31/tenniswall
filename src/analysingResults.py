from matplotlib import pyplot as plt
import numpy as np
def viewAllPeaks(allPeaks):
    """Plots peaks from all mics

    Args:
        allPeaks (List<array>): List of arrays of the peaks for each of the microphones.
    """
    for peaks in allPeaks:
        plt.plot(peaks,peaks,'o')
    plt.show()

def offsetOfAllPeaks(allPeaks,method):
    """Returns offset needed to take each set of peaks from different microphone according to given method.
    The offsets are treated respectively to the first set of peaks.

    Args:
        allPeaks (List<array>): List of arrays of the peaks for each of the microphones.
        method (function): Function by which the offset is calculated. F.E. lambda x: x[0] will make all the sets start at the same peak
    
    Returns:
        offsets (array): array containing the offset required for each mic to bring it to the first mic.
    """


    offsetOfFirst = method(allPeaks[0])
    offsets = np.zeros(len(allPeaks))
    for micInd,peaks in enumerate(allPeaks):
        offsets[micInd] = offsetOfFirst - method(peaks)
    return offsets

def offsetAccordingToOffsets(allPeaks,offsets):
    """Return new list of arrays of peaks after offsetting them by given offset list

    Args:
        allPeaks (List<array>): List of arrays of the peaks for each of the microphones
        offsets (_type_): _description_
    """
    return [peaks + offset for peaks,offset in zip(allPeaks,offsets)]


def main():
    allPeaks = [np.array([0,2,4]),np.array([1,2,3])]
    offsets = offsetOfAllPeaks(allPeaks,lambda x: x[-1])
    shiftedPeaks = offsetAccordingToOffsets(allPeaks,offsets)
    viewAllPeaks(shiftedPeaks)

if __name__ == '__main__':
    main()




