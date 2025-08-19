import os,sys
from osym import rpc
from osym.rpc import node
rpc.pexec(node.template.replace('node',os.path.basename(__file__).split('.')[0]),globals())

_shutter = 1
def shutter(val=None):
    global _shutter
    if val is None:
        return _shutter
    else:    
        _shutter = val

repeats = 100

from osym import *
from osym.io import *
Env[0] = globals()
Load()

#from osym import rpc;test=rpc.caller('test');print(test.repeats,test.shutter())