__all__ = ['table','config','equal','expr','sym','context','flow','meta','multi','domain']
from pprint import pformat

class table(list):
    def __init__(self, *args, **kwargs):
        super().__init__(args)
        self.__dict__.update(kwargs)
    def __getitem__(self, key=None):
        if type(key) is str:
            return self.__dict__[key]
        return super().__getitem__(key)
    def __setitem__(self, key, val):
        if type(key) is str:
            self.__dict__[key] = val
        else:
            super().__setitem__(key, val)
    def __delitem__(self, key):
        if type(key) is str:
            del self.__dict__[key]
        else:
            super().__delitem__(key)
    def __call__(self, *args, **kwargs):
        func = self.__dict__.get('__call__',None)
        if func is not None:
            return func(self,*args,**kwargs)
        if len(args) == 0 and len(kwargs) == 0:
            return self
        super().extend(args)
        self.__dict__.update(kwargs)
        return self
    def __repr__(self):
        r = ''
        for i in self[:]:
            r += pformat(i) + ','
        for k,v in self.__dict__.items():
            r += f'{k}={pformat(v)},'
        if len(r) > 0 and r[-1] == ',':
            r = r[:-1]
        return '[' + r + ']'
    def __neg__(self):
        return self
    def copy(self):
        return self.__class__(*self[:],**self.__dict__)
    @staticmethod
    def to_dict(x):
        if isinstance(x, table):
            return {f'__{x.__class__.__name__}__':table.to_dict(x[:])}|table.to_dict(x.__dict__)
        elif isinstance(x,(tuple,list)):
            return [table.to_dict(v) for v in x]
        elif isinstance(x,dict):
            return {k:table.to_dict(v) for k,v in x.items()}
        else:
            return x
    @classmethod
    def from_dict(cls,dct):
        cls = {table,config,expr,flow._tbl}|{cls}
        for i in cls:
            if f'__{i.__name__}__' in dct:
                lst = dct.pop(f'__{i.__name__}__')
                return i(*lst,**dct)
        return dct

class config(table):
    root = '../json'

    @classmethod
    def load(cls, name=None):
        import json
        dct = {}
        for i in cls.__bases__:
            if i not in (table,config):
                dct |= i.load().__dict__
        with open(f'{config.root}/{cls.__module__}.{name or cls.__name__}.json') as f:
            val = json.load(f)
            if type(val) is dict:
                dct |= val
                return cls.from_dict(dct)
            else:
                val.__dict__ = dct | val.__dict__
                return val
            
    def save(self, *args):
        import json
        if len(args) == 0:
            args = self.__class__.__mro__[::-1][4:-1] + (self,)
        dct = self.__dict__.copy()
        for i in args:
            with open(f"{config.root}/{i.__module__}.{getattr(i,'__name__',i.__class__.__name__)}.json",'w') as f:
                if type(i) is type:
                    json.dump({k:dct.pop(k) for k in i.__annotations__}|{f'__{i.__name__}__':[]},f)
                else:
                    json.dump(dct|{f'__{i.__class__.__name__}__':[]},f)
    
    def __call__(self,*args,**kwargs):
        func = self.__dict__.get('__call__',None)
        if func is not None:
            return func(self,*args,**kwargs)
        import copy
        r = copy.deepcopy(self)
        for k,v in kwargs.items():
            setattr(r,k,v)
        return r

import operator

def equal(x, y):
    if type(x) != type(y):
        return False
    if getattr(x,'__getitem__',None) is not None:
        x = x[:]
        y = y[:]
    if type(x) in (tuple,list,dict):
        if len(x) != len(y):
            return False
        if type(x) is dict:
            for k,v in x.items():
                if not equal(v,y.get(k,None)):
                    return False
        else:
            for i in range(len(x)):
                if not equal(x[i],y[i]):
                    return False
        return True
    return x == y
            
