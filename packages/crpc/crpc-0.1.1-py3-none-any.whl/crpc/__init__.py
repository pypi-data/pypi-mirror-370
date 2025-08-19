from paho.mqtt import client as mqtt_client
import os, sys, time, traceback, importlib, threading
from concurrent.futures import ThreadPoolExecutor
import msgpack as mp
try:
    import msgpack_numpy
    msgpack_numpy.patch()
except:
    pass
from uuid import uuid4

broker = 'localhost'
port = 1883
username = 'emqx_test'
password = 'emqx_test'
WS = f'"ws://{broker}:8083/mqtt",'+'{'+f'username:"{username}",password:"{password}"'+'}'
WEB = "http://localhost"

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

def peval(expr, env={}):
    if type(env) == dict:
        builtins = env.get('__builtins__',__builtins__)
        if type(builtins) != dict:
            builtins = builtins.__dict__
    if type(expr) == dict:
        head = expr.get('',None)
        if head == '':
            return env
        elif type(head) in (int,str):
            head = head.split('.') if type(head) == str else (head,)
            ret = env.get(head[0],builtins.get(head[0],None)) if type(env) == dict else env(head[0])
            for h in head[1:]:
                if ret is None:
                    break
                ret = ret.get(h,None) if type(ret) == dict else getattr(ret,h,None)
            return ret
        expr = {k:peval(v,env) for k,v in expr.items() if k != ''}
        if type(head) in (tuple,list) and len(head) > 0:
            func = peval(head[0] if type(head[0]) == dict else {'':head[0]},env)
            if func is env:
                key = head[1]
                ret = peval({'':key},env)
                if len(head) == 2:
                    return pcall(ret) if callable(ret) else ret
                else:
                    val = peval(head[2],env)
                    if callable(ret):
                        pcall(ret,val)
                    elif type(env) == dict:
                        if val == None:
                            if env.get(key,None) is not None:
                                del env[key]
                        else:
                            env[key] = val
                    else:
                        env(key,val)
                    return
            elif callable(func):
                return pcall(func,*peval(head[1:],env),**expr)    
            elif len(head) == 1 and len(expr) == 0:
                return func
    elif type(expr) in (tuple, list):
        return [peval(i,env) for i in expr]
    return expr
        
class Promise:
    def __init__(self, setup, *args):
        self.setup = setup
        self.args = args
    def __call__(self, *args):
        return pcall(self.setup, *args)
                       
def rpc(env={}):
    def rpc_default(obj):
        t = type(obj)
        if isinstance(obj,Exception):
            key = 'Exception'
            s = ''.join(traceback.format_exception_only(t,obj))[:-1]
        else:
            key = id(obj)
            if type(env) == dict:
                env[key] = obj
            else:
                env(key,obj)
            s = repr(obj)
        t = t.__module__+'.'+t.__name__
        return {'':key,t:s}
    def handler(client, userdata, msg):
        topic = '/'.join(msg.topic.split('/')[1:])
        if topic[-1] == '/':
            key = topic[:-1].split('/')[-1]
            ret = peval({'':key},env)
            if len(msg.payload) == 0:
                if callable(ret):
                    ret = pcall(ret)
                ret = mp.dumps(ret,default=rpc_default)
            else:
                val = peval(mp.loads(msg.payload),env)
                if callable(ret):
                    pcall(ret,val)
                elif type(env) == dict:
                    if val == None:
                        if env.get(key,None) is not None:
                            del env[key]
                    else:
                        env[key] =  val
                else:
                    env(key,val)
                ret = mp.dumps(val,default=rpc_default)
        else:
            ret = peval(mp.loads(msg.payload),env)
            if type(ret) == Promise:
                if len(ret.args) == 0:
                    return ret(topic)
                else:
                    def wrap(ret):
                        try:
                            ret = mp.dumps(ret,default=rpc_default)
                        except Exception as e:
                            ret = mp.dumps(e,default=rpc_default)
                        client.publish(topic,ret,qos=2)
                    return ret(wrap,*ret.args)
            try:
                ret = mp.dumps(ret,default=rpc_default)
            except Exception as e:
                ret = mp.dumps(e,default=rpc_default)
        client.publish(topic,ret,qos=2)
    return handler

def server(name, env={}, client=None, prefix=''):
    if client is None or type(client) in (int,str):
        client = create(name=client,start=False)
    topic = f'{prefix}/{name}/#'
    client.subscribe(topic)
    client.message_callback_add(topic, rpc(env))
    return client

