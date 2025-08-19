from datetime import datetime
    
class Arg:
    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_mut', True)
        for i in range(len(args)):
            kwargs[i] = args[i]
        object.__setattr__(self, '_dict', kwargs)
    def __call__(self, *args, **kwargs):
        r = self.__class__()
        for k,v in self._dict.items():
            r._dict[k] = v
        for i in range(len(args)):
            r._dict[i] = args[i]
        for k,v in kwargs.items():
            r._dict[k] = v
        return r
    def __getitem__(self, key):
        if isinstance(key, str) and (key.startswith('_') or key in ('compute','getdoc','size','shape')):
            return None
        if type(key) is slice and key == slice(None,None,None):
            return self._dict
        elif type(key) in (tuple,list) and len(key) == 0:
            num = max([i for i in self._dict.keys() if type(i) is int] or [-1]) + 1
            return [self._dict.get(i,None) for i in range(num)]
        elif type(key) is dict and len(key) == 0:
            return {k:v for k,v in self._dict.items() if isinstance(k,str) and k.isidentifier()}
        return Prop(self,key) if self._mut else self._dict.get(key,None)
    def __getattr__(self, key):
        return self[key]
    def __setitem__(self, key, val):
        if self._mut:
            self[key](val)
        else:
            self._dict[key] = val
    def __setattr__(self, key, val):
        if isinstance(key, str) and key.startswith('_'):
            self.__dict__[key] = val
        else:
            self[key] = val
    def __len__(self):
        return len(self._dict)
    def __pos__(self):
        self._mut = True
        return self
    def __neg__(self):
        self._mut = False
        return self
    def __invert__(self):
        self._mut = not self._mut
        return self
    def __repr__(self):
        #return repr(self._dict)
        from pprint import pformat
        r = ''
        arg = self._dict
        num = max([i for i in arg.keys() if type(i) is int] or [-1]) + 1
        for i in range(num):
            r += pformat(arg.get(i,None)) + ','
        for k,v in arg.items():
            if isinstance(k, str) and k.isidentifier():
                r += f'{k}={pformat(v)},'
        if len(r) > 0 and r[-1] == ',':
            r = r[:-1]
        return '(' + r + ')'
    
class Prop:
    def __init__(self, obj, key):
        self._obj = obj
        self._key = key
    def __call__(self, *args, **kwargs):
        arg = None
        if not (len(kwargs) == 0 and len(args) == 0):
            if len(kwargs) == 0 and len(args) == 1:
                arg = args[0]
            else:
                arg = Arg(*args,**kwargs)
            if arg is None:
                del self._obj._dict[self._key]
                return self._obj
            elif type(arg) is not Expr:
                self._obj._dict[self._key] = arg
                return self._obj
        obj = self._obj
        val = None
        while obj is not None:
            val = obj._dict.get(self._key, None)
            if val is not None:
                break
            obj = obj.__dict__.get('_proto', None)
        if arg is None:
            #return Eval(val,this=self._obj)#if type(val) is Expr else val
            #return val if val is None or type(val) in (int,float,str,Arg) else Eval(val,this=self._obj)
            return Eval(val,this=self._obj) if type(val) in (Expr,Obj,tuple,list,dict) else val
        else:
            self._obj._dict[self._key] = Eval(arg,old=val,this=self._obj)
            return self._obj
    def __repr__(self):
        return repr(self._obj) + (f'.{self._key}' if isinstance(self._key,str) else f'[{self._key}]')
    def __getitem__(self, key):
        if isinstance(key, str) and (key.startswith('_') or key in ('compute','getdoc','size','shape')):
            return None
        key = str(self._key) + '.' + str(key)
        val = self._obj.__dict__.get(key, None)
        if val is not None:
            return val
        val = self.__class__(self._obj,key)
        self._obj.__dict__[key] = val
        return val
    def __getattr__(self, key):
        return self[key]
        
