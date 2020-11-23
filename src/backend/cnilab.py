"""Creates Hummingbird events for CNI Lab experiments"""
import time
import random
from backend.event_translator import EventTranslator
from backend.record import add_record
from backend import Worker
from . import ureg
import numpy
import ipc
import zmq
import msgpack
import msgpack_numpy
msgpack_numpy.patch()

class CNILabTranslator(object):
    """Creates Hummingbird events for CNI Lab experiments"""
    def __init__(self, state):
        self.library = 'CNILab'
        self.state = state
        self.keys = set()
        self.keys.add('analysis')
        self.detnames = set()

        if 'SenderIP' not in self.state['CNILab']:
            print('No experiment sender specified. Showing random data')
            self.socket = None
        else:
            port = self.state['CNILab']['SenderPort'] if 'SenderPort' in self.state['CNILab'] else 5678
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            self.socket.setsockopt(zmq.SUBSCRIBE, b'')
            self.socket.connect('tcp://%s:%d' % (self.state['CNILab']['SenderIP'], port))

        self._last_event_time = -1

    def next_event(self):
        """Generates and returns the next event"""
        evt = {}        
        
        # Check if we need to sleep
        self._sleep_check()

        if 'SenderIP' not in self.state['CNILab']:
            # Generate a simple CCD as default
            evt['CCD'] = numpy.random.rand(128, 128)
            self.keys.add('photonPixelDetectors')
            return EventTranslator(evt, self)

        try:
            edict = msgpack.unpackb(self.socket.recv(flags=0, copy=True, track=False))
            evt[edict['name']] = edict['data']
            self.keys.add('photonPixelDetectors')
            self.detnames.add(edict['name'])
        except (IndexError, StopIteration) as e:
            logging.warning('End of Run.')
            if 'end_of_run' in dir(Worker.conf):
                Worker.conf.end_of_run()
            ipc.mpi.slave_done()
            return None

        return EventTranslator(evt, self)

    def translate(self, evt, key):
        """Returns a dict of Records that match a given Humminbird key"""
        values = {}
        if 'SenderIP' not in self.state['CNILab']:
            if(key == 'photonPixelDetectors'):
                # Translate default CCD as default
                add_record(values, key, 'CCD', evt['CCD'], ureg.ADU)
            if(values == {}):
                raise RuntimeError('%s not found in event' % (key))
            return values
        
        if key == 'photonPixelDetectors':
            for name in self.detnames:
                if name in evt:
                    add_record(values, key, name, evt[name])

        if values == {} and not key == 'analysis':
            raise RuntimeError('%s not found in event' % (key))
        return values

    def event_keys(self, _):
        """Returns the translated keys available"""
        return list(self.keys)

    def event_native_keys(self, evt):
        """Returns the native keys available"""
        return evt.keys()

    def init_detectors(self, state):
        """
        A dummy placeholder for the initialization of detector objects, this is the place to 
        switch between different reading modes (e.g. calibrated or raw)
        """
        pass
    
    def event_id(self, _):
        """Returns an id which should be unique for each
        shot and increase monotonically"""
        return float(time.time())

    def event_id2(self, _):
        """Returns an alternative id, which is just a copy of the usual id here"""
        return self.event_id(0)

    def _sleep_check(self):
        if self._last_event_time > 0:
            rep_rate = 1
            if 'Repetition Rate' in self.state['CNILab']:
                rep_rate = self.state['CNILab']['Repetition Rate'] / float(ipc.mpi.nr_workers())
            else:
                return
            target_t = self._last_event_time+1.0/rep_rate
            t = time.time()
            if t < target_t:
                time.sleep(target_t - t)
        self._last_event_time = time.time()