class expr(table):
    def __getitem__(self, key):
        if type(key) is slice and key == slice(None,None,None):
            return super().__getitem__(key)
        dct = self.__dict__
        if 'self' in dct:
            this = dct.pop('self')
            r = self.__class__(*self,key,**dct)
            r.__dict__['self'] = this
            dct['self'] = this
            return r
        else:
            return self.__class__(*self,key,**dct)
    def __getattr__(self, key):
        return None if key.startswith('_') or key in ('compute','getdoc','size','shape') else self[key]
    def __repr__(self):
        if len(self) == 0:
            return 'expr()'
        line = 'sym' if self[:][0] is None else 'expr('+pformat(self[:][0])+')'
        for i in self[:][1:]:
            if type(i) is str:
                line += f'.{i}'
            elif type(i) is table:
                line += '(' + repr(i)[1:-1] + ')'
            else:
                line += f'[{i}]'
        return line[1:] if line.startswith('.') else line
    def __call__(self, *args, **kwargs):
        r = self[:][0]
        body = self[:][1:]
        body.append(table(*args,**kwargs))
        for i in range(len(body)):
            key = body[i]
            if type(key) is table:
                t = table(*key[:],**key.__dict__)
                for k in range(len(key)):
                    v = t[k]
                    if type(v) is self.__class__:
                        dct = self.__dict__|v.__dict__
                        if 'self' in dct:
                            this = dct.pop('self')
                            v = self.__class__(*v[:],**dct)
                            v.__dict__['self'] = this
                            t[k] = v() 
                        else:
                            t[k] = self.__class__(*v[:],**dct)()
                for k,v in key.__dict__.items():
                    if type(v) is self.__class__:
                        dct = self.__dict__|v.__dict__
                        if 'self' in dct:
                            this = dct.pop('self')
                            v = self.__class__(*v[:],**dct)
                            v.__dict__['self'] = this
                            t.__dict__[k] = v()
                        else:
                            t.__dict__[k] = self.__class__(*v[:],**dct)()
                if type(r) is self.__class__:
                    try:
                        v = r[:][0]
                        if v is None:
                            v = self.__dict__
                        for k in r[:][1:-1]:
                            geti = getattr(v,'__getitem__',None)
                            v = getattr(v,k) if geti is None else geti(k)
                        k = r[:][-1]
                        f = getattr(v,k,None) if type(k) is str else None 
                        if callable(f):
                            r = f(*t[:],**t.__dict__)
                        else:
                            if len(t) == 0 and len(t.__dict__) == 0:
                                geti = getattr(v,'__getitem__',None)
                                try:
                                    r = getattr(v,k) if geti is None else geti(k)
                                except:
                                    if r[:][0] is None:
                                        v = None
                                    r = v[k] if type(v) is self.__class__ else self.__class__(v,k)
                            else:
                                seti = getattr(v,'__setitem__',None)
                                if len(t) == 1 and len(t.__dict__) == 0:
                                    t = t[0]
                                setattr(v,k,t) if seti is None else seti(k,t)
                                r = expr(r[:][0])
                    except:
                        if not (i == len(body) - 1 and len(args) == 0 and len(kwargs) == 0):
                            r = r[t] if type(r) is self.__class__ else self.__class__(r,t)
                elif callable(r):
                    try:
                        r = r(*t[:],**t.__dict__)
                    except:
                        if not (i == len(body) - 1 and len(args) == 0 and len(kwargs) == 0):
                            r = self.__class__(r,t)
                else:
                    if not (i == len(body) - 1 and len(args) == 0 and len(kwargs) == 0):
                        r = self.__class__(r,t)
            else:
                r = r[key] if type(r) is self.__class__ else self.__class__(r,key)
        #print(self[:],args,kwargs,self.__dict__,r)
        return r
    def __lt__(a, b):
        return a.__class__(operator.__lt__,table(a,b))
    def __le__(a, b):
        return a.__class__(operator.__le__,table(a,b))
    def __eq__(a, b):
        return a.__class__(operator.__eq__,table(a,b))
    def __ne__(a, b):
        return a.__class__(operator.__ne__,table(a,b))
    def __ge__(a, b):
        return a.__class__(operator.__ge__,table(a,b))
    def __gt__(a, b):
        return a.__class__(operator.__gt__,table(a,b))
    def __not__(a):
        return a.__class__(operator.__not__,table(a))
    def __abs__(a):
        return a.__class__(operator.__abs__,table(a))
    def __round__(a):
        return a.__class__(round,table(a))
    def __add__(a, b):
        return plus(a,b)
    def __radd__(a, b):
        return plus(b,a)
    def __iadd__(a, b):
        return plus(a,b)
    def __and__(a, b):
        return a.__class__(operator.__and__,table(a,b))
    def __rand__(a, b):
        return a.__class__(operator.__and__,table(b,a))
    def __floordiv__(a, b):
        return a.__class__(operator.__floordiv__,table(a,b))
    def __rfloordiv__(a, b):
        return a.__class__(operator.__floordiv__,table(b,a))
    def __inv__(a):
        return a.__class__(operator.__inv__,table(a))
    def __invert__(a):
        return a.__class__(operator.__invert__,table(a))
    def __lshift__(a, b):
        return a.__class__(operator.__lshift__,table(a,b))
    def __rlshift__(a, b):
        return a.__class__(operator.__lshift__,table(b,a))
    def __mod__(a, b):
        return a.__class__(operator.__mod__,table(a,b))
    def __rmod__(a, b):
        return a.__class__(operator.__mod__,table(b,a))
    def __mul__(a, b):
        return a.__class__(operator.__mul__,table(a,b))
    def __rmul__(a, b):
        return a.__class__(operator.__mul__,table(b,a))
    def __matmul__(a, b):
        return a.__class__(operator.__matmul__,table(a,b))
    def __rmatmul__(a, b):
        return a.__class__(operator.__matmul__,table(b,a))
    def __neg__(a):
        return uminus(a)
    def __or__(a, b):
        return a.__class__(operator.__or__,table(a,b))
    def __ror__(a, b):
        return a.__class__(operator.__or__,table(b,a))
    def __pos__(a):
        return uplus(a)
    def __pow__(a, b):
        return a.__class__(operator.__pow__,table(a,b))
    def __rpow__(a, b):
        return a.__class__(operator.__pow__,table(b,a))
    def __rshift__(a, b):
        return a.__class__(operator.__rshift__,table(a,b))
    def __rrshift__(a, b):
        return a.__class__(operator.__rshift__,table(b,a))
    def __sub__(a, b):
        return minus(a,b)
    def __rsub__(a, b):
        return minus(b,a)
    def __truediv__(a, b):
        return a.__class__(operator.__truediv__,table(a,b))
    def __rtruediv__(a, b):
        return a.__class__(operator.__truediv__,table(b,a))
    def __xor__(a, b):
        return a.__class__(operator.__xor__,table(a,b))
    def __rxor__(a, b):
        return a.__class__(operator.__xor__,table(b,a))
    
