from fractions import Fraction as Frac
from typing import Any,Literal

# fraction constants
ZERO = Frac(0)
ONE = Frac(1)

# literals for tableau form
L_opt = Literal['optimal']
L_unb = Literal['unbounded']
L_inf = Literal['infeasible']

class Tableau:
    '''
    simplex tableau
    example with m=3,n=5
    -z |  c0  c1  c2  c3  c4
    ------------------------
    b0 | a00 a01 a02 a03 a04
    b1 | a10 a11 a12 a13 a14
    b2 | a20 a21 a22 a23 a24
    for usability as more of a testing/academic tool,
    variables (columns) have names (str) and markings (bool)
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
        ''' (negative) objective value '''
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

    # data management

    def addVar(self, v: str = ''):
        ''' add variable with new values initialized as 0 '''
        self._n += 1
        self._c.append(ZERO)
        for row in self._a:
            row.append(ZERO)
        self._cl.append(v)
        self._cm.append(False)

    def addCon(self):
        ''' add constraint with new values initialized as 0 '''
        self._m += 1
        self._b.append(ZERO)
        self._a.append([ZERO]*self._n)

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

    # math operations

    def rowMult(self, r: int, m):
        ''' multiply constraint row r by m '''
        m = Frac(m)
        self._b[r] *= m
        self._a[r] = [arj*m for arj in self._a[r]]

    def rowDiv(self, r: int, d):
        ''' divide constraint row by d (d != 0) '''
        d = Frac(d)
        self.rowMult(r,ONE/d)

    def rowAdd(self, rd: int, rs: int, m: Any = ONE):
        ''' add m times row rs (source) to row rd (destination) '''
        self._b[rd] += m*self._b[rs]
        for j in range(self.getNumVars()):
            self._a[rd][j] += m*self._a[rs][j]

    def rowSub(self, rd: int, rs: int, m: Any = ONE):
        ''' subtract m times row rs (source) from row rd (destination) '''
        self.rowAdd(rd,rs,-m)

    def rowAddToObj(self, r: int, m: Any = ONE):
        ''' add m times row r to objective row '''
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
        self.rowDiv(r,self._a[r][c]) # normalize row
        self.rowAddToObj(r,-self._c[c]) # make reduced cost 0
        # eliminate remaining nonzeros
        for rr in range(self.getNumCons()):
            if r == rr:
                continue
            self.rowSub(rr,r,self._a[rr][c])

    def findPivotMinIndex(self) -> tuple[int,int]|L_opt|L_unb:
        '''
        find a pivot r,c with Bland's min index rule (for avoiding cycling)
        returns 'optimal' or 'unbounded' if no suitable pivot is found
        assumes the tableau is in canonical form
        '''
        m,n = self.getTableauSize()
        j = -1
        for j2 in range(n): # find negative reduced cost
            if self.getCj(j2) >= ZERO:
                continue
            j = j2
            break
        if j == -1: # all reduced costs nonnegative
            return 'optimal'
        i = -1
        ratio: None|Frac = None
        for i2 in range(m): # find first row with minimum ratio
            a = self.getAij(i2,j)
            if a <= ZERO:
                continue
            r = self.getBi(i2)/a
            if ratio is None or r < ratio:
                i = i2
                ratio = r
        if ratio is None: # all column entries negative
            return 'unbounded'
        return i,j

    def findPivotStandard(self) -> tuple[int,int]|L_opt|L_unb:
        '''
        find a pivot r,c with the standard minimum reduced cost rule
        returns 'optimal' or 'unbounded' if not suitable pivot is found
        assumes the tableau is in canonical form
        '''
        m,n = self.getTableauSize()
        j = -1
        for j2 in range(n): # find smallest negative reduced cost
            cj2 = self.getCj(j2)
            if cj2 >= ZERO:
                continue
            if j == -1 or cj2 < self.getCj(j): # smaller
                j = j2
        if j == -1: # all reduced costs nonnegative
            return 'optimal'
        ratio: None|Frac = None
        i = -1
        for i2 in range(m): # find first row with minimum ratio
            a = self.getAij(i2,j)
            if a <= ZERO:
                continue
            r = self.getBi(i2)/a
            if ratio is None or r < ratio:
                i = i2
                ratio = r
        if ratio is None: # all column entries negative
            return 'unbounded'
        return i,j

    def findPivotAll(self) -> list[tuple[int,int]]:
        '''
        find all possible pivots that maintain canonical form
        assumes the tableau is in canonical form
        does not check for optimal or unbounded form
        '''
        ret: list[tuple[int,int]] = []
        m,n = self.getTableauSize()
        for j in range(n):
            cj = self.getCj(j)
            if cj >= ZERO:
                continue
            # keep track of all pivots with this ratio
            # reset when a better minimum ratio is found
            ratio: None|Frac = None
            pivotlist: list[tuple[int,int]] = []
            for i in range(m):
                aij = self.getAij(i,j)
                if aij <= ZERO:
                    continue
                r = self.getBi(i)/aij
                if ratio is None:
                    ratio = r
                    pivotlist.append((i,j))
                elif r == ratio:
                    pivotlist.append((i,j))
                elif r < ratio:
                    ratio = r
                    pivotlist = []
                    pivotlist.append((i,j))
                # if greater, do nothing
            ret += pivotlist
        return ret

    def findBFS(self):
        '''
        convert the tableau into an initial basic feasible solution
        uses the method of artificial variables
        '''
        raise NotImplementedError()

    # tableau input/output

    def loadFile(self, file: str):
        raise NotImplementedError()

    def saveFile(self, file: str):
        raise NotImplementedError()

    def loadFromJson(self, jdata):
        raise NotImplementedError()

    def toJson(self):
        raise NotImplementedError()

    def printText(self, labels: bool = True, spacing: int = 2) -> str:
        raise NotImplementedError()

    def printLatex(self, labels: bool = True, lab_mm: bool = True) -> str:
        raise NotImplementedError()

    def printCSV(self, labels: bool = True) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.printText()

    # tableau form checking

    def isCanonical(self) -> bool:
        raise NotImplementedError()

    def isOptimal(self) -> bool:
        raise NotImplementedError()

    def isUnbounded(self) -> bool:
        raise NotImplementedError()

    def isInfeasible(self) -> bool:
        raise NotImplementedError()

    def isDegenerate(self) -> bool:
        raise NotImplementedError()
