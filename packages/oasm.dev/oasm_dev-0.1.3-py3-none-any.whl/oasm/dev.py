import math
from . import *
try:
    from . import rtmq2
except:
    pass

LO = 0xfffff
HI = 0xfff00000

class bus(table):
    def __call__(self, key, *args):
        cfg = self.__dict__.get('cfg',None)
        if cfg not in (None,list):
            asm = rtmq2.asm
            asm.__enter__()
            asm.core = cfg.core
        if len(self) > 0 and self[-1][0].endswith('.'):
            if cfg is list:
                self[-1][0] += key
            else:
                self[-1][0] = self[-1][0][:-1]
                #print(f"sfs('{self[-1][0]}','{key}')")
                rtmq2.sfs(self[-1][0], key)
        elif type(key) is str and key[0] not in '&$':
            if len(self) == 0 or cfg is list:
                super().append([key])
            else:
                self[-1][0] = key
        else:
            args = (key,) + args
        if cfg is list:
            self[-1] += list(args)
        elif len(args) > 0:
            key = self[-1][0]
            func = rtmq2.__dict__.get(key,None)
            if func is None:
                if len(args) == 1:
                    #print(f"mov('{key}',{hex(args[0])})")
                    rtmq2.mov(key,args[0])
                else:
                    #print(f"mov('{key}',({hex(args[0])},{hex(args[1])}))")
                    rtmq2.mov(key,args)
            else:
                #print(f'{key}('+','.join(map(hex,args))+')')
                func(*args)
        if cfg not in (None,list):
            try:
                if len(rtmq2.asm) > 0:
                    cfg(rtmq2.asm(),dnld=0)
            finally:
                rtmq2.asm.__exit__(0,0,0)
        return self
    def __repr__(self):
        return '\n'.join(i[0]+'('+','.join(map(lambda v:hex(v) if type(v) is int else f"'{v}'",i[1:]))+')' for i in self[:])
    def rtmq2(self):
        if self.__dict__.get('cfg',None) is not list:
            return
        for i in self:
            key = i[0]
            func = rtmq2.__dict__.get(key,None)
            if func is None:
                if '.' in key:
                    key,sub = key.split('.')
                    #print(f"sfs('{key}','{sub}')")
                    rtmq2.sfs(key,sub)
                if len(i) == 2:
                    #print(f"mov('{key}',{hex(i[1])})")
                    rtmq2.mov(key,i[1])
                elif len(i) == 3:
                    #print(f"mov('{key}',({hex(i[1])},{hex(i[2])}))")
                    rtmq2.mov(key,i[1:])
            else:
                #print(f'{key}('+','.join(map(hex,i[1:]))+')')
                func(*i[1:])

bus = context(table=bus)

class bit_field:
    def __init__(self, *args):
        assert len(args) > 0, 'Empty bits field'
        #if len(args) == 1:
        #    msk = args[0]
        #    sca = int(math.log2(msk & (1 + ~msk)))
        #    assert (msk + sca) & msk == 0, 'Non-contiguous bits field'
        #elif len(args) == 2:
        self.rng = (min(args),max(args))
        self.msk = ((1<<(self.rng[1]+1-self.rng[0]))-1)<<self.rng[0]

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return (obj._val & self.msk) >> self.rng[0]

    def __set__(self, obj, val):
        obj._val &= ~self.msk
        obj._val |=  self.msk & (val << self.rng[0])
        
