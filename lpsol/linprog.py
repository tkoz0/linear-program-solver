from fractions import Fraction as Frac
import math
import re
from typing import Any,Literal
import unittest

from .tableau import Tableau

# fraction constants
ZERO = Frac(0)
ONE = Frac(1)

# literals for compare operators
L_eq = Literal['==']
L_le = Literal['<=']
L_ge = Literal['>=']
Comp = L_eq|L_le|L_ge

# regex
RE_VARNAME = re.compile(r'[_A-Za-z][_A-Za-z0-9]*')

class LinExpr:
    '''
    linear expression (sum over constant times variable)
    also used to represent objective function
    coefficients ci==0 are removed to simplify
    string representations sort variable names to have a consistent form
    '''

    def __init__(self, *args):
        '''
        constructor arguments must be
        [c1,x1,c2,x2,...],[c]
        representing c1*x1 + c2*x2 + ... + c
        '''
        self.m: dict[str,Frac] = dict()
        self.c: Frac = ZERO
        for i in range(0,len(args),2):
            if i+1 == len(args): # constant at end
                self.c = Frac(args[i])
            else: # parse ci,xi pair
                c = Frac(args[i])
                x = args[i+1]
                if not isinstance(x,str):
                    raise TypeError('var name must be str')
                if not RE_VARNAME.fullmatch(x):
                    raise ValueError(f'invalid var name: {repr(x)}')
                if x not in self.m:
                    self.m[x] = ZERO
                self.m[x] += c
                if self.m[x] == ZERO: # simplify
                    self.m.pop(x)

    def __eq__(self, a) -> bool:
        if isinstance(a,LinExpr):
            return self.m == a.m and self.c == a.c
        else:
            return self.c == Frac(a) and len(self.m) == 0

    def copy(self) -> 'LinExpr':
        ''' return an identical copy '''
        ret = LinExpr()
        ret.m = {x:c for x,c in self.m.items()}
        ret.c = self.c
        return ret

    def __str__(self) -> str:
        if len(self.m) == 0:
            return str(self.c)
        isfirst = True
        ret = ''
        for x in sorted(self.m.keys()):
            c = self.m[x]
            assert c != ZERO
            if isfirst:
                isfirst = False
                if c < ZERO:
                    ret += f'- {abs(c)}*{x}'
                else:
                    ret += f'{c}*{x}'
            else:
                if c < ZERO:
                    ret += f' - {abs(c)}*{x}'
                else:
                    ret += f' + {c}*{x}'
        if self.c < ZERO:
            ret += f' - {abs(self.c)}'
        elif self.c > ZERO:
            ret += f' + {self.c}'
        return ret

    def __repr__(self) -> str:
        ret = f'{type(self).__name__}('
        isfirst = True
        for x in sorted(self.m.keys()):
            c = self.m[x]
            assert c != ZERO
            if isfirst:
                isfirst = False
            else:
                ret += ','
            cs = c.numerator if c.denominator == 1 else str(c)
            ret += f'{repr(cs)},{repr(x)}'
        if self.c != ZERO:
            c = self.c.numerator if self.c.denominator == 1 else str(self.c)
            if isfirst:
                ret += repr(c)
            else:
                ret += f',{repr(c)}'
        ret += ')'
        return ret

    def __iadd__(self, a) -> 'LinExpr': # self += a
        if isinstance(a,LinExpr):
            for x,c in a.m.items():
                if x not in self.m:
                    self.m[x] = ZERO
                self.m[x] += c
                if self.m[x] == ZERO:
                    self.m.pop(x)
            self.c += a.c
        else:
            self.c += Frac(a)
        return self

    def __isub__(self, a) -> 'LinExpr': # self -= a
        if isinstance(a,LinExpr):
            for x,c in a.m.items():
                if x not in self.m:
                    self.m[x] = ZERO
                self.m[x] -= c
                if self.m[x] == ZERO:
                    self.m.pop(x)
            self.c -= a.c
        else:
            self.c -= Frac(a)
        return self

    def __neg__(self) -> 'LinExpr': # -self
        ret = LinExpr()
        for x,c in self.m.items():
            ret.m[x] = -c
        ret.c = -self.c
        return ret

    def __pos__(self) -> 'LinExpr': # +self
        return self

    def __add__(self, a) -> 'LinExpr': # self + a
        ret = self.copy()
        ret += a
        return ret

    def __radd__(self, a) -> 'LinExpr': # a + self
        return self + a

    def __sub__(self, a) -> 'LinExpr': # self - a
        ret = self.copy()
        ret -= a
        return ret

    def __rsub__(self, a) -> 'LinExpr': # a - self
        return - (self - a)

    def _make_con(self, a, comp: Comp) -> 'LinCon':
        if isinstance(a,LinExpr):
            return LinCon(self,comp,a)
        return LinCon(self,comp,LinExpr(a))

    def conEq(self, a) -> 'LinCon':
        ''' create linear constraint self == a '''
        return self._make_con(a,'==')

    def conLe(self, a) -> 'LinCon':
        ''' create linear constraint self <= a '''
        return self._make_con(a,'<=')

    def conGe(self, a) -> 'LinCon':
        ''' create linear constraint self >= a '''
        return self._make_con(a,'>=')

    def subst(self, vars: dict[str,Any]) -> 'LinExpr':
        '''
        substitute variables with other linear expressions given a mapping
        leaves variable unchanged if it is not present in the dictionary
        '''
        _m: dict[str,Frac] = dict()
        _c: Frac = self.c
        for x,c in self.m.items():
            if x in vars:
                xval = vars[x]
                if isinstance(xval,LinExpr):
                    for xx,cc in xval.m.items():
                        if xx not in _m:
                            _m[xx] = ZERO
                        _m[xx] += c*cc
                    _c += c*xval.c
                else:
                    _c += c*Frac(xval)
            else:
                if x not in _m:
                    _m[x] = ZERO
                _m[x] += c
        ret = LinExpr(_c)
        ret.m = {x:c for x,c in _m.items() if c != ZERO}
        return ret

