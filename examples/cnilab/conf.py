import sys

# Import analysis/plotting modules
import analysis.event
import plotting.image
import plotting.line
import numpy as np
from backend.record import add_record

# Set new random seed
np.random.seed()

# Specify the facility
state = {}
state['Facility'] = 'CNILab'

# Create a dummy facility
state['CNILab'] = {
    #'Repetition Rate' : 10,
    'SenderIP': '127.0.0.1',
    'SenderPort': 5678,
}

# This function is called for every single event
# following the given recipe of analysis
def onEvent(evt):
    # Processing rate [Hz]
    analysis.event.printProcessingRate()
    sys.stdout.flush()

    # Visualize detector image(s)
    for key in evt['photonPixelDetectors'].keys():
        plotting.image.plotImage(evt['photonPixelDetectors'][key], send_rate=10, group='Raw')

    # "Dark" correction
    img_dark = evt['photonPixelDetectors']['SIMCAM'].data - 1.
    add_record(evt["analysis"], "analysis", "dark_corrected", img_dark)
    plotting.image.plotImage(evt['analysis']['dark_corrected'], group='Corrected')

    # RMS value
    rms = evt['photonPixelDetectors']['SIMCAM'].data.std()
    add_record(evt['analysis'], 'analysis', 'RMS', rms)
    plotting.line.plotHistory(evt['analysis']['RMS'], history=10000)
