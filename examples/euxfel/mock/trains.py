"""
For testing the trains-based EuXFEL backend, start the karabo server:

./karabo-bridge-server-sim 1234
    OR
./karabo-bridge-server-sim -d AGIPDModule -r 1234

from the karabo-bridge (https://github.com/European-XFEL/karabo-bridge-py).
and then start the Hummingbird backend:

./hummingbird.py -b examples/euxfel/mock/trains.py
"""
import plotting.image
import analysis.agipd
import analysis.event
from backend import add_record

state = {}
state['Facility'] = 'EuXFELtrains'
state['EuXFEL/DataSource'] = 'tcp://127.0.0.1:1234'
state['EuXFEL/DataFormat'] = 'Calib'
state['EuXFEL/MaxTrainAge'] = 4

# Use SelModule = None or remove key to indicate a full detector
# [For simulator, comment if running with full detector, otherwise uncomment]
#state['EuXFEL/SelModule'] = 0

event_number = 0
def onEvent(evt):
    global event_number
    event_number += 1
    #analysis.event.printKeys(evt)
    #analysis.event.printNativeKeys(evt)
    analysis.event.printProcessingRate()
    T = evt["eventID"]["Timestamp"]
    #print(event_number, T.timestamp, T.pulseId, T.cellId, T.trainId)

    # Full train(stack) of a single agipd module
    if 'EuXFEL/SelModule' in state and state['EuXFEL/SelModule'] != None:
        agipd_module = evt['photonPixelDetectors']['AGIPD'].data[:,state['EuXFEL/SelModule']]
    else:
        agipd_module = evt['photonPixelDetectors']['AGIPD'].data[:,8]

    # Gain doesn't make physical sense here since the shape is not the same
    agipd_gain = evt['photonPixelDetectors']['AGIPD'].data[:,-1]
    
    # Iterate through the pulses
    for i in range(len(agipd_module)):
        agipd_pulse = add_record(evt['analysis'], 'analysis', 'AGIPD', agipd_module[i])

        plotting.image.plotImage(agipd_pulse)