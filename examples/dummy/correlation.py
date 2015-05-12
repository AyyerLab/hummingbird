import analysis.event
import analysis.hitfinding
import plotting.image
import plotting.line
import plotting.correlation
import ipc
import random
from backend import ureg
import numpy

state = {
    'Facility': 'dummy',
    'Dummy': {
        'Repetition Rate' : 1,
        'Data Sources': {
            'CCD': {
                'data': lambda: numpy.random.rand(256,128),
                'unit': ureg.ADU,     
                'type': 'photonPixelDetectors'
            },
            'pulseEnergy1': {
                'data': lambda: random.random(),
                'unit': ureg.mJ,
                'type': 'pulseEnergies'
            }
        }        
    }
}

# PARAMETERS
# ----------
# hitfinding
# ----------
# threshold is expectation value of numpy.random.rand()
aduThreshold = 0.5
# lit pixels are half of total number of pixels
hitscoreMinCount = 16384
# -----------
# correlation
# -----------
correlationMinX = 0.0
correlationMaxX = 1.0
correlationNbinsX = 10
correlationMinY = 16000
correlationMaxY = 16768
correlationNbinsY = 10


def onEvent(evt):
    # Look at available sources
    analysis.event.printKeys(evt)
    analysis.event.printKeys(evt['photonPixelDetectors'])

    # Plot CCD/PulseEnergy
    plotting.image.plotImage(evt['photonPixelDetectors']['CCD'], vmin=0.9, vmax=1)
    plotting.line.plotHistory(evt['pulseEnergies']['pulseEnergy1'])
    
    # Hitfinding
    hit, evt["hitscore"] = analysis.hitfinding.countLitPixels(evt['photonPixelDetectors']['CCD'], aduThreshold, hitscoreMinCount)
    
    # Plot Hitscore
    plotting.line.plotHistory(evt["hitscore"])

    # Count Hits and Blanks
    evt["nrHits"], evt["nrBlanks"] = analysis.hitfinding.countHits(hit)
    print "%d lit pixels (%d accumulated hits)" % (evt["hitscore"].data, evt["nrHits"].data)

    # correlation normalizes by the mean of the accumulated x/y-arrays, if x or y are zero for the first events you may receive:
    #    RuntimeWarning: invalid value encountered in double_scalars
    plotting.correlation.plotCorrelation(evt['pulseEnergies']['pulseEnergy1'], evt["hitscore"])
    
    # correlate2D takes arguments x, y in 2D image, and optional arguments for xMin, xMax, xNbins, yMin, yMax, yNbins
    # correlationMinX, correlationMaxX, and correlationNbinsX are equal to default values of xMin, xMax, and xNbins
    #    => only need to set yMin, yMax, yNbins
    plotting.correlation.plotHeatmap(evt['pulseEnergies']['pulseEnergy1'], evt["hitscore"], yMin=correlationMinY, yMax=correlationMaxY, yNbins=correlationNbinsY)

    # Processing rate
    analysis.event.printProcessingRate()