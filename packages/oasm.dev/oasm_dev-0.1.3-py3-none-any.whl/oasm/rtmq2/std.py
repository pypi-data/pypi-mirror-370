from . import *
from ..dev import *
    
led = port('led')

class rsm(port):
    master = bit_field(0)
    monitor = bit_field(1)
    timer = bit_field(2)

rsm = rsm()

class exc(port):
    halt = bit_field(0)
    resume = bit_field(1)
    tcs = bit_field(2)
    byzero = bit_field(3)
    ich = bit_field(4)
    dch = bit_field(5)
    unaligned = bit_field(6)
    fifo = bit_field(7)

exc = exc()

tim = port('tim')

class std(dev):
    C_STD = C_STD
    us = 250

    def boot(self):
        import os,sys
        with asm:
            path = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
            with open(os.path.join(path,self.__class__.__qualname__+'.bin'),'rb') as f:
                while True:
                    v = f.read(4)
                    if len(v) == 0:
                        break
                    asm(int.from_bytes(v))
            return asm()
        
    def nop(self, n = 1, hp = 0):
        bus('nop', n, hp)
        return self

    def hold(self, n = 1):
        return self.nop(n, 1)

    def pause(self, n = 1):
        return self.nop(n, 2)

    def timer(self, dur, us=False, strict=True, wait=1):
        if wait & 1:
            self.hold()
        if us:
            dur = round(dur * self.us)
        if type(dur) is int:
            if dur == 0:
                return
            dur = dur - 1
        tim(dur)
        (exc.on if strict else exc.off)(resume=1)
        rsm.on(timer=1)
        if wait >> 1:
            self.hold()
    
    def wait(self, **kwargs):
        rsm.on(**kwargs)
        std.hold()
        rsm.off(**kwargs)

std = std(**globals())