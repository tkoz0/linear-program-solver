import csv
from fractions import Fraction as Frac
import io
import json
from typing import Any,Literal
import unittest

# fraction constants
ZERO = Frac(0)
ONE = Frac(1)

# literals for tableau form
L_opt = Literal['optimal']
L_unb = Literal['unbounded']
L_inf = Literal['infeasible']

class Tableau:
    '''
    full simplex tableau with rational numbers
    for usability as more of a testing/academic tool,
    variables (columns) have names (str) and markings (bool)
    example with m=3,n=5
          x0  x1  x2  x3  x4
    -z |  c0  c1  c2  c3  c4
    ------------------------
    b0 | a00 a01 a02 a03 a04
    b1 | a10 a11 a12 a13 a14
    b2 | a20 a21 a22 a23 a24
    conventions:
    - tableau size m*n is the size of the constraint matrix
    - m constraints
    - n variables
    - i indexes constraints
    - j indexes variables
    '''

    def __init__(self, m: int, n: int):
        '''
        initializes a (m+1)*(n+1) tableau with all zeros
        '''
        if m <= 0:
            raise ValueError(f'need m > 0, provided m = {m}')
        if n <= 0:
            raise ValueError(f'need n > 0, provided n = {n}')
        self._m = m # number of constraints
        self._n = n # number of variables
        self._z = ZERO # (negative) objective value
        self._c = [ZERO]*n # reduced costs
        self._b = [ZERO]*m # constants of equality constraints
        self._a = [[ZERO]*n for _ in range(m)] # constraint matrix
        self._cl = ['']*n # variable names
        self._cm = [False]*n # identify basic variables

    # comparison

    def __eq__(self, t) -> bool:
        ''' compare for equality by testing all corresponding member values '''
        if not isinstance(t,Tableau):
            raise TypeError(f'cannot compare to type {type(t)}')
        return self._m == t._m and self._n == t._n \
            and self._z == t._z \
            and self._c == t._c \
            and self._b == t._b \
            and all(self._a[i] == t._a[i] for i in range(self._m)) \
            and self._cl == t._cl \
            and self._cm == t._cm

    # getters

    def getNumCons(self) -> int:
        ''' number of constraints '''
        return self._m

    def getNumVars(self) -> int:
        ''' number of variables '''
        return self._n

    def getTableauSize(self) -> tuple[int,int]:
        ''' returns row*col size of constraint matrix '''
        return self.getNumCons(),self.getNumVars()

    def getZ(self) -> Frac:
        ''' objective value (-z) '''
        return -self._z

    def getC(self) -> list[Frac]:
        ''' reduced costs '''
        return self._c

    def getCj(self, j: int) -> Frac:
        ''' get a single reduced cost '''
        return self._c[j]

    def getB(self) -> list[Frac]:
        ''' equality constraint constants '''
        return self._b

    def getBi(self, i: int) -> Frac:
        ''' get a single constraint constant '''
        return self._b[i]

    def getA(self) -> list[list[Frac]]:
        ''' constraint matrix '''
        return self._a

    def getAij(self, i: int, j: int) -> Frac:
        ''' get a single constraint coefficient '''
        return self._a[i][j]

    def getVarNames(self) -> list[str]:
        ''' variable names '''
        return self._cl

    def getVarName(self, j: int) -> str:
        ''' get a variable name '''
        return self._cl[j]

    def getVarMarks(self) -> list[bool]:
        ''' variable markings '''
        return self._cm

    def getVarMark(self, j: int) -> bool:
        ''' get a variable marking '''
        return self._cm[j]

    # setters

    def setZ(self, z):
        ''' set objective value, the value stored is -z '''
        self._z = -Frac(z)

    def setC(self, c: list[Any]):
        ''' set reduced costs '''
        for j in range(self.getNumVars()):
            self.setCj(j,Frac(c[j]))

    def setCj(self, j: int, cj):
        ''' set a reduced cost '''
        self._c[j] = Frac(cj)

    def setB(self, b: list[Any]):
        ''' set constraint constants '''
        for i in range(self.getNumCons()):
            self.setBi(i,Frac(b[i]))

    def setBi(self, i: int, bi):
        ''' set a constraint constant '''
        self._b[i] = Frac(bi)

    def setA(self, a: list[list[Any]]):
        ''' set constraint matrix '''
        for i in range(self.getNumCons()):
            for j in range(self.getNumVars()):
                self.setAij(i,j,Frac(a[i][j]))

    def setAij(self, i: int, j: int, aij):
        ''' set a constraint coefficient '''
        self._a[i][j] = Frac(aij)

    def setVarNames(self, cl: list[str]):
        ''' set variable names '''
        for j in range(self.getNumVars()):
            self.setVarName(j,cl[j])

    def setVarName(self, j: int, l: str):
        ''' set a variable name '''
        self._cl[j] = l

    def setVarMarks(self, cm: list[bool]):
        ''' set variable markings '''
        for j in range(self.getNumVars()):
            self.setVarMark(j,cm[j])

    def setVarMark(self, j: int, m: bool):
        ''' set a variable marking '''
        self._cm[j] = m

    def toggleVarMark(self, j: int):
        ''' toggle value of variable marking '''
        self._cm[j] = not self._cm[j]

    # data management

    def addVar(self, v: str = ''):
        ''' add variable with new values initialized as 0 '''
        self._n += 1
        self._c.append(ZERO)
        for row in self._a:
            row.append(ZERO)
        self._cl.append(v)
        self._cm.append(False)

    def addVars(self, vs: list[str]):
        ''' add multiple variables '''
        self._n += len(vs)
        self._c += [ZERO]*len(vs)
        for row in self._a:
            row += [ZERO]*len(vs)
        self._cl += vs
        self._cm += [False]*len(vs)

    def addCon(self):
        ''' add constraint with new values initialized as 0 '''
        self._m += 1
        self._b.append(ZERO)
        self._a.append([ZERO]*self._n)

    def addCons(self, count: int):
        ''' add multiple constraints '''
        if count <= 0:
            raise ValueError(f'need count > 0, provided count = {count}')
        self._m += count
        self._b += [ZERO]*count
        self._a += [[ZERO]*self._n for _ in range(count)]

    def permuteRows(self, perm: list[int]):
        '''
        change the order of the rows
        perm is a permutation of 0..m-1 as a list
        '''
        m = self.getNumCons()
        if len(perm) != m or set(perm) != set(range(m)):
            raise ValueError(f'not a permutation of 0..{m-1}')
        self._a = [self._a[i] for i in perm]
        self._b = [self._b[i] for i in perm]

    def permuteCols(self, perm: list[int]):
        '''
        change the order of the columns
        perm is a permutation of 0..n-1 as a list
        '''
        n = self.getNumVars()
        if len(perm) != n or set(perm) != set(range(n)):
            raise ValueError(f'not a permutation of 0..{n-1}')
        self._a = [[row[j] for j in perm] for row in self._a]
        self._c = [self._c[j] for j in perm]
        self._cl = [self._cl[j] for j in perm]
        self._cm = [self._cm[j] for j in perm]

    def copy(self) -> 'Tableau':
        ''' returns a copy of this tableau '''
        m,n = self.getTableauSize()
        ret = Tableau(m,n)
        ret._z = self._z
        ret._c = self._c[:]
        ret._b = self._b[:]
        ret._a = [row[:] for row in self._a]
        ret._cl = self._cl[:]
        ret._cm = self._cm[:]
        return ret

    # math operations

    def rowMult(self, r: int, m):
        ''' multiply constraint row r by m '''
        m = Frac(m)
        if m == ONE: # nothing will change
            return
        self._b[r] *= m
        self._a[r] = [arj*m for arj in self._a[r]]

    def rowDiv(self, r: int, d):
        ''' divide constraint row by d (d != 0) '''
        d = Frac(d)
        if d == ZERO:
            raise ZeroDivisionError('cannot divide row by zero')
        self.rowMult(r,ONE/d)

    def rowAdd(self, rd: int, rs: int, m: Any = ONE):
        ''' add m times row rs (source) to row rd (destination) '''
        m = Frac(m)
        if m == ZERO: # nothing will change
            return
        self._b[rd] += m*self._b[rs]
        for j in range(self.getNumVars()):
            self._a[rd][j] += m*self._a[rs][j]

    def rowSub(self, rd: int, rs: int, m: Any = ONE):
        ''' subtract m times row rs (source) from row rd (destination) '''
        self.rowAdd(rd,rs,-m)

    def rowAddToObj(self, r: int, m: Any = ONE):
        ''' add m times row r to objective row '''
        m = Frac(m)
        if m == ZERO:
            return
        self._z += m*self._b[r]
        for j in range(self.getNumVars()):
            self._c[j] += m*self._a[r][j]

    def rowSubFromObj(self, r: int, m: Any = ONE):
        ''' subtract m times row r from objective row '''
        self.rowAddToObj(r,-m)

    def pivot(self, r: int, c: int):
        '''
        perform a simplex pivot on r,c
        assumes nothing about the tableau
        '''
        if self._a[r][c] == ZERO:
            raise ZeroDivisionError(f'zero pivot {r},{c}')
        self.rowDiv(r,self._a[r][c]) # normalize row
        self.rowAddToObj(r,-self._c[c]) # make reduced cost 0
        # eliminate remaining nonzeros
        for rr in range(self.getNumCons()):
            if r == rr:
                continue
            self.rowSub(rr,r,self._a[rr][c])

    # tableau input/output

    def loadFile(self, file: str):
        ''' load data from a JSON file '''
        with open(file,'r') as f:
            self.loadJson(json.loads(f.read()))

    def saveFile(self, file: str):
        ''' save data to a JSON file '''
        with open(file,'w') as f:
            f.write(json.dumps(self.saveJson(),separators=(',',':')))

    def loadJson(self, data: dict[str,Any]):
        ''' create a tableau from JSON file data '''
        assert isinstance(data['m'],int) and data['m'] > 0
        assert isinstance(data['n'],int) and data['n'] > 0
        m = data['m']
        n = data['n']
        self._m = m
        self._n = n
        self._z = ZERO
        self._c = [ZERO]*n
        self._b = [ZERO]*m
        self._a = [[ZERO]*n for _ in range(m)]
        self._cl = ['']*n
        self._cm = [False]*n
        self._z = Frac(data['z'])
        for j in range(n):
            self._c[j] = Frac(data['c'][j])
        for i in range(m):
            self._b[i] = Frac(data['b'][i])
        for i in range(m):
            for j in range(n):
                self._a[i][j] = Frac(data['a'][i][j])
        for j in range(n):
            self._cl[j] = str(data['cl'][j])
            self._cm[j] = bool(data['cm'][j])

    def saveJson(self) -> dict[str,Any]:
        ''' create JSON object for saving to file '''
        data: dict[str,Any] = {}
        m,n = self.getTableauSize()
        data['m'] = m
        data['n'] = n
        data['z'] = str(self._z)
        data['c'] = [str(cj) for cj in self._c]
        data['b'] = [str(bi) for bi in self._b]
        data['a'] = [[str(aij) for aij in row] for row in self._a]
        data['cl'] = self._cl
        data['cm'] = self._cm
        return data

    def printGrid(self, labels: bool = True, rownums: bool = True,
                  mpre: str = '(', msuf: str = ')') -> list[list[str]]:
        '''
        create a 2d grid representation of the tableau
        labels = include variable labels?
        rownums = include row indexes as labels?
        mpre = mark prefix for labels of marked variables
        msuf = mark suffix for labels of marked variables
        '''
        data: list[list[str]] = []
        if labels: # labels row
            row = ['',''] if rownums else ['']
            row += [f'{mpre}{l}{msuf}' if self._cm[j] else l
                    for j,l in enumerate(self._cl)]
            data.append(row)
        # objective row
        row = ['',str(self._z)] if rownums else [str(self._z)]
        row += [str(cj) for cj in self._c]
        data.append(row)
        for i in range(self.getNumCons()): # constraint rows
            row = [f'{i}',str(self._b[i])] if rownums else [str(self._b[i])]
            row += [str(aij) for aij in self._a[i]]
            data.append(row)
        return data

    def printText(self, labels: bool = True, rownums: bool = False,
                  spacing: int = 2, left: bool = False,
                  mpre: str = '(', msuf: str = ')') -> str:
        '''
        create a text string for a neat tableau (meant for terminal output)
        labels = include variable labels?
        rownums = include row indexes as labels?
        spacing = number of spaces between columns
        left = left justify values instead of right justify
        mpre = mark prefix for labels of marked variables
        msuf = mark suffix for labels of marked variables
        '''
        if spacing < 1:
            raise ValueError(f'spacing must be positive, provided {spacing}')
        grid = self.printGrid(labels,rownums,mpre,msuf)
        # determine column widths by longest string
        cw = [max(len(grid[r][c]) for r in range(len(grid)))
              for c in range(len(grid[0]))]
        for row in grid: # pad grid values to proper width
            for j in range(len(row)):
                if left:
                    row[j] = f'{row[j]:<{cw[j]}}'
                else:
                    row[j] = f'{row[j]:>{cw[j]}}'
        spaces = ' '*spacing
        sepline = '-'*(spacing*(len(grid[0]) + 2) + sum(cw) + 3)
        lines: list[str] = [sepline]
        sepi = 2 if labels else 1
        sepj = 2 if rownums else 1
        for i,row in enumerate(grid):
            if i == sepi:
                lines.append(sepline)
            lines.append(f'|{spaces}'+
                         spaces.join(row[:sepj]+['|']+row[sepj:])
                         +f'{spaces}|')
        lines.append(sepline)
        return '\n'.join(lines)+'\n'

    def printLatex(self, labels: bool = True, rownums: bool = False,
                   mpre: str = '(', msuf: str = ')') -> str:
        grid = self.printGrid(labels,rownums,mpre,msuf)
        m,n = self.getTableauSize()
        sepi = 2 if labels else 1
        lines: list[str] = []
        lines.append('\\begin{tabular}{'+('|c'*sepi)+'|'+('c'*n)+'|} \\hline')
        # math mode for table entries
        grid = [[f'${s}$' if s else s for s in row] for row in grid]
        for r,row in enumerate(grid):
            line = ' & '.join(row) + ' \\\\'
            if r < sepi or r == len(grid)-1:
                line += '\\hline'
            lines.append(line)
        lines.append('\\end{tabular}')
        return '\n'.join(lines)+'\n'

    def printCSV(self, labels: bool = True, rownums: bool = False,
                 mpre: str = '(', msuf: str = ')') -> str:
        '''
        output as csv data
        labels = include variable labels?
        rownums = incnlude row indexes as labels?
        mpre = mark prefix for labels of marked variables
        msuf = mark suffix for labels of marked variables
        '''
        grid = self.printGrid(labels,rownums,mpre,msuf)
        retio = io.StringIO()
        csvw = csv.writer(retio)
        csvw.writerows(grid)
        return retio.getvalue()

    def __str__(self) -> str:
        return self.printText()

    def __repr__(self) -> str:
        return f'<FracTableau object at {hex(id(self))}, ' \
            f'm = {self._m}, n = {self._n}>'

    # tableau form checking

    def isCanonical(self, bcols: list[int]|None = None) -> bool:
        '''
        check for canonical form
        if cols is not None, stores indexes of basic columns (0..m-1)
        bcols[i] = j means column j is basic with a_ij = 1
        bcols[i] = -1 if no such basic column is in the tableau
        '''
        m,n = self.getTableauSize()
        if any(bi < ZERO for bi in self._b): # need all bi >= 0
            return False
        # row index of 1 to column indexes basic with that 1
        cols: list[list[int]] = [[] for _ in range(m)]
        for j in range(n): # find basic columns
            if self._c[j] != ZERO: # reduced cost must be 0
                continue
            onei = -1
            for i in range(m):
                if self._a[i][j] == ONE:
                    onei = i
                    break
            # found 1, check that all others are 0
            if onei != -1 and all(i == onei or self._a[i][j] == ZERO
                                  for i in range(m)):
                cols[onei].append(j)
        if bcols is not None: # store basic column information
            for i,collist in enumerate(cols):
                if len(collist) == 0:
                    bcols[i] = -1 # not found
                else:
                    bcols[i] = collist[0]
        return all(len(collist) > 0 for collist in cols)

    # the following assume canonical form for performance reasons

    def isOptimal(self) -> bool:
        ''' assuming canonical form, is the tableau in optimal form '''
        return all(cj >= ZERO for cj in self._c)

    def isUnbounded(self) -> bool:
        ''' assuming canonical form, is the tableau in unbounded form '''
        return any(cj < ZERO and all(self._a[i][j] <= ZERO
                                     for i in range(self._m))
                   for j,cj in enumerate(self._c))

    def isInfeasible(self) -> bool:
        ''' assuming canonical form, is the tableau in infeasible form '''
        return any(bi > ZERO and all(self._a[i][j] <= ZERO
                                     for j in range(self._n))
                   for i,bi in enumerate(self._b))

    def isDegenerate(self) -> bool:
        '''
        assuming canonical form
        determines if this basic feasible solution is degenerate
        '''
        return any(bi == ZERO for bi in self._b)

