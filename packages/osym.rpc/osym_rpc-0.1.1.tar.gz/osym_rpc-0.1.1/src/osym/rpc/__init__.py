from paho.mqtt import client as mqtt_client
import os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
import msgpack as mp
import numpy as np
from uuid import uuid4
from ..io import *

broker = 'localhost'
port = 1883
username = 'emqx_test'
password = 'emqx_test'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)        

topic = ''
payload = None
def on_message(client, userdata, msg):
    global topic, payload
    topic = msg.topic
    payload = msg.payload

clients = {}     
def create(name=None, start=True):
    if name is not None:
        client = clients.get(name, None)
        if client is not None:
            return client
    client = mqtt_client.Client(client_id=name)
    if name is not None:
        clients[name] = client
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password=password)
    client.connect(broker, port)
    if start:
        client.loop_start()
    return client

def pexec(text, env={}):# globals(), locals()
    ret = None
    if text.endswith('.py') and os.path.exists(text):
        env.update({
            '__file__': text,
            '__name__': '__main__',
        })
        try:
            with open(text, 'rb') as f:
                exec(compile(f.read(), text, 'exec'), env, env)
        except Exception as e:
                ret = e
    else:
        try:
            ret = eval(compile(text, '<stdin>', 'eval'), env, env)
        except:
            try:
                exec(compile(text, '<stdin>', 'exec'), env, env)
            except Exception as e:
                ret = e
    return ret

def pcall(func, *args, **kwargs):
    ret = None
    try:
        ret = func(*args,**kwargs)
    except Exception as e:
        ret = e
    return ret
        
class future:
    def __init__(self, setup):
        self.setup = setup
    def __call__(self, topic):
        return pcall(self.setup, topic)
                      
class server:
    def __init__(self, name, env=None, mqtt=None, loc='LAN'):
        if mqtt is None:
            mqtt = create(start=False)
        self.__name__ = name
        self.loc = loc
        self.mqtt = mqtt
        self.env = [env or {},Env[1]]
        self.objs = {}
        topic = loc + '/' + name + '/#'
        mqtt.subscribe(topic)
        mqtt.message_callback_add(topic, self)
    def dump(self, obj, deep):
        if not (deep and (type(obj) is complex or isinstance(obj,np.ndarray) or isinstance(obj,(np.bool_,np.number)))):
            ref = id(obj)
            self.objs[ref] = obj
            return {'':ref,type(obj).__module__+'.'+type(obj).__name__:repr(obj)}
    def load(self, msg):
        return mp.loads(msg,object_hook=lambda obj:Restore(obj,self.env,lambda ref,obj:self.objs.get(ref,obj)),strict_map_key=False)
    def __call__(self, client, userdata, msg):
        topic,msg = msg.topic,msg.payload
        try:
            if topic[-1] == '/':
                key = Expr(*topic[:-1].split('/')[-1].split('.'))
                ret = Eval(key,self.env)
                if len(msg) == 0:
                    if callable(ret):
                        ret = pcall(ret)
                else:
                    val = self.load(msg)
                    if callable(ret):
                        if isinstance(val,(tuple,list)):
                            ret(*val)
                        else:
                            ret(val)
                    else:
                        Set(key,val,env=self.env)
                    ret = val
            else:
                ret = Eval(self.load(msg),self.env)
                if type(ret) is future:
                    return ret(topic)
        except Exception as e:
            ret = e
        client.publish(topic[len(self.loc)+1:],mp.dumps(ret,default=lambda obj:Dump(obj,False,self.dump)),qos=2)
    def __repr__(self):
        return self.__name__
            