class port:
    def __init__(self, _key=None):
        self._key = self.__class__.__name__ if _key is None else _key

    def __call__(self, *args, **kwargs):
        bus(self._key)
        if len(args) == 0 and len(kwargs) == 0:
            return
        nargs = len(args)
        for i in args[::-1]:
            if type(i) in (tuple,list):
                nargs -= 1
            else:
                break
        self._val = 0 if nargs < 2 else args[0]
        for i, v in args[nargs:]:
            if type(i) in (tuple,list):
                bit_field(*i).__set__(self,v)
            elif self._val == 0:
                self._val = (v&1)<<i
            else:
                self._val |= (v&1)<<i
        for k, v in kwargs.items():
            setattr(self, k, v)
        if nargs == 0:
            val = self._val
            msk = None
        elif nargs == 1:
            val = args[0]
            msk = self._val if len(args)-nargs+len(kwargs) > 0 else None
        else:
            val = self._val
            msk = args[1]
        if msk is None:
            bus(val)
        else:
            bus(val,msk)
        return self
    
    def on(self, *args, **kwargs):
        self._val = 0
        if len(args) > 0:
            for i in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,-1)
                elif self._val == 0:
                    self._val = 1<<i
                else:
                    self._val |= 1<<i
        else:
            for k,v in kwargs.items():
                setattr(self, k, -1)
        msk = self._val
        self(-1, msk)
    
    def off(self, *args, **kwargs):
        self._val = 0
        if len(args) > 0:
            for i in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,-1)
                elif self._val == 0:
                    self._val = 1<<i
                else:
                    self._val |= 1<<i
        else:
            for k,v in kwargs.items():
                setattr(self, k, -1)
        msk = self._val
        self(0, msk)
    
    def set(self, *args, **kwargs):
        if len(args) > 0:
            self._val = 0
            for i,v in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,v)
                elif self._val == 0:
                    self._val = (v&1)<<i
                else:
                    self._val |= (v&1)<<i
            val = self._val
            self._val = 0
            for i,v in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,-1)
                elif self._val == 0:
                    self._val = 1<<i   
                else:
                    self._val |= 1<<i
            msk = self._val
        else:
            self._val = 0
            for k, v in kwargs.items():
                setattr(self, k, v)
            val = self._val
            self._val = 0
            for k, v in kwargs.items():
                setattr(self, k, -1)
            msk = self._val
        self(val, msk)

class pin:
    def __init__(self,port,sub=None,pos=None):
        self.port = port
        self.sub = sub
        if type(pos) is str:
            pos = getattr(port.__class__,pos,None)
            if type(pos) is bit_field:
                pos = pos.rng
        self.pos = pos

    def __call__(self, *args):
        if len(args) == 0:
            if self.pos is None:
                return rtmq2.R[self.port._key] if self.sub is None else rtmq2.R[self.port._key][self.sub]
            elif type(self.pos) in (tuple,list):
                return ((rtmq2.R[self.port._key] if self.sub is None else rtmq2.R[self.port._key][self.sub])>>self.pos[0])&((1<<(self.pos[1]+1-self.pos[0]))-1)
            else:
                return ((rtmq2.R[self.port._key] if self.sub is None else rtmq2.R[self.port._key][self.sub])>>self.pos)&1
        else:
            if self.pos is None:
                (self.port if self.sub is None else self.port[self.sub])(*args)
            else:
                (self.port if self.sub is None else self.port[self.sub]).set((self.pos,args[0]))
    
    def on(self):
        self(-1)
    
    def off(self):
        self(0)

class dev:
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            if isinstance(v,port):
                self.__dict__[k] = v

    def __setitem__(self, key, val):
        if type(key) is int:
            key = f'&{key:02x}'
        try:
            sub = super().__getattribute__(key)
        except:
            sub = None
        if isinstance(sub,port):
            if isinstance(self, ports):
                bus(self.__class__.__name__+f'.')
            if type(val) is tuple:
                if type(val[-1]) is dict:
                    sub(*val[:-1],**val[-1])
                else:
                    sub(*val)
            elif type(val) is table:
                sub(*val[:],**val.__dict__)
            else:
                sub(val)
        else:
            object.__setattr__(self, key, val)
        return val

    def __setattr__(self, key, val):
        try:
            sub = super().__getattribute__(key)
        except:
            sub = None
        if isinstance(sub,port):
            self[key] = val
        else:
            object.__setattr__(self, key, val)
        return val
    
class ports(port,dev):
    def __getattribute__(self, key):
        sub = super().__getattribute__(key)
        if isinstance(sub,port):
            bus(self._key+f'.')
        return sub

    def __getitem__(self, key):
        bus(self._key+f'.')
        if type(key) is int:
            key = f'&{key:02x}'
        key = str(key)
        return self.__dict__.get(key,port(key))