class Obj:
    def __init__(self, proto=None, *args, **kwargs):
        if proto is None or type(proto) is str:
            object.__setattr__(self, '_proto', None)
            object.__setattr__(self, '_name', proto if proto else '')
        else:
            object.__setattr__(self, '_proto', proto)
            object.__setattr__(self, '_name', (proto._name if type(proto) is Obj else repr(proto))+'()')
        for k in range(len(args)):
            kwargs[str(k)] = args[k]
        object.__setattr__(self, '_dict', kwargs)
        if self._proto is None and proto:
            changed(self)
    def __call__(self, *args, **kwargs):
        if type(self._proto).__name__ == 'function':
            return self._proto(*args,**kwargs)
        elif type(self._proto) is Expr:
            return Eval(self._proto,arg=-Arg(*args,**kwargs))
        else:
            return self.__class__(self, *args, **kwargs)
    def __getitem__(self, key):
        if isinstance(key, str) and (key.startswith('_') or key in ('compute','getdoc','size','shape')):
            return None
        if key == '.':
            return self._proto
        elif key == '..':
            proto = self._proto
            if proto is None:
                return self
            elif proto._name.endswith('()'):
                return proto['..']
            else:
                return proto
        elif key == '...':
            proto = self
            while proto._proto is not None:
                proto = proto._proto
            return proto
        elif type(key) is slice and key == slice(None,None,None):
            return self._dict
        key = str(key)
        val = self.__dict__.get(key, None)
        if val is not None:
            return val
        val = Prop(self,key)
        self.__dict__[key] = val
        return val
    def __getattr__(self, key):
        return self[key]
    def __setitem__(self, key, val):
        key = str(key)
        if type(val).__name__ == 'function' or type(val) is Expr:
            val = Obj(val)
        last = self.__dict__.get(key, None)
        if type(val) is Obj and type(last) is Obj:
            val.__dict__.update({k:v for k,v in last.__dict__.items() if type(v) is not Prop and not k.startswith('_')})
        self.__dict__[key] = val
        if not key.startswith('_') and self._name and not self._name.endswith('()'):
            name = self._name+'.'+key
            changed(name,val)
            if type(val) is Obj:
                val._name = name
                self.__dict__[key] = val
    def __setattr__(self, key, val):
        if isinstance(key, str) and key.startswith('_'):
            self.__dict__[key] = val
        else:
            self[key] = val
    def __repr__(self):
        #return self._name
        from pprint import pformat
        if self._name and (self._proto is None or not self._name.endswith('()')):
            return self._name
        if self._proto is None or type(self._proto) is not str:
            r = 'Obj' if self._proto is None else repr(self._proto)
            num = max([int(i) for i in self._dict.keys() if i[0].isdigit()] or [-1]) + 1
            r += '(' + ','.join([pformat(self._dict.get(str(i),None)) for i in range(num)]) + ')'
        else:
            r = f"Obj('{self._proto}')"
        for k,v in self._dict.items():
            if not k[0].isdigit():
                for i in k.split('.'):
                    if i.isidentifier():
                        r += '.' + i
                    else:
                        r += '[' + i + ']'
                if type(v) is Arg:
                    r += repr(v)
                else:
                    r += '(' + pformat(v) + ')'
        return r

class Seq:
    def __init__(self, obj, *args):
        self._obj = obj
        self._this = obj
        self._list = list(args)
    def __getitem__(self, key):
        if self._this is self._obj and not isinstance(key,str):
            return self._list[key]
        else:
            if isinstance(key, str) and key.startswith('_') or key in ('compute','getdoc','size','shape'):
                return None
            if key == '.':
                return self._obj
            if type(self._this) is Prop:
                self._this = self._this[key]
            else:
                self._this = self._this.__dict__.get(str(key),self._this[key])
            return self
    def __getattr__(self, key):
        return self[key]
    def __setitem__(self, key, val):
        self._list[key] = val
    def __iadd__(self, other):
        self._list += list(other[:])
        return self
    def __add__(self, other):
        return self.__class__(self._obj,*(self._list+list(other[:])))
    def __call__(self, *args, **kwargs):
        if len(args) == 0 and len(kwargs) == 0:
            if self._this is self._obj:
                return self
            elif type(self._this) is Seq:
                self._list.append(self._this)
                self._this = self._obj
            else:
                self._this = self._this()
        elif self._this is self._obj:
            self._list += list(args)
        elif type(self._this) is Prop:
            self._this = self._this(*args,**kwargs)
        else:
            self._list.append(self._this(*args, **kwargs))
            self._this = self._obj
        return self
    def __len__(self):
        return len(self._list)
    def __repr__(self):
        obj = repr(self._obj)
        r = f'Seq({obj})'
        t = []
        for i in self._list:
            s = repr(i)
            if s.startswith(obj) and len(s.split(').')) == 1:
                if len(t) > 0:
                    r += '('+','.join(t)+')'
                    t.clear()
                r += s[len(obj):]
            else:
                t.append(s)
        if len(t) > 0:
            r += '('+','.join(t)+')'
        return r