class LinCon:
    ''' 2 linear expressions compared by <= >= or == '''
    def __init__(self, left, comp: Comp, right):
        if isinstance(left,LinExpr):
            self.left: LinExpr = left
        else:
            self.left: LinExpr = LinExpr(left)
        self.comp: Comp = comp
        if isinstance(left,LinExpr):
            self.right: LinExpr = right
        else:
            self.right: LinExpr = LinExpr(right)

    def copy(self) -> 'LinCon':
        ''' return an identical copy '''
        return LinCon(self.left.copy(),self.comp,self.right.copy())

    def __str__(self) -> str:
        return f'{self.left} {self.comp} {self.right}'

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.left)},' \
                f'{repr(self.comp)},{repr(self.right)})'

    def reverse(self) -> 'LinCon':
        ''' flip the inequality '''
        revmap: dict[Comp,Comp] = { '==': '==', '<=': '>=', '>=': '<=' }
        comp = revmap[self.comp]
        return LinCon(self.right,comp,self.left)

    def simplify(self) -> 'LinCon':
        ''' write with variables on left and constant on right '''
        if self.left.c == ZERO and len(self.right.m) == 0:
            return self
        con = self.left - self.right
        c = con.c
        con.c = ZERO
        return LinCon(con,self.comp,LinExpr(-c))

    # self is: left comp right

    def __add__(self, a) -> 'LinCon':
        ret = self.copy()
        ret.right += a
        return ret

    def __sub__(self, a) -> 'LinCon':
        ret = self.copy()
        ret.right -= a
        return ret

    def __radd__(self, a) -> 'LinCon':
        ret = self.copy()
        ret.left += a
        return ret

    def __rsub__(self, a) -> 'LinCon':
        ret = self.copy()
        ret.left = - (ret.left - a)
        return ret

class LinVar:
    '''
    a variable with its bounds
    used to simplify LPs before conversion to standard form
    '''
    def __init__(self, x: str, integral: bool = False,
                 lb: None|Any = None, ub: None|Any = None):
        if not RE_VARNAME.fullmatch(x):
            raise ValueError(f'invalid var name: {repr(x)}')
        self.x: str = x
        self.isint: bool = integral
        self.lb: None|Frac = None if lb is None else Frac(lb)
        self.ub: None|Frac = None if ub is None else Frac(ub)

    def copy(self) -> 'LinVar':
        return LinVar(self.x,self.isint,self.lb,self.ub)

    def __str__(self) -> str:
        lb = '-inf' if self.lb is None else self.lb
        ub = '+inf' if self.ub is None else self.ub
        lbi = isinstance(lb,Frac) and lb.denominator == 1
        ubi = isinstance(ub,Frac) and ub.denominator == 1
        if lb == '-inf' and ub == '+inf':
            msg = 'feasible'
        elif self.isint:
            if lb == '-inf' or ub == '+inf':
                msg = 'feasible'
            elif lb > ub:
                msg = 'infeasible'
            elif lbi or ubi:
                msg = 'feasible'
            else:
                msg = ['','in'][math.floor(lb) == math.floor(ub)] + 'feasible'
        else: # real
            if lb == '-inf' or ub == '+inf':
                msg = 'feasible'
            else:
                msg = ['','in'][lb > ub] + 'feasible'
        return f'{self.x}@{"RZ"[self.isint]}[{lb},{ub}]({msg})'

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.x)},{repr(self.isint)},' \
                f'{repr(self.lb)},{repr(self.ub)})'

    def __eq__(self, a) -> 'LinVar': # self == a
        ret = self.copy()
        a = Frac(a)
        if ret.ub is None or a < ret.ub:
            ret.ub = a
        if ret.lb is None or a > ret.lb:
            ret.lb = a
        return ret

    def __le__(self, a) -> 'LinVar': # self <= a
        ret = self.copy()
        a = Frac(a)
        if ret.ub is None or a < ret.ub:
            ret.ub = a
        return ret

    def __ge__(self, a) -> 'LinVar': # self >= a
        ret = self.copy()
        a = Frac(a)
        if ret.lb is None or a > ret.lb:
            ret.lb = a
        return ret

    def __ne__(self, a):
        raise NotImplementedError('can only use <= >= ==')

    def __lt__(self, a):
        raise NotImplementedError('can only use <= >= ==')

    def __gt__(self, a):
        raise NotImplementedError('can only use <= >= ==')

class LinProg:
    '''
    representation of a linear program in possibly non standard form
    the linear objective function can be maximize or minimized
    constraints are linear equality or inequality
    variables can have arbitrary bounds or be unbounded
    '''

    def __init__(self):
        '''
        '''
