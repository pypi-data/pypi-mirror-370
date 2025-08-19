import msgpack as mp
try:
    import numpy as np
    import msgpack_numpy
    msgpack_numpy.patch()
except:
    import np
    np.bool_ = bool
    np.number = int,float
from . import *

def function(code):
    if code.startswith('def '):
        name = code.split('\n')[0].split('(')[0][4:]
        exec(code,Env[0])
        return Env[0][name]
    else:
        code = code.split('lambda')
        return eval('lambda '+'lambda'.join(code[1:]).strip())
            
def Dump(obj,deep=True,ext=None):
    if obj is None:
        return None
    elif type(obj) in (int,float,str,bytes):
        return obj
    elif isinstance(obj,np.ndarray) or isinstance(obj,np.bool_) or isinstance(obj,np.number) or isinstance(obj,complex):
        return obj
    elif type(obj) in (tuple,list):
        return [Dump(i,deep,ext) for i in obj]
    elif type(obj) is dict:
        return {k:Dump(v,deep,ext) for k,v in obj.items()}
    if isinstance(obj,Exception):
        import traceback
        msg = ''.join(traceback.format_exception_only(type(obj),obj))[:-1]
        print(msg)
        return {'':[type(obj).__name__,msg]}
    elif type(obj) is slice:
        return {'':['slice',obj.start,obj.stop,obj.step]}
    elif type(obj) is Expr:
        return {'':['Expr']+([Dump(i,deep,ext) for i in obj[:]] if deep else obj[:])}
    elif type(obj) is Arg:
        r = Dump(obj[{}],deep,ext) if deep else obj[{}]
        r[''] = ['Arg']+(Dump(obj[()],deep,ext) if deep else obj[()])
        return r
    elif type(obj) is Seq:
        return {'':['Seq',Dump(obj['.'],deep,ext),*Dump(obj[:],deep,ext)]}
    elif type(obj) is Obj and (obj._name.endswith('()') or obj._name == ''):
        proto = Dump(obj['.'],deep,ext)
        if obj['.'] is not None and proto is None:
            return None
        return {'':['Obj',proto],**Dump(obj[:],deep,ext)}
    elif ext is None and type(obj) is Obj:
        return {'':obj._name}
    elif ext is None and type(obj).__name__ == 'function':
        import inspect
        try:
            src = inspect.getsource(obj)
        except:
            src = None
        return src and {'':['function',src]}
    else:
        r = None if ext is None else ext(obj,deep)
        return repr(obj) if r is None else r 

def Restore(obj,env=None,ext=None):
    if type(obj) is not dict:
        return obj
    r = obj.get('',None)
    if r is None:
        return {k:Restore(v,env,ext) for k,v in obj.items()}
    del obj['']
    if type(r) is int:
        return None if ext is None else ext(r,obj)
    elif type(r) is str:
        return Eval(Expr(*r.split('.')),env)
    elif type(r) is list:
        if isinstance(r[0],str):
            func = Eval(Expr(r[0]),env)
        else:    
            func = Restore(r[0],env,ext)
        args = [Restore(i,env,ext) for i in r[1:]]
        kwargs = {k:Restore(v,env,ext) for k,v in obj.items()}
        try:
            ret = func(*args,**kwargs)
        except Exception as e:
            ret = e
        return ret

updated = set()

def DB():
    import os,sqlite3
    root = globals().get('__file__',None)
    root = os.path.dirname(os.path.abspath('.') if root is None else os.path.dirname(os.path.abspath(root)))
    db = sqlite3.connect(os.path.join(root,'config.db'))
    cs = db.cursor()
    return db,cs

_cache = {}
def Load(key=None,conn=None):
    db,cs = DB() if conn is None else conn
    if key is None:
        cs.execute('CREATE TABLE IF NOT EXISTS key(kid INTEGER PRIMARY KEY,key TEXT UNIQUE);')
        cs.execute("CREATE TABLE IF NOT EXISTS val(ts INTEGER DEFAULT (1000*(unixepoch(strftime('%Y-%m-%d %H:%M'))+strftime('%f'))),kid INT,val BLOB);")
        db.commit()
        cs.fetchall()
        cs.execute('SELECT kid,key FROM key ORDER BY kid;')
        keys = []
        vals = {}
        srcs = []
        for kid,key in cs.fetchall() or []:
            _cache[key] = kid
            if not key.startswith('<'):
                keys.append(key)
        for key in keys:
            val,src = Load(key,(db,cs))
            vals[k[0]] = val
            srcs.append(src)
        cs.close()
        db.close()
        return vals,'\n'.join(srcs)
    kid = _cache.get(key,None)
    if kid is None:
        cs.execute('SELECT kid FROM key WHERE key=?;',(key,))
        ret = cs.fetchone()
        if ret is None:
            cs.close()
            db.close()
            return
        kid = ret[0]
        _cache[key] = kid
    cs.execute('SELECT ts,val FROM val WHERE kid=? ORDER BY ts DESC LIMIT 1;',(kid,))
    ret = cs.fetchone()
    if ret is None:
        cs.close()
        db.close()
        return
    ts,blob = ret
    _cache[kid] = ts,blob
    #log = json.dumps(mp.loads(blob,strict_map_key=False),separators=(",",":"))
    print(f'Load {key} @ {str(datetime.fromtimestamp(ts/1000))[:-3]}')
    updated.add(key)
    key = key.split('.')
    function = globals()['function']
    globals()['function'] = sym.function
    val = mp.loads(blob,object_hook=Restore,strict_map_key=False)
    src = []
    if len(key) == 1:
        src.append(f"Obj('{key[0]}')")
    elif type(val) is Expr and val[:][0] == 'function':
        code = val[:][1][0]()
        if code.startswith('def '):
            src.append(code)
            src.append(code.split('\n')[0].split('(')[0][4:])
        else:
            src.append('lambda '+'lambda'.join(code.split('lambda')[1:]).strip())
    else:
        src.append(repr(val))
    src[-1] = '.'.join(key)+' = '+src[-1]
    globals()['function'] = function
    val = mp.loads(blob,object_hook=Restore,strict_map_key=False)
    Set(Expr(*key),val)
    if conn is None:
        cs.close()
        db.close()
    return val,'\n'.join(src)
    
def Save(key, val):
    blob = mp.dumps(val,default=lambda obj:Dump(obj,False))
    if blob == b'\xc0':
        return
    db,cs = DB()
    kid = _cache.get(key,None)
    if kid is None:
        cs.execute('INSERT OR IGNORE INTO key (key) VALUES (?);',(key,))
        db.commit()
        cs.execute('SELECT kid from key where key=?;',(key,))
        ret = cs.fetchone()
        if ret is None:
            cs.close()
            db.close()
            return
        kid = ret[0]
        _cache[key] = kid
    last = _cache.get(kid,None)
    ts = datetime.now()
    if last is not None and last[1] == blob:
        ts = int(1000*datetime.timestamp(ts))
        cs.execute('UPDATE val SET ts = ? WHERE ts = ? and kid = ?;',(ts,_cache[kid][0],kid))
        db.commit()
        _cache[kid] = ts,blob
    else:
        print(f'[{str(ts)[:-3]}] {key} = {val}')
        ts = int(1000*datetime.timestamp(ts))
        cs.execute('INSERT INTO val (ts,kid,val) VALUES (?,?,?);',(ts,kid,blob))
        db.commit()
        _cache[kid] = ts,blob
    cs.close()
    db.close()