class Expr:
    def __init__(self, *args):
        object.__setattr__(self,'_code',[i for i in args if not (isinstance(i,str) and i.startswith('_'))])
    def __getitem__(self, key):
        if type(key) is slice and key == slice(None,None,None):
            return self._code
        elif isinstance(key, str) and (key.startswith('_') or key in ('compute','getdoc','size','shape')):
            return None
        return self.__class__(*(self._code + [key]))
    def __getattr__(self, key):
        return self[key]
    def __setitem__(self, key, val):
        Set(self[key],val)
        return val
    def __setattr__(self, key, val):
        Set(self[key],val)
        return val
    def __call__(self, *args, **kwargs):
        if len(kwargs) == 0 and len(args) == 1 and type(args[0]) is Arg:
            arg = args[0]
        else:
            arg = Arg(*args,**kwargs)
        return self.__class__(*(self._code + [arg]))
    def __len__(self):
        return len(self._code)
    def __repr__(self):
        if len(self._code) == 0:
            return 'sym'
        head = globals().get(self._code[0], self._code[0])
        line = '' if type(head) is Expr or isinstance(head,Oper) else 'sym'
        for i in self._code:
            if isinstance(i, str):
                line += f'.{i}'
            elif type(i) is Arg or isinstance(i,Oper):
                line += repr(i)
            else:
                line += f'[{i}]'
        return line[1:] if line.startswith('.') else line
    def __lt__(self, other):
        return Lt(self,other)
    def __le__(self, other):
        return Le(self,other)
    def __eq__(self, other):
        return Eq(self,other)
    def __ne__(self, other):
        return Ne(self,other)
    def __ge__(self, other):
        return Ge(self,other)
    def __gt__(self, other):
        return Gt(self,other)
    def __not__(self):
        return Not(self) 
    def __abs__(self):
        return Abs(self)
    def __round__(self):
        return Round(self)        
    def __add__(self, other):
        return Add(self,other)
    def __radd__(self, other):
        return Add(other,self)
    def __and__(self, other):
        return And(self,other)
    def __rand__(self, other):
        return And(other,self)
    def __floordiv__(self, other):
        return IDiv(self,other)
    def __rfloordiv__(self, other):
        return IDiv(other,self)
    def __inv__(self):
        return Inv(self)
    def __invert__(self):
        return Invert(self)
    def __lshift__(self, other):
        return LShift(self,other)
    def __rlshift__(self, other):
        return LShift(other,self)
    def __mod__(self, other):
        return Mod(self,other)
    def __rmod__(self, other):
        return Mod(other,self)
    def __mul__(self, other):
        return Mul(self,other)
    def __rmul__(self, other):
        return Mul(other,self)
    def __matmul__(self, other):
        return MatMul(self,other)
    def __rmatmul__(self, other):
        return MatMul(other,self)
    def __neg__(self):
        return USub(self)
    def __or__(self, other):
        return Or(self,other)
    def __ror__(self, other):
        return Or(other,self)
    def __pos__(self):
        return UAdd(self)
    def __pow__(self, other):
        return Pow(self,other)
    def __rpow__(self, other):
        return Pow(other,self)
    def __rshift__(self, other):
        return RShift(self,other)
    def __rrshift__(self, other):
        return RShift(other,self)
    def __sub__(self, other):
        return Sub(self,other)
    def __rsub__(self, other):
        return Sub(other,self)
    def __truediv__(self, other):
        return Div(self,other)
    def __rtruediv__(self, other):
        return Div(other,self)
    def __xor__(self, other):
        return Xor(self,other)
    def __rxor__(self, other):
        return Xor(other,self)
    
sym = Expr()
this = sym.this # obj
old = sym.old # act,val
arg = sym.arg # _

class Oper:
    def __init__(self,oper,name=None):
        import operator
        self._oper = operator.__dict__[oper] if type(oper) is str else oper
        self._name = name or repr(oper)
    def __call__(self,*args):
        for x in args:
            if type(x) is Expr:    
                return Expr(self,Arg(*args))
        else:
            return self._oper(*args)
    def __repr__(self):
        return self._name

