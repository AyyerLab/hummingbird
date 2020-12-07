import sys

# Import analysis/plotting modules
import analysis.event
import plotting.image
import plotting.line
import numpy as np
import h5py as h5
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
    #'SenderIP': '131.169.224.229', #office pc
    'SenderPort': 5678,
}

if state['CNILab']['SenderIP'] != '131.169.116.105':
    name = 'test'
else:
    name = 'iStar-sCMOS18F73-S'

data_sum = None
do_dark_correction = False
if do_dark_correction:
    dark = []
    dpath = '/home/wittetam/CNIDetector/data/raw/'
    fname = 'Run22_0000.h5'
    with h5.File(dpath+fname, 'r') as f:
        for key in f:
            dark.append(np.array(f[key]))
    dark = np.mean(np.array(dark), axis=0)
# This function is called for every single event
# following the given recipe of analysis
def onEvent(evt):
    global data_sum
    # Processing rate [Hz]
    analysis.event.printProcessingRate()
    sys.stdout.flush()
    my_data = evt['photonPixelDetectors'][name].data
    if data_sum is None:
        if do_dark_correction:
            data_sum = np.copy(my_data-dark)
        else:
            data_sum = np.copy(my_data)
    else:
        if do_dark_correction:
            data_sum += my_data - dark
        else:
            data_sum += my_data
    
    # Visualize detector image(s)
    for key in evt['photonPixelDetectors'].keys():
        print(key)
        plotting.image.plotImage(evt['photonPixelDetectors'][key], send_rate=10, group='Raw')

    if do_dark_correction:
        # "Dark" correction
        img_dark = evt['photonPixelDetectors'][name].data - dark
        add_record(evt["analysis"], "analysis", "dark_corrected", img_dark)
        plotting.image.plotImage(evt['analysis']['dark_corrected'], group='Corrected')

        #Accumulated image
        add_record(evt['analysis'], 'analysis', 'accumulated', data_sum)
        plotting.image.plotImage(evt['analysis']['accumulated'], group='Corrected')

    # RMS value
    rms = evt['photonPixelDetectors'][name].data.std()
    add_record(evt['analysis'], 'analysis', 'RMS', rms)
    plotting.line.plotHistory(evt['analysis']['RMS'], history=10000)