sym = expr(None)

class plus_minus:
    def __init__(self,name):
        self._name = name
    def __repr__(self):
        return self._name
    def __call__(self,*args):
        if len(args) == 1:
            x = args[0]
            if self._name == 'uplus':
                return x
            if type(x) is expr:
                if len(x) > 0 and x[:][0] is uminus:
                    return x[:][1][0]
                elif len(x) > 0 and x[:][0] is plus:
                    return expr(plus,table(uminus(x[:][1][0]),uminus(x[:][1][1])))
                else:
                    return expr(uminus,table(x))
            return -x
        if type(args[0]) not in (int,float,expr) or type(args[1]) not in (int,float,expr):
            if type(args[0]) is expr or type(args[1]) is expr:
                return expr(plus if self._name == 'plus' else minus,table(*args))
            return args[0]+args[1] if self._name == 'plus' else args[0]-args[1] 
        atom = []
        term = []
        for i in range(2):
            x = args[i]
            sub = i == 1 and self._name == 'minus'
            if type(x) is expr:
                if len(x) > 0 and x[:][0] is plus:
                    t = x[:][1]
                    (term if type(t[0]) is expr else atom).append(t[0])
                    (term if type(t[1]) is expr else atom).append(-t[1] if sub else t[1])
                else:
                    term.append(-x if sub else x)
            else:
                atom.append(-x if sub else x)
        if len(atom) == 0:
            r = 0
        else:
            r = sum(atom)
        for i in term:
            if type(r) is not expr and r == 0:
                r = i
            else:
                r = expr(plus,table(r,i))
        return r

