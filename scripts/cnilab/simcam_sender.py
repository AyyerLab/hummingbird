import sys
import time
import numpy as np
import zmq
import msgpack
import msgpack_numpy
msgpack_numpy.patch()

from cnidet import atcore
atcore.initialize()

num_buffers = 10
det_num = 1
port = 5678
det_shape = (2160, 2560)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:%d' % port)
socket.setsockopt(zmq.SNDHWM, 2)
socket.setsockopt(zmq.SNDBUF, 100*1024**2)

det = atcore.ATDetector(det_num)
print('Sending from', det.get.CameraModel())
det.set.CycleMode('Continuous')

imsize = det.get.ImageSizeBytes()
buf = np.ones((num_buffers, imsize), dtype='u1')

log_counter = 0
det.flush()

for i in range(num_buffers):
    det.queue_buffer(buf[i])

stime = time.time()
det.AcquisitionStart()
while True:
    try:
        ret_buf, ret_size = det.wait_buffer(timeout=100)
    except atcore.ATCoreException:
        sys.stderr.write('\n')
        det.AcquisitionStop()
        det.flush()
        for i in range(num_buffers):
            det.queue_buffer(buf[i])
        det.AcquisitionStart()
        continue

    index = log_counter % num_buffers

    log_counter += 1

    evt = {}
    evt['data'] = buf[index].view('u2').reshape(det_shape[0], det_shape[1]).astype('f4')
    evt['name'] = 'SIMCAM'
    evt['meta'] = {'pixel_size': 6.5e-6, 'gain': 1.0}
    
    socket.send(msgpack.packb(evt))
    det.queue_buffer(buf[index])

    sys.stderr.write('\r%d %.3f Hz'%(log_counter, log_counter/(time.time()-stime)))
sys.stderr.write('\n')