Lt = Oper('lt','Lt')
Le = Oper('le','Le')
Eq = Oper('eq','Eq')
Ne = Oper('ne','Ne')
Ge = Oper('ge','Ge')
Gt = Oper('gt','Gt')
Not = Oper('not_','Not')
Abs = Oper('abs','Abs')
Round = Oper(round,'Round')
And = Oper('and_','And')
IDiv = Oper('floordiv','IDiv')
Inv = Oper('inv','Inv')
Invert = Oper('invert','Invert')
LShift = Oper('lshift','LShift')
Mod = Oper('mod','Mod')
Mul = Oper('mul','Mul')
MatMul = Oper('matmul','MatMul')
Or = Oper('or_','Or')
Pow = Oper('pow','Pow')
RShift = Oper('rshift','RShift')
Div = Oper('truediv','Div') 
Xor = Oper('xor','Xor')

DivMod = Oper(divmod,'DivMod')
Sum = Oper(sum,'Sum')
    
class PlusMinus(Oper):
    def __init__(self,name):
        self._name = name
    def __call__(self,*args):
        if len(args) == 1:
            x = args[0]
            if self._name == 'UAdd':
                return x
            if type(x) is Expr:
                if x[:][0] is USub:
                    return x[:][1][0]()
                elif x[:][0] is Add:
                    return Expr(Add,Arg(USub(x[:][1][0]()),USub(x[:][1][1]())))
                else:
                    return Expr(USub,Arg(x))
            else:
                return -x            
        atom = []
        expr = []
        for i in range(2):
            x = args[i]
            sub = i == 1 and self._name == 'Sub'
            if type(x) is Expr:
                if x[:][0] is Add:
                    t = x[:][1][()]
                    (expr if type(t[0]) is Expr else atom).append(t[0])
                    (expr if type(t[1]) is Expr else atom).append(-t[1] if sub else t[1])
                else:
                    expr.append(-x if sub else x)
            else:
                atom.append(-x if sub else x)
        if len(atom) == 0:
            r = 0
        elif type(atom[0]) is str:
            r = ''.join(atom)
        else:
            r = sum(atom)
        for i in expr:
            if type(r) is not Expr and r == 0:
                r = i
            else:
                r = Expr(Add,Arg(r,i))
        return r
        
Add = PlusMinus('Add')
Sub = PlusMinus('Sub')
UAdd = PlusMinus('UAdd')
USub = PlusMinus('USub')

def Equal(x, y):
    if type(x) != type(y):
        return False
    if type(x) in (Arg,Obj,Expr,Seq):
        x = x[:]
        y = y[:]
    if type(x) in (tuple,list,dict):
        if len(x) != len(y):
            return False
        if type(x) is dict:
            for k,v in x.items():
                if not Equal(v,y.get(k,None)):
                    return False
        else:
            for i in range(len(x)):
                if not Equal(x[i],y[i]):
                    return False
        return True
    return x == y

Env = [{},{}]

_builtins = __builtins__ if type(__builtins__) is dict else __builtins__.__dict__
#Env[1] = {k:v for k,v in _builtins.items() if type(v) is type and not k.startswith('_')}
for k in ['abs','bool','bytearray','bytes','complex','dict','divmod','float',
          'getattr','int','len','list','map','max','min','pow','range',
          'round','set','setattr','str','sum','tuple','type','zip']:
    Env[1][k] = _builtins[k]

