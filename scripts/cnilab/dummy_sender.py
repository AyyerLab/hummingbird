import time
import numpy as np
import zmq
import msgpack
import msgpack_numpy
msgpack_numpy.patch()

port = 5678

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:%d' % port)

while True:
    evt = {}
    evt['data'] = np.random.normal(0, 0.5, (200, 200))
    evt['name'] = 'SIMCAM'
    evt['meta'] = {'pixel_size': 6.5e-6, 'gain': 1.0}
    
    socket.send(msgpack.packb(evt))
    time.sleep(0.01)