class Remote:
    def __init__(self, caller, key, obj={}):
        object.__setattr__(self,'_caller',caller)
        object.__setattr__(self,'_key',key)
        object.__setattr__(self,'_obj',obj)
    def __call__(self, *args, **kwargs):
        return self._caller(self._key,*args,**kwargs)
    def __getattr__(self, key):
        if key == '__signature__':
            return
        return self.__class__(self._caller,('getattr',{'':self._key},key))
    def __setattr__(self, key, val):
        self._caller('setattr',{'':self._key},key,val)
    def __getitem__(self, key):
        return self.__class__(self._caller, (('getattr',{'':self._key},'__getitem__'),key))
    def __setitem__(self, key, val):
        self._caller(('getattr',{'':self._key},'__setitem__'),key,val)
    def __repr__(self):
        return f'{self.__class__.__name__}({self._caller._topic}, {self._obj or self._key})'
    def __del__(self):
        if type(self._key) == int:
            self._caller('',self._key,None)
    def __dir__(self):
        return self._caller(('getattr',{'':self._key},'__dir__'))

def caller_default(obj):
    if type(obj) == slice:
        return {'':('slice',obj.start,obj.stop,obj.step)}
    elif type(obj) == Remote:
        return {'':obj._key}

class RemoteException(Exception):
    def __init__(self, obj):
        self.obj = obj
    def __str__(self):
        for k,v in self.obj.items():
            return v #return f'{k}: {v}'

executor = ThreadPoolExecutor()
                   
class caller:
    def __init__(self, topic, client=None, prefix=''):
        if client is None or type(client) in (int,str):
            client = create(name=client)
        object.__setattr__(self,'_topic',topic)
        object.__setattr__(self,'_client',client)
        object.__setattr__(self,'_id',client._client_id.decode() or str(uuid4()))
        object.__setattr__(self,'_prefix',prefix)
        object.__setattr__(self,'_',{})
        topic = f'{self._topic}/{self._id}'
        client.subscribe(topic)
        client.message_callback_add(topic, self.on_ret)
        topic = f'{self._topic}/+/'
        client.subscribe(topic)
        client.message_callback_add(topic, self.on_val)
        def object_hook(obj):
            key = obj.get('',None)
            if key is None:
                return obj
            del obj['']
            if key == 'Exception':
                raise RemoteException(obj)
            else:
                return Remote(self,key,obj)
        object.__setattr__(self,'_object_hook',object_hook)
    def _loads(self,msg):
        try:
            ret = mp.loads(msg,object_hook=self._object_hook)
        except RemoteException as e:
            ret = e
        if isinstance(ret,RemoteException):
            raise RemoteException(ret.obj)
        else:
            return ret
    def on_ret(self, client, userdata, msg):
        self._[''] = msg.payload
    def on_val(self, client, userdata, msg):
        key = msg.topic[:-1].split('/')[-1]
        ret = pcall(self._loads, msg.payload)
        cb = self._.get(key,None)
        if callable(cb):
            executor.submit(cb, self, ret)
        else:
            self._[key] = ret
    def __call__(self, *args, **kwargs):
        self._[''] = None
        kwargs[''] = args
        self._client.publish(f'{self._prefix}/{self._topic}/{self._id}',mp.dumps(kwargs,default=caller_default),qos=2)
        while self._[''] is None:
            time.sleep(0.001)
        return self._loads(self._[''])
    def __getattr__(self, key):
        return Remote(self, key)
    def __getitem__(self, key):
        val = self._.get(key,None)
        if val is None:
            self._client.publish(f'{self._prefix}/{self._topic}/{key}/',b'',qos=2)
            for i in range(1000):
                time.sleep(0.001)
                val = self._.get(key,None)
                if val is not None:
                    break
        return val
    def __setattr__(self, key, val):
        self('',key,val)
    def __setitem__(self, key, val):
        self._[key] = val    
        if val is not None and not callable(val):
            self._client.publish(f'{self._prefix}/{self._topic}/{key}/',mp.dumps(val,default=caller_default),qos=2)
    def __dir__(self):
        return [i for i in self.list({'':(('getattr',{'':''},'keys'),)}) if type(i) is str and not i.startswith('_') and not i.startswith('$')]
                
def repl(topic, client=None):
    handler = caller(topic, client)
    for line in sys.stdin:
        print(handler('pexec', line))
    
def reload(mod, keep=True, code=None):
    if keep:
        keep = {k:v for k,v in mod.__dict__.items() if not (type(k)==int or k.startswith('__') or type(v).__name__=='module' or callable(v))}
    if code is None:
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

if __name__ == '__main__':        
    if len(sys.argv) > 2:
        if sys.argv[1] == 'server':
            server(sys.argv[2], globals()).loop_forever()
        elif sys.argv[1] == 'repl':
            repl(sys.argv[2])