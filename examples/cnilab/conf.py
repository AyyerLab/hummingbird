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
    #'SenderIP': '127.0.0.1',
    'SenderIP': '131.169.116.105',
    'SenderPort': 5678,
}

# This function is called for every single event
# following the given recipe of analysis
def onEvent(evt):
    # Processing rate [Hz]
    analysis.event.printProcessingRate()
    sys.stdout.flush()
    #my_data = evt['photonPixelDetectors']['iStar-sCMOS18F73-S'].data
    my_data = evt['photonPixelDetectors']['dude'].data
    print(my_data.shape)
    print(my_data.dtype)
    print(my_data.max())
    print(my_data.min())
    if np.isnan(np.min(my_data)) or None in my_data:
        print('noooooooooooooooooooo')


    # Visualize detector image(s)
    for key in evt['photonPixelDetectors'].keys():
        #plotting.image.plotImage(evt['photonPixelDetectors'][key], send_rate=10, group='Raw')
        plotting.image.plotImage(evt['photonPixelDetectors'][key], history=10, send_rate=10, group='Raw')

    # "Dark" correction
    #img_dark = evt['photonPixelDetectors']['iStar-sCMOS18F73-S'].data - 1.
    #img_dark = evt['photonPixelDetectors']['dude'].data - 1.
    #add_record(evt["analysis"], "analysis", "dark_corrected", img_dark)
    #plotting.image.plotImage(evt['analysis']['dark_corrected'], group='Corrected')

    # RMS value
    #rms = evt['photonPixelDetectors']['iStar-sCMOS18F73-S'].data.std()
    rms = evt['photonPixelDetectors']['dude'].data.std()
    add_record(evt['analysis'], 'analysis', 'RMS', rms)
    plotting.line.plotHistory(evt['analysis']['RMS'], history=10000)