def Eval(expr, env=None, **kwargs):
    #if Env[0].get('DEBUG',None):
    #    print(type(expr),expr)
    if type(expr) in (tuple,list):
        return type(expr)([Eval(i,env,**kwargs) for i in expr])
    elif type(expr) is dict:
        return {k:Eval(v,env,**kwargs) for k,v in expr.items()}
    elif type(expr) is Arg:
        return Arg(*Eval(expr[()],env,**kwargs),**Eval(expr[{}],env,**kwargs))
    elif type(expr) is Obj and expr._name.endswith('()'):
        obj = Obj(Eval(expr._proto,env,**kwargs))
        for k,v in expr[:].items():
            obj[:][k] = Eval(v,env,**kwargs) 
        return obj
    elif type(expr) is not Expr:
        return expr
    
    env = env or Env
    if not isinstance(env,(tuple,list)):
        env = (env,)
    r = env
    for i in expr[:]:
        #print(expr,i,kwargs)
        if type(i) is Arg:
            t = Arg()
            for k,v in i[:].items():
                t[:][k] = Eval(v,env,**kwargs)
            if r is Set and t[:].get('env',None) is None:
                t[:]['env'] = env
            # print(type(r), r, repr(r))
            try:
                r = r(*t[()],**t[{}])
            except:
                r = Expr(r,t)
            kwargs['old'] = None
        else:
            key = Eval(i,env,**kwargs)
            if r is env:
                if type(key) is int:
                    r = Env[key]
                elif type(key) is str:
                    r = kwargs.get(key,globals().get(key,None))
                    if r is None:
                        for e in env:
                            r = e.get(key,None)
                            if r is not None:
                                break
                        else:
                            r = Expr(key)
                else:
                    r = key
            else:
                r = r[key] if type(r) in (tuple,list,dict,Arg,Expr,Obj,Prop,Seq) else getattr(r,str(key))
    return None if r is env or r is Env else r

def Set(*args,env=None):
    if len(args) == 3:
        obj,key,val = args
    else:
        obj = None
        key,val = args
        if type(key) is Expr:
            if len(key) == 1:
                key = key[:][0]
            else:
                obj = Eval(Expr(*key[:][:-1]))
                key = key[:][-1]
    if obj is None:
        env = env or Env
        if not isinstance(env,(tuple,list)):
            env = (env,)
        found = False
        for e in env:
            r = e.get(key,None)
            if r is not None:
                if type(r).__name__ == 'function':
                    r(val)
                else:
                    if val is None:
                        del e[key]
                    else:
                        e[key] = val
                found = True
                break
        if not found:
            env[0][key] = val
    else:
        func = getattr(obj,'__setitem__',None)
        if func is None:
            if type(obj) not in (int,float,str,tuple,list,dict):
                setattr(obj,str(key),val)
        else:
            func(key,val)
    return val

class Asm:
    def __init__(self, state=0, code=None):
        self._state = state
        self._code = [] if code is None else code
    def __getitem__(self, key):
        if type(key) is slice and key == slice(None,None,None):
            return self._code
        elif isinstance(key, str) and (key.startswith('_') or key in ('compute','getdoc','size','shape')):
            return None
        if self._state == 0:
            self._code.append([])
            return self.__class__(1, self._code[-1])[key]
        elif self._state == 1:
            self._code.append(key)
            return self
    def __getattr__(self, key):
        return self[key]
    def __setitem__(self, key, val):
        if isinstance(key, str) and (key.startswith('_') or key in ('compute','getdoc','size','shape')):
            return None
        if self._state == 0:
            self._code.append(['Set',Arg(key,val)])
        else:
            arg = Arg(Expr(*self._code),key,val)
            self._code.clear()
            self._code += ['Set',arg]
    def __setattr__(self, key, val):
        if isinstance(key, str) and key.startswith('_'):
            self.__dict__[key] = val
        else:
            self[key] = val
    def __call__(self, *args, **kwargs):
        if self._state == 0:
            self._code = list(args)
        else:
            self._code.append(Arg(*args,**kwargs))
        return self
    def __len__(self):
        return len(self._code)
    def __repr__(self):
        return '\n'.join([repr(Expr(*i)) for i in (self._code if self._state == 0 else [self._code])])
            
#asm = Asm()

_opers = {'Mult':'Mul','GtE':'Ge','LtE':'le','NotEq':'Ne'}
def Parse(code):
    if code is None:
        return code
    elif isinstance(code, str):
        import ast
        code = ast.parse(code)
        #print(ast.dump(code))
    name = code.__class__.__name__
    if name == 'Module':
        return [Parse(i) for i in code.body]
    elif name == 'Expr':
        return Parse(code.value)
    elif name == 'Call':
        func = Parse(code.func)
        args = [Parse(i) for i in code.args]
        kwargs = {i.arg:Parse(i.value) for i in code.keywords}
        return func(*args,**kwargs)
    elif name == 'Attribute':
        return Parse(code.value)[code.attr]
    elif name == 'Subscript':
        return Parse(code.value)[Parse(code.slice)]
    #elif name == 'Slice':
    #    lower = Parse(getattr(code,'lower',None))
    #    upper = Parse(getattr(code,'upper',None))
    #    step = Parse(getattr(code,'step',None))
    #    return slice(lower,upper,step)
    elif name == 'Name':
        return Expr(code.id)
    elif name == 'Constant':
        return code.value
    elif name == 'UnaryOp':
        op = code.op.__class__.__name__
        return globals()[_opers.get(op,op)](Parse(code.operand))
    elif name == 'BinOp':
        op = code.op.__class__.__name__
        return globals()[_opers.get(op,op)](Parse(code.left),Parse(code.right))
    elif name == 'Compare':
        op = code.ops[0].__class__.__name__
        return globals()[_opers.get(op,op)](Parse(code.left),Parse(code.comparators[0]))
    elif name == 'Tuple':
        return tuple([Parse(i) for i in code.elts])
    elif name == 'List':
        return [Parse(i) for i in code.elts]
    elif name == 'Dict':
        return dict(zip([Parse(i) for i in code.keys],[Parse(i) for i in code.values]))
    else:
        import ast
        raise NotImplementedError(ast.dump(code)) # ast.unparse
            
