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
socket.setsockopt(zmq.SNDHWM, 2)
socket.setsockopt(zmq.SNDBUF, 100*1024**2)

while True:
    evt = {}
    evt['data'] = np.pad(np.random.normal(0, 0.5, (2000, 2000)).astype('f4'), ((20,), (80,)), mode='constant')
    evt['name'] = 'SIMCAM'
    evt['meta'] = {'pixel_size': 6.5e-6, 'gain': 1.0}
    
    socket.send(msgpack.packb(evt))
    time.sleep(0.01)
