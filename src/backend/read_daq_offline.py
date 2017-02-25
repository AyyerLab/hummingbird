import numpy
import h5py
import time
import os


class DAQReader(object):
    def __init__(self, experiment_dir):
        self._dir = experiment_dir
        #self._runnr = runnr

    def get_tof(self, event_id):
        all_files = os.listdir(self._dir)
        
        for this_file in all_files:
            with h5py.File(os.path.join(self._dir, this_file), "r") as file_handle:
                file_event_ids = file_handle["Experiment/BL1/ADQ412 GHz ADC/CH00/TD.event"]
                if event_id in file_event_ids:
                    index = list(file_event_ids).index(event_id)
                    tof_data = file_handle["Experiment/BL1/ADQ412 GHz ADC/CH00/TD"][index, :]
                    return tof_data
        return None

if __name__ == "__main__":
    reader = DAQReader("/data/beamline/current/raw/hdf/block-01/exp2/")
    start_id = 3584520
    for event_id in range(start_id, start_id+100):
        tof_trace = reader.get_tof(event_id)
        if tof_trace is not None:
            print tof_trace
            print tof_trace.shape
        else:
            print "No tof data"