changers = {}
def changed(*args):
    name = None
    if len(args) == 1:
        val = args[0]
        key = repr(val)
        if type(val) is Obj:
            name = val._name
            val._name = 'Obj()'
            if len(key.split('.')) == 1:
                val._proto = name
    else:
        key,val = args
    #Save(key, val)
    if name is not None:
        val._name = name
        if len(key.split('.')) == 1:
            val._proto = None
    func = changers.get(key, None)
    if func is not None:
        func()

class Ref:
    def __init__(self,node,ref,obj={}):
        object.__setattr__(self,'_node',node)
        object.__setattr__(self,'_ref',ref)
        val = f'<object at {hex(self._ref)}>' if type(self._ref) is int else repr(self._ref)
        for k,v in obj.items():
            val = v
            break
        object.__setattr__(self,'_val',val)
    def __getattr__(self, key):
        if isinstance(key, str) and (key.startswith('_') or key in ('compute','getdoc','size','shape')):
            return None
        return self._node(sym.getattr(self,key))
    def __setattr__(self, key, val):
        return self._node(sym.setattr(self,key,val))
    def __getitem__(self, key):
        return self._node(sym.getattr(self,'__getitem__')(key))
    def __setitem__(self, key, val):
        return self._node(sym.getattr(self,'__setitem__')(key,val))
    def __call__(self, *args, **kwargs):
        kwargs[''] = [self] + list(args)
        return self._node(kwargs)
    def __dir__(self):
        return self._node(sym.getattr(self,'__dir__')())
    def __repr__(self):
        return f'{self._node}.{self._val}'
    
if __name__ == '__main__':
    Env[0] = globals()
    # Load()
    # Freq = Obj('Freq')
    # Freq.bsb = Obj()
    
    # asm.DDS.Cooling = sym.DDS(pos=1).f[0](200).a[0](1)
    # asm.Cooling = sym.DDS.Cooling
    # asm.Cooling.on = sym.Cooling().f[1](10).a[1]({'a':1,2:3})
    # asm.Cooling.on.sub = sym.Cooling.on().f[2](-10)

    # asm.Wave.Cooling = sym.Wave().w[0]([sym.Cooling.on])
    # asm.Wave.Zero = sym.Wave().w[0]([])
    # asm.Wave.Detection = sym.Wave().w[0]([sym.Cooling.on]).w[1]([])

    # asm.pre = sym.Seq(sym.Wave).Cooling(1000).Zero(10)
    # asm.Wave.Pre = sym.Wave(seq=sym.pre)

    # asm.seq = sym.Seq(sym.Wave).Pre(3,4,theta=3.14,foo=5).Detection(500,1).Zero(10)
    # asm.Scan(sym.seq, 1, [0.01, 5, 0.1])
    # asm.Scan(sym.seq, sym.Cooling.on.f[1], (-10, 10, 1))
    
    # print(asm)
    
    # DDS = Obj('DDS')
    # Wave = Obj('Wave')
    
    # def Scan(*args, **kwargs):
    #     print('Scan', *args)
    
    # Env[0] = globals()
    # Eval(Parse(str(asm)))
    #exec(str(asm))

    #qh = Seq(Hamiltonian).p(1).C(1).p(1).n(2).C(1)
    #qc = Seq(Gate).Rx(0.5).cx(1,2)
    #code = Seq(Asm).mov(0,1).if(3,10,20)