import numpy

class RingBuffer(object):
    def __init__(self, maxlen):
        self._index = 0
        self._len = 0
        self._maxlen = maxlen
        self._data = None
    def append(self, x):
        if(self._data is None):
            self._init_data(x)
        try:
            self._data[self._index] = x
        except ValueError:
            self._init_data(x)
            self._index = 0
            self._len = 0
            self._data[self._index] = x            

        self._data[self._index + self._maxlen] = x
        self._index = (self._index + 1) % self._maxlen
        if(self._len < self._maxlen):
            self._len += 1
        
    def _init_data(self, x):
        try:
            self._data = numpy.empty(tuple([2*self._maxlen]+list(x.shape)),
                                     x.dtype)
        except AttributeError:
            self._data = numpy.empty([2*self._maxlen], type(x))

    def __array__(self):
        return self._data[self._maxlen+self._index-self._len:self._maxlen+self._index]

    def __len__(self):
        return self._len

    def clear(self):
        self._len = 0
        self._index = 0

    @property
    def shape(self):
        if(len(self._data.shape) == 1):
            return (self._len)        
        else:
            return (self._len,)+self._data.shape[1:]

    def __getitem__(self, args):
        if(isinstance(args, slice)):
            start = self._maxlen+self._index-self._len
            if(args.start is None):
                if(args.step is not None and args.step < 0):
                    start = self._maxlen+self._index-1
            elif(args.start > 0):
                start += args.start
            elif(args.start < 0):
                start += args.start + self._len

            stop = self._maxlen+self._index
            if(args.stop is None):
                if(args.step is not None and args.step < 0):
                    stop = self._maxlen+self._index-self._len-1
            elif(args.stop > 0):
                stop += args.stop-self._len
            elif(args.stop < 0):
                stop += args.stop
            return self._data[start:stop:args.step]
        else:
            if args < 0:
                args = self._len + args
            return self._data[args+self._maxlen+self._index-self._len]