# tableau 1 for testing
# https://math.libretexts.org/Bookshelves/Applied_Mathematics/Applied_Finite_Mathematics_(Sekhon_and_Bloom)/04%3A_Linear_Programming_The_Simplex_Method/4.02%3A_Maximization_By_The_Simplex_Method
# solution x1=4,x2=8,z=-400
tab1a = '''\
    .  .  .  .
    x1  x2 s1 s2
0  -40 -30  0  0
12   1   1  1  0
16   2   1  0  1
'''
tab1b = '''\
    .   .   .   .
    x1  x2  s1  s2
320  0  -10 0    20
4    0  1/2 1  -1/2
8    1  1/2 0   1/2
'''
tab1c = '''\
    .   .   .   .
    x1  x2  s1  s2
400  0   0  20  10
8    0   1   2  -1
4    1   0  -1   1
'''

class TableauTest(unittest.TestCase):
    '''
    tests for simplex tableau
    '''

    def _make_tableau_1(self, tabstr: str) -> Tableau:
        ''' create a tableau from a string representation '''
        grid = [line.split() for line in tabstr.splitlines()]
        m = len(grid)-3
        n = len(grid[0])
        ret = Tableau(m,n)
        ret.setVarMarks([s not in '.-0fF' for s in grid[0]])
        ret.setVarNames(grid[1])
        ret.setZ(-Frac(grid[2][0]))
        ret.setC(grid[2][1:])
        ret.setB([grid[i][0] for i in range(3,3+m)])
        ret.setA([row[1:] for row in grid[3:]])
        return ret

    def setUp(self):
        self.tab1a = self._make_tableau_1(tab1a)
        self.tab1b = self._make_tableau_1(tab1b)
        self.tab1c = self._make_tableau_1(tab1c)

    def tearDown(self):
        pass

    # test getters

    def test_getNumCons(self):
        self.assertEqual(self.tab1a.getNumCons(),2)

    def test_getNumVars(self):
        self.assertEqual(self.tab1a.getNumVars(),4)

    def test_getTableauSize(self):
        self.assertEqual(self.tab1a.getTableauSize(),(2,4))

    def test_getZ(self):
        self.assertEqual(self.tab1a.getZ(),0)
        self.assertEqual(self.tab1b.getZ(),-320)
        self.assertEqual(self.tab1c.getZ(),-400)

    def test_getC(self):
        self.assertEqual(self.tab1a.getC(),[-40,-30,0,0])
        self.assertEqual(self.tab1b.getC(),[0,-10,0,20])
        self.assertEqual(self.tab1c.getC(),[0,0,20,10])

    def test_getCj(self):
        self.assertEqual(self.tab1a.getCj(0),-40)
        self.assertEqual(self.tab1b.getCj(1),-10)
        self.assertEqual(self.tab1c.getCj(2),20)
        # bounds
        self.assertRaises(IndexError,self.tab1a.getCj,4)
        #self.assertRaises(IndexError,self.tab1a.getCj,-1)

    def test_getB(self):
        self.assertEqual(self.tab1a.getB(),[12,16])
        self.assertEqual(self.tab1b.getB(),[4,8])
        self.assertEqual(self.tab1c.getB(),[8,4])

    def test_getBi(self):
        self.assertEqual(self.tab1a.getBi(0),12)
        self.assertEqual(self.tab1a.getBi(1),16)
        # bounds
        self.assertRaises(IndexError,self.tab1a.getBi,2)
        #self.assertRaises(IndexError,self.tab1a.getBi,-1)

    def test_getA(self):
        h = Frac(1,2)
        self.assertEqual(self.tab1a.getA(),[[1,1,1,0],[2,1,0,1]])
        self.assertEqual(self.tab1b.getA(),[[0,h,1,-h],[1,h,0,h]])
        self.assertEqual(self.tab1c.getA(),[[0,1,2,-1],[1,0,-1,1]])

    def test_getAij(self):
        self.assertEqual(self.tab1a.getAij(1,0),2)
        self.assertEqual(self.tab1a.getAij(1,1),1)
        self.assertEqual(self.tab1b.getAij(0,1),Frac(1,2))
        self.assertEqual(self.tab1b.getAij(0,3),-Frac(1,2))
        self.assertEqual(self.tab1c.getAij(1,2),-1)
        # bounds
        self.assertRaises(IndexError,self.tab1a.getAij,0,4)
        self.assertRaises(IndexError,self.tab1a.getAij,2,0)
        self.assertRaises(IndexError,self.tab1a.getAij,2,4)
        #self.assertRaises(IndexError,self.tab1a.getAij,-1,0)
        #self.assertRaises(IndexError,self.tab1a.getAij,0,-1)
        #self.assertRaises(IndexError,self.tab1a.getAij,-1,-1)

    def test_getVarNames(self):
        self.assertEqual(self.tab1a.getVarNames(),['x1','x2','s1','s2'])

    def test_getVarName(self):
        self.assertEqual(self.tab1a.getVarName(0),'x1')
        self.assertEqual(self.tab1a.getVarName(3),'s2')
        # bounds
        self.assertRaises(IndexError,self.tab1a.getVarName,4)
        #self.assertRaises(IndexError,self.tab1a.getVarName,-1)

    def test_getVarMarks(self):
        self.assertEqual(self.tab1a.getVarMarks(),[False]*4)

    def test_getVarMark(self):
        self.assertFalse(self.tab1a.getVarMark(0))
        self.assertFalse(self.tab1a.getVarMark(3))
        # bounds
        self.assertRaises(IndexError,self.tab1a.getVarMark,4)
        #self.assertRaises(IndexError,self.tab1a.getVarMark,-1)

    # test setters

    #def test_setZ(self):
    #    raise NotImplementedError()

    #def test_setC(self):
    #    raise NotImplementedError()

    #def test_setCj(self):
    #    raise NotImplementedError()

    #def test_setB(self):
    #    raise NotImplementedError()

    #def test_setBi(self):
    #    raise NotImplementedError()

    #def test_setA(self):
    #    raise NotImplementedError()

    #def test_setAij(self):
    #    raise NotImplementedError()

    #def test_setVarNames(self):
    #    raise NotImplementedError()

    #def test_setVarName(self):
    #    raise NotImplementedError()

    #def test_setVarMarks(self):
    #    raise NotImplementedError()

    #def test_setVarMark(self):
    #    raise NotImplementedError()

    #def test_toggleVarMark(self):
    #    raise NotImplementedError()

    # test data management stuff

    #def test_addVar(self):
    #    raise NotImplementedError()

    #def test_addVars(self):
    #    raise NotImplementedError()

    #def test_addCon(self):
    #    raise NotImplementedError()

    #def test_addCons(self):
    #    raise NotImplementedError()

    #def test_permuteRows(self):
    #    raise NotImplementedError()

    #def test_permuteCols(self):
    #    raise NotImplementedError()

    #def test_copy(self):
    #    raise NotImplementedError()

    # test math operations

    #def test_rowMult(self):
    #    raise NotImplementedError()

    #def test_rowDiv(self):
    #    raise NotImplementedError()

    #def test_rowAdd(self):
    #    raise NotImplementedError()

    #def test_rowSub(self):
    #    raise NotImplementedError()

    #def test_rowAddToObj(self):
    #    raise NotImplementedError()

    #def test_rowSubFromObj(self):
    #    raise NotImplementedError()

    def test_pivot(self):
        # pivot tableau 1 to optimality
        self.tab1a.pivot(1,0)
        self.assertEqual(self.tab1a,self.tab1b)
        self.tab1b.pivot(0,1)
        self.assertEqual(self.tab1b,self.tab1c)
        self.tab1a.pivot(0,1)
        self.assertEqual(self.tab1a,self.tab1c)

    # test input and output

    #def test_loadFile(self):
    #    raise NotImplementedError()

    #def test_saveFile(self):
    #    raise NotImplementedError()

    #def test_loadJson(self):
    #    raise NotImplementedError()

    #def test_saveJson(self):
    #    raise NotImplementedError()

    #def test_printGrid(self):
    #    raise NotImplementedError()

    #def test_printText(self):
    #    raise NotImplementedError()

    #def test_printLatex(self):
    #    raise NotImplementedError()

    #def test_printCSV(self):
    #    raise NotImplementedError()

    # test form checking

    #def test_isCanonical(self):
    #    raise NotImplementedError()

    #def test_isOptimal(self):
    #    raise NotImplementedError()

    #def test_isInfeasible(self):
    #    raise NotImplementedError()

    #def test_isDegenerate(self):
    #    raise NotImplementedError()

if __name__ == '__main__':
    unittest.main(verbosity=2)