plus = plus_minus('plus')
minus = plus_minus('minus')
uplus = plus_minus('uplus')
uminus = plus_minus('uminus')

class context_switch:
    def __init__(self, ctx, tbl):
        self.ctx = ctx
        self.tbl = tbl
    def __enter__(self):
        self.top = self.ctx <= self.tbl
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx <= self.top

class context:
    def __init__(self,*args,**kwargs):
        tbl = kwargs.pop('table',table)
        object.__setattr__(self,'_tbl',tbl)
        object.__setattr__(self,'_new',lambda:tbl(*args,**kwargs))
        object.__setattr__(self,'_stk',[])
        self.__enter__()
    def __getattr__(self, key):
        return getattr(self._stk[-1],key)
    def __setattr__(self, key, val):
        setattr(self._stk[-1],key,val)
    def __getitem__(self,key):
        return self._stk[-1][key]
    def __setitem__(self,key,val):
        self._stk[-1][key] = val
    def __delitem__(self,key):
        del self._stk[-1][key]
    def __len__(self):
        return len(self._stk[-1])
    def __repr__(self):
        return repr(self._stk[-1])
    def __call__(self, *args, **kwargs):
        return self._stk[-1] if len(args) == 0 and len(kwargs) == 0 else self._stk[-1](*args,**kwargs)
    def __le__(self,val):
        top = self._stk[-1]
        self._stk[-1] = val
        return top
    def __lt__(self, other):
        return context_switch(self, other)
    def __enter__(self):
        top = self._new()
        self._stk.append(top)
        return top
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stk.pop()

class flow(table):
    def __getitem__(self, key):
        if type(key) is slice:
            return super().__getitem__(key)
        key = str(key)
        val = self.__dict__.get(key,None)
        if val is None:
            val = self.__class__()
            self.__dict__[key] = val
        return val
    def __getattr__(self, key):
        return None if key.startswith('_') or key in ('compute','getdoc','size','shape') else self[key]
    def __call__(self, *args, **kwargs):
        if not (len(args) == 0 and len(kwargs) == 0):
            super().append(self.__class__(*args,**kwargs))
        return self
    def clear(self):
        super().clear()
        self.__dict__.clear()

flow = context(table=flow)

class meta:
    def __init__(self, *args):
        self.__meta__ = args
    def __getattr__(self, key):
        return None if key.startswith('_') or key in ('compute','getdoc','size','shape') else self[key]
    def __getitem__(self, key):
        if key is None:
            return self        
        hashable = getattr(key,'__hash__',None)
        val = None if hashable is None else self.__dict__.get(key,None)
        if val is None:
            val = self.__class__()
            val.__dict__['__meta__'] = self.__meta__ + (key,)
            if hashable is not None:
                self.__dict__[key] = val
        return val
    def __call__(self, *args, **kwargs):
        return self.__meta__[0](*args,*self.__meta__[1:],**kwargs)

class multi(meta):
    def __call__(self, *args, **kwargs):
        if len(self.__meta__) == 1:
            val = self.__class__()
            val.__dict__['__meta__'] = self.__meta__ + args
            return val
        elif len(self.__meta__) == 2:
            nodes = getattr(self.__meta__[0],'multi',None)
            if nodes is None:
                return self.__meta__[1](*args,**kwargs)
        else:
            nodes = self.__meta__[2]
            if type(nodes) is range:
                nodes = list(nodes)
            if type(nodes) not in (tuple,list):
                nodes = [nodes]
            if len(nodes) == 0:
                return self.__meta__[1](*args,*self.__meta__[3:],**kwargs)
        env = self.__meta__[0]()
        for node in nodes:
            tbl = getattr(env,str(node),None)
            if tbl is None:
                with self.__meta__[0] as tbl:
                    pass
                env[str(node)] = tbl
            self.__meta__[0] <= tbl
            self.__meta__[1](*args,*self.__meta__[3:],**kwargs)
        self.__meta__[0] <= env
                        
import ast, inspect, copy

class FindReg(ast.NodeVisitor):
    def __init__(self, regq):
        self.regq = regq
        self.found = False
    def visit_Name(self, node):
        if self.regq(node.id):
            self.found = True
            
