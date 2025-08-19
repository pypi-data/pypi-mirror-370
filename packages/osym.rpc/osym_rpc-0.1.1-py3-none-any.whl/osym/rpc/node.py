import os,sys
from osym import rpc
__dirname__ = os.path.dirname(__file__)
sys.path.append(__dirname__)
if __name__ == '__main__':
    from osym.rpc import node
    import time
    mqtt = rpc.server('node',node.__dict__).mqtt
    node.mqtt = mqtt
    node.init()
    node.restart()
    tic = time.time()
    while True:
        mqtt.loop(node.timeout)
        toc = time.time()
        if toc - tic > 0.99*node.timeout:
            node.run()
            tic = toc
            if os.path.basename(__file__) == 'nod'+'e.py':
                node.status()

import threading,queue    
__size__ = os.path.getsize(__file__)
timeout = 1
fifo = queue.SimpleQueue()
mp = rpc.mp

def reload(code=None):    
    from rpc import node
    rpc.reload(node,code=code)

_stop = False
def restart():
    global _stop
    for thread in threading.enumerate():
        if thread.name == 'node_loop':
            _stop = True
            thread.join()
            break
    _stop = False
    def target(*args):
        while not _stop and loop():
            pass
    threading.Thread(target=target,name='node_loop',daemon=True).start()

def init():
    pass
    
def run():
    pass

def loop():
    pass

import inspect
with open(__file__) as f:
    f.readline();f.readline()
    template = '\n'.join([f.readline() for i in range(inspect.currentframe().f_lineno-6)])

import sys,subprocess,time,platform

_nodes = {}
def start(name):
    _node = _nodes.get(name,None)
    if _node is None:
        fileName = os.path.join(os.path.dirname(__file__),name+'.py')
        _node = None
        # if the file does not exist in this platform
        if not os.path.exists(fileName):
            err = 0
        else:
            _node = subprocess.Popen([sys.executable, fileName])
            time.sleep(1)
            err = _node.poll()
        if err is not None: 
            return rpc.promise(print)
        print(f'{time.strftime("%H:%M:%S")} start {name}')
        _nodes[name] = _node
        return platform.node()

def kill(name,restart=False):
    _node = _nodes.get(name,None)
    if _node is not None:
        _node.kill()
        del _nodes[name]
        time.sleep(1)
        print(f'{time.strftime("%H:%M:%S")} kill {name}')
    if restart:
        return start(name)
    return rpc.promise(print) if node is None else platform.node()

def status(name = None):
    import psutil
    info = {}
    keys = list(_nodes.keys())
    names = keys if name is None else [name]
    for name in names:
        _node = _nodes.get(name, None)
        if _node is not None:
            info[name] = [True, platform.node()]

    # get cpu usage information
    cpu = psutil.cpu_percent()
    memo = psutil.virtual_memory().percent

    info['node'] = [platform.node(), cpu, memo] 
    mqtt.publish('node/status/', mp.dumps(info))