class caller:
    _Pool = ThreadPoolExecutor()
    def __init__(self, name, mqtt=None, env=None, loc='LAN'):
        if mqtt is None:
            mqtt = create()
        object.__setattr__(self,'__name__',name)
        object.__setattr__(self,'_loc',loc)
        object.__setattr__(self,'_env',[env or {},Env[1]])
        object.__setattr__(self,'_mqtt',mqtt)
        object.__setattr__(self,'_id',mqtt._client_id.decode() or str(uuid4()))
        object.__setattr__(self,'_',{})
        topic = f'{self.__name__}/{self._id}'
        mqtt.subscribe(topic)
        mqtt.message_callback_add(topic, self._ret)
        topic = f'{self.__name__}/+/'
        mqtt.subscribe(topic)
        mqtt.message_callback_add(topic, self._val)
    def _dump(self, obj):
        return mp.dumps(obj,default=lambda obj:Dump(obj,False,lambda obj,deep:{'':obj._ref} if type(obj) is Ref else None))
    def _load(self, msg):
        if msg is None:
            return
        #print(self, mp.loads(msg))
        return mp.loads(msg,object_hook=lambda obj:Restore(obj,self._env,lambda *args:Ref(self,*args)),strict_map_key=False)
    def _ret(self, client, userdata, msg):
        self._[''] = msg.payload
    def _val(self, client, userdata, msg):
        key = msg.topic[:-1].split('/')[-1]
        cb = self._.get(key,None)
        if callable(cb):
            self._Pool.submit(cb,self,self._load(msg.payload))
        else:
            self._[key] = msg.payload
    def __call__(self, req):
        self._[''] = None
        self._mqtt.publish(f'{self._loc}/{self.__name__}/{self._id}',self._dump(req),qos=2)
        while self._[''] is None:
            time.sleep(0.001)
        ret = self._load(self._[''])
        if isinstance(ret,Exception):
            raise ret
        else:
            return ret
    def __getattr__(self, key):
        return self[key]
    def __getitem__(self, key):
        if key.endswith('/'):
            key = key[:-1]
            msg = self._.get(key,None)
            if msg is None:
                self[key] = None
                msg = self._[key]
            ret = self._load(msg)
            if isinstance(ret,Exception):
                raise ret
            else:
                return ret
        else:
            return self(Expr(key))
    def __setattr__(self, key, val):
        self[key] = val
    def __setitem__(self, key, val):
        if key.endswith('/'):
            key = key[:-1]
            self._[key] = val
            if val is None:
                self._[key] = None
                self._mqtt.publish(f'{self._loc}/{self.__name__}/{key}/',b'',qos=2)
                while self._[key] is None:
                    time.sleep(0.001)
            elif type(val).__name__ not in ('function','builtin_function_or_method'):
                self._mqtt.publish(f'{self._loc}/{self.__name__}/{key}/',self._dump(val),qos=2)
                self[key] = None
        else:
            self(sym.Set(key,val))
    def __dir__(self):
        return self(sym.list(sym.getattr(sym[0],'keys')()))
    def __repr__(self):
        return self.__name__
    
def reload(mod, keep=True, code=None):
    if keep:
        keep = {k:v for k,v in mod.__dict__.items() if not (type(k)==int or k.startswith('__') or type(v).__name__=='module' or callable(v))}
    if code is None:
        import importlib
        importlib.reload(mod)
    else:
        pexec(code, mod.__dict__)
        size = getattr(mod,'__size__',None)
        if size is not None:
            with open(mod.__file__,'r+b') as f:
                code = f.read(size) + code.replace('\r\n','\n').replace('\n','\r\n').encode()
                f.seek(0)
                f.write(code)
                f.truncate(len(code))
    if keep:
        mod.__dict__.update(keep)

_stop = {}
def start(func,*args,**kwargs):
    name = func.__name__ or str(id(func))
    _stop[name] = False
    def target(*args):
        while not _stop[name]:
            func(*args,**kwargs)
    threading.Thread(target=target,name=name,args=args,kwargs=kwargs,daemon=True).start()
    return name

def stop(func):
    name = func if type(func) == str else func.__name__ or str(id(func))
    for thread in threading.enumerate():
        if thread.name == name:
            _stop[name] = True
            thread.join()
            break