def RegQ(node, regq):
    visitor = FindReg(regq)
    visitor.visit(node)
    return visitor.found
    
class WithPass(ast.NodeTransformer):
    def __init__(self, regq, env={}):
        self.regq = regq
        self.env = env
    def visit_If(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        If = self.env['If']
        if type(If) is not str:
            If = 'If'
        Else = self.env['Else']
        if type(Else) is not str:
            Else = 'Else'
        Elif = self.env['Elif']
        if type(Elif) is not str:
            Elif = 'Elif'
        if isinstance(node.test, ast.Call) and node.test.func.id == '_':
            node.test.func.id = If
        elif RegQ(node.test, self.regq):
            node.test = ast.Call(func=ast.Name(id=If, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.test], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        if isinstance(node.test, ast.Call) and node.test.func.id == If:
            withs = [ast.With(items=[ast.withitem(context_expr = node.test)], body=node.body, lineno=node.lineno, col_offset = node.col_offset)]
            for i in range(len(node.orelse)):
                orelse = node.orelse[i]
                if isinstance(orelse, ast.With) \
                    and isinstance(orelse.items[0].context_expr, ast.Call):
                    if orelse.items[0].context_expr.func.id == If:
                        orelse.items[0].context_expr.func.id = Elif
                    withs.append(orelse)
                else:
                    orelse = ast.With(items=[\
                    ast.withitem(context_expr = \
                    ast.Call(func=ast.Name(id=Else, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset),\
                    args=[], keywords=[], lineno=node.lineno, col_offset = node.col_offset),\
                    lineno=node.lineno, col_offset = node.col_offset)], \
                    body=node.orelse[i:], lineno=node.lineno, col_offset = node.col_offset)
                    withs.append(orelse)
                    break
            return withs
        return node
    def visit_While(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        While = self.env['While']
        if type(While) is not str:
            While = 'While'
        if isinstance(node.test, ast.Name) and node.test.id == '_':
            node.test = ast.Call(func=ast.Name(id=While, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        elif isinstance(node.test, ast.Call) and node.test.func.id == '_':
            node.test.func.id = While
        elif RegQ(node.test, self.regq):
            node.test = ast.Call(func=ast.Name(id=While, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.test], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        if isinstance(node.test, ast.Call) and node.test.func.id == While:
            return ast.With(items=[ast.withitem(context_expr = node.test)], body=node.body, lineno=node.lineno, col_offset = node.col_offset)
        return node
    def visit_For(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        For = self.env['For']
        if type(For) is not str:
            For = 'For'
        if isinstance(node.iter, ast.Call) and node.iter.func.id == '_':
            node.iter.func.id = For
        elif RegQ(node.target, self.regq):
            node.iter = ast.Call(func=ast.Name(id=For, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.iter], keywords=[], lineno=node.lineno, col_offset = node.col_offset)
        if isinstance(node.iter, ast.Call) and node.iter.func.id == For:
            node.target.ctx = ast.Load()
            if len(node.iter.args) == 1 and isinstance(node.iter.args[0], ast.Call) and node.iter.args[0].func.id == 'range':
                node.iter.args[0] = ast.Tuple(node.iter.args[0].args, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset)
            node.iter.args = [node.target] + node.iter.args
            return ast.With(items=[ast.withitem(context_expr = node.iter)], body=node.body, lineno=node.lineno, col_offset = node.col_offset)
        return node
    def visit_Assign(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        Set = self.env['Set']
        if type(Set) is not str:
            Set = 'Set'
        if isinstance(node.targets[0], ast.Name) and isinstance(node.targets[0], ast.Name) and self.regq(node.targets[0].id):
            node.targets[0].ctx = ast.Load()
            return ast.Expr(value=ast.Call(func=ast.Name(id=Set, ctx=ast.Load(), lineno=node.lineno, col_offset = node.col_offset), args=[node.targets[0], node.value], keywords=[], lineno=node.lineno, col_offset = node.col_offset), lineno=node.lineno, col_offset = node.col_offset)
        return node
    def visit_Call(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        Call = self.env['Call']
        if type(Call) is not str:
            Call = 'Call'
        func = getattr(node.func, 'id', None)
        if func is not None and self.env.get('#'+func, None) is not None:
            return ast.Call(func=ast.Name(id=Call,ctx=ast.Load(),lineno=node.lineno,col_offset=node.col_offset),args=[ast.Constant(value=node.func.id,lineno=node.lineno,col_offset=node.col_offset)]+node.args,keywords=[],lineno=node.lineno,col_offset=node.col_offset)
        return node
    def visit_Return(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        Return = self.env['Return']
        if type(Return) is not str:
            Return = 'Return'
        return ast.Expr(value=ast.Call(func=ast.Name(id=Return,ctx=ast.Load(),lineno=node.lineno,col_offset=node.col_offset),args=\
            node.value.elts if type(node.value) is ast.Tuple else ([] if node.value is None else [node.value]),keywords=[],lineno=node.lineno,col_offset=node.col_offset), lineno=node.lineno, col_offset = node.col_offset)
                           
class SubPass(ast.NodeTransformer):
    def __init__(self, env={}):
        self.env = env
        self.regs = {}
    def visit_FunctionDef(self, node):
        #print(ast.dump(node))
        self.regs = {'_':[]}
        reg = -1
        kws = len(node.args.defaults)
        for arg in node.args.args[:(-kws or None)]:
            if arg.annotation is None:
                reg += 1
            else:
                reg = arg.annotation.value
                self.regs['_'].append(reg)
                arg.annotation = None
            self.regs[arg.arg] = ast.Subscript(value=ast.Name(id='R',ctx=ast.Load(),lineno=node.lineno,col_offset=node.col_offset), \
            slice=ast.Index(value=ast.Constant(value=reg,lineno=node.lineno,col_offset=node.col_offset)), \
            lineno=node.lineno,col_offset=node.col_offset)
        self.regs['_'].append(reg)
        node.regs = self.regs['_']
        self.generic_visit(node)
        self.env['#'+node.name] = self.regs['_']
        self.regs = {}
        Func = self.env['Func']
        if type(Func) is not str:
            Func = 'Func'
        node.args.args = node.args.args[-kws:] if kws else []
        node.body = [ast.With(items=[ast.withitem(context_expr=ast.Call(func=ast.Name(id=Func,ctx=ast.Load(),lineno=node.lineno, col_offset = node.col_offset), \
            args=[ast.Constant(value=node.name,lineno=node.lineno,col_offset=node.col_offset)]+ \
                [ast.Constant(value=i,lineno=node.lineno,col_offset=node.col_offset) for i in node.regs], \
                keywords=[],lineno=node.lineno,col_offset=node.col_offset))],body=node.body, lineno=node.lineno,col_offset=node.col_offset)]
        return node
    def visit_Name(self, node):
        #print(ast.dump(node))
        if node.id != '_':
            value = self.regs.get(node.id, None)
            if value is not None:
                value = copy.copy(value)
                value.ctx = node.ctx
                return value
        return node
    def visit_Assign(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)
        if isinstance(node.targets[0], ast.Name):
            value = self.regs.get(node.targets[0].id, None)
            if value is not None:
                value = copy.copy(value)
                value.ctx = ast.Store()
                node.targets[0] = value
        return node

def domain(ctx={}, regq=None, sub=None, dump=False):
    def decorator(func):
        src = inspect.getsourcelines(func)[0]
        indent = len(src[0]) - len(src[0].lstrip())
        src = ''.join([line[indent:] for line in src])
        node = ast.parse(src)
        node.body[0].decorator_list = []
        if sub is True:
            node = SubPass(ctx).visit(node)
        elif isinstance(sub, ast.NodeTransformer):
            node = sub(ctx).visit(node)
        elif callable(sub):
            node = sub(node)
        if callable(regq):
            node = WithPass(regq,ctx).visit(node)
            if dump:
                unparse = getattr(ast, 'unparse', None)
                if unparse is not None:
                    print(unparse(node))
        env = func.__globals__.copy()
        env.update(ctx)
        exec(compile(node, filename='', mode='exec'), env)
        def wrap(*args, **kwargs):
            env.update(ctx)
            return eval(func.__name__, env)(*args, **kwargs)
        return wrap
    return decorator