from fractions import Fraction as Frac
from typing import Literal
import unittest

from .tableau import Tableau

# fraction constants
ZERO = Frac(0)
ONE = Frac(1)

# literals for tableau form
L_opt = Literal['optimal']
L_unb = Literal['unbounded']
L_inf = Literal['infeasible']

class Simplex:
    '''
    state of the simplex algorithm with canonical form tableaus and pivoting
    between basic feasible solutions
    the constructor throws an exception if the problem is infeasible,
    leaving the tableau as the optimal solution to the artificial problem
    '''

    def __init__(self, tab: Tableau):
        '''
        initializes an initial basic feasible solution
        exception if the original problem is infeasible
        in order to save memory, this does not copy the tableau
        if the tableau is modified using functions outside of this class,
        behavior is undefined
        '''
        self._tab: Tableau = tab
        self._bfs: list[int] = [-1]*tab.getNumCons()
        self._find_bfs()

    def _find_bfs(self):
        '''
        convert the tableau into an initial basic feasible solution
        uses the method of artificial variables
        for efficiency, only adds missing columns instead of all
        '''
        m,n = self._tab.getTableauSize()
        for i in range(m): # get all bi >= 0
            if self._tab.getBi(i) < ZERO:
                self._tab.rowMult(i,-ONE)
        if self._tab.isCanonical(self._bfs):
            return
        # method of artificial variables
        orig_c = self._tab.getC()[:]
        orig_z = self._tab.getZ()
        self._tab.setC([0]*n)
        self._tab.setZ(0)
        # number of artificial variables needed
        missing = [i for i,j in enumerate(self._bfs) if j == -1]
        self._tab.addVars([f'$a{i}' for i in missing])
        for ind,i in enumerate(missing): # handle variable adding
            self._tab.setCj(n+ind,ONE)
            self._tab.setAij(i,n+ind,ONE)
            self._tab.rowSubFromObj(i,ONE)
            self._bfs[i] = n+ind
        # solve artificial problem
        self.solve()
        # solution should now be optimal
        z = self._tab.getZ()
        if z != ZERO:
            raise ValueError(f'infeasible problem, '
                                f'artificial opt = {z}')
        rowkeep = [True]*m # mark linearly dependent rows for deletion
        for i in range(m):
            j = self._bfs[i]
            if j < n: # basic variable is in original problem
                continue
            assert self._tab.getBi(i) == ZERO, \
                f'invalid artificial solution (internal error)'
            # basic artificial variable, pivot on an original variable
            j1 = -1 # column of nonzero entry to pivot on in this row
            for j2 in range(n):
                if self._tab.getAij(i,j2) != ZERO:
                    j1 = j2
                    break
            if j1 == -1: # all 0, constraint is linearly dependent
                rowkeep[i] = False
            else: # pivot
                self._pivot(i,j1)
        # now all basic variables are in the original problem
        # break the abstraction layer to remove rows for deletion
        # FIXME add functionality for this in the tableau class
        self._bfs = [j for i,j in enumerate(self._bfs) if rowkeep[i]]
        assert all(0 <= i < n for i in self._bfs), \
            'invalid basic feasible solution (internal error)'
        self._tab._b = [bi for i,bi in enumerate(self._tab._b) if rowkeep[i]]
        self._tab._a = [row for i,row in enumerate(self._tab._a) if rowkeep[i]]
        self._tab._m = m
        # and remove the artificial variables
        # FIXME add to tableau class to avoid breaking abstraction layer
        self._tab._c = self._tab._c[:n]
        self._tab._cl = self._tab._cl[:n]
        self._tab._cm = self._tab._cm[:n]
        self._tab._a = [row[:n] for row in self._tab._a]
        self._tab._n = n
        # restore original objective and put zeroes back in objective row
        self._tab.setZ(orig_z)
        self._tab.setC(orig_c)
        for i,j in enumerate(self._bfs):
            self._tab.rowSubFromObj(i,self._tab.getCj(j))
        assert self._tab.isCanonical(), 'tableau not canonical (internal error)'
        for j in self._bfs:
            self._tab.setVarMark(j,True)

    def solve(self):
        '''
        pivot to an optimal solution
        uses standard lowest reduced cost pivots
        switches to min index pivots if objective value seems stuck
        '''
        m,n = self._tab.getTableauSize()
        num_piv = 0
        obj_val = self._tab.getZ()
        steps_stuck = 0 # count steps with unchanged objective value
        is_opt = self._tab.isOptimal()
        if is_opt:
            return
        while steps_stuck < m+n: # do standard pivots
            result = self.findPivotStandard(True)
            assert result != 'unbounded', \
                'unbounded artificial problem (internal error)'
            if result == 'optimal':
                is_opt = True
                break
            # successfully pivoted
            num_piv += 1
            z = self._tab.getZ()
            assert z <= obj_val, 'objective value increased (internal error)'
            if z == obj_val:
                steps_stuck += 1
            else:
                steps_stuck = 0
        while not is_opt: # stuck, switch to min index rule
            result = self.findPivotMinIndex(True)
            assert result != 'unbounded', \
                'unbounded artificial problem (internal error)'
            if result == 'optimal':
                is_opt = True
                break
            # successfully pivoted
            num_piv += 1
        # should now be at optimality
        assert self._tab.isOptimal(), f'solver failed (internal error)'

    def getBasicSequence(self) -> list[int]:
        '''
        returns the basic sequence using column indexes
        (the internal representation) do not modify
        '''
        return self._bfs

    def getBasicSequenceNames(self) -> list[str]:
        '''
        returns the basic sequence using variable names
        '''
        ret: list[str] = []
        for j in self._bfs:
            ret.append(self._tab.getVarName(j))
        return ret

    def getBFS(self) -> dict[int,Frac]:
        '''
        returns the values of the basic variables, keyed by column index
        '''
        ret: dict[int,Frac] = {}
        for i,j in enumerate(self._bfs):
            ret[j] = self._tab.getBi(i)
        return ret

    def getObjValue(self) -> Frac:
        '''
        the current objective value (for the minimization problem)
        '''
        return self._tab.getZ()

    def getBFSNames(self) -> dict[str,Frac]:
        '''
        returns the values of the basic variables, keyed by variable name
        assumes all variable names are unique
        '''
        names = self.getBasicSequenceNames()
        ret: dict[str,Frac] = {}
        for i,name in enumerate(names):
            ret[name] = self._tab.getBi(i)
        return ret

    def _pivot(self, r: int, c: int):
        ''' pivot without checking validity (internal use only) '''
        self._tab.pivot(r,c)
        self._tab.setVarMark(self._bfs[r],False)
        self._bfs[r] = c
        self._tab.setVarMark(c,True)

    def pivot(self, r: int, c: int):
        '''
        pivot, checking that the pivot maintains feasibility
        exception if pivoting would violate canonical form
        '''
        # determine minimum ratio
        minratio: None|Frac = None
        for i in range(self._tab.getNumCons()):
            a = self._tab.getAij(i,c)
            if a <= ZERO:
                continue
            ratio = self._tab.getBi(i)/a
            if minratio is None or ratio < minratio:
                minratio = ratio
        ratio = self._tab.getBi(r)/self._tab.getAij(r,c)
        if ratio != minratio:
            raise ValueError(f'bad pivot by min ratio test, r = {r}, c = {c}')
        self._pivot(r,c)

    def findPivotMinIndex(self, do_pivot: bool = False) \
            -> tuple[int,int]|L_opt|L_unb:
        '''
        find a pivot r,c with Bland's min index rule (for avoiding cycling)
        returns 'optimal' or 'unbounded' if no suitable pivot is found
        assumes the tableau is in canonical form
        do_pivot = perform pivot if one is found?
        '''
        m,n = self._tab.getTableauSize()
        j = -1
        for j2 in range(n): # find negative reduced cost
            if self._tab.getCj(j2) >= ZERO:
                continue
            j = j2
            break
        if j == -1: # all reduced costs nonnegative
            return 'optimal'
        i = -1
        ratio: None|Frac = None
        for i2 in range(m): # find first row with minimum ratio
            a = self._tab.getAij(i2,j)
            if a <= ZERO:
                continue
            r = self._tab.getBi(i2)/a
            if ratio is None or r < ratio:
                i = i2
                ratio = r
        if ratio is None: # all column entries negative
            return 'unbounded'
        if do_pivot:
            self._pivot(i,j)
        return i,j

    def findPivotStandard(self, do_pivot: bool = False) \
            -> tuple[int,int]|L_opt|L_unb:
        '''
        find a pivot r,c with the standard minimum reduced cost rule
        returns 'optimal' or 'unbounded' if no suitable pivot is found
        assumes the tableau is in canonical form
        this method may lead to cycling
        do_pivot = perform pivot if one is found?
        '''
        m,n = self._tab.getTableauSize()
        j = -1
        for j2 in range(n): # find smallest negative reduced cost
            cj2 = self._tab.getCj(j2)
            if cj2 >= ZERO:
                continue
            if j == -1 or cj2 < self._tab.getCj(j): # smaller
                j = j2
        if j == -1: # all reduced costs nonnegative
            return 'optimal'
        ratio: None|Frac = None
        i = -1
        for i2 in range(m): # find first row with minimum ratio
            a = self._tab.getAij(i2,j)
            if a <= ZERO:
                continue
            r = self._tab.getBi(i2)/a
            if ratio is None or r < ratio:
                i = i2
                ratio = r
        if ratio is None: # all column entries negative
            return 'unbounded'
        if do_pivot:
            self._pivot(i,j)
        return i,j

    def findPivotMaxIncrease(self, do_pivot: bool = False) \
            -> tuple[int,int]|L_opt|L_unb:
        '''
        find a pivot r,c that will lead to maximum decrease in objective value
        returns 'optimal' or 'unbounded' if no suitable pivot is found
        this method is more expensive since it must read the whole tableau
        do_pivot = perform pivot if one is found?
        '''
        m,n = self._tab.getTableauSize()
        inc: None|Frac = None
        si,sj = -1,-1 # selected pivot
        any_negative_cj = False
        for j in range(n):
            cj = self._tab.getCj(j)
            if cj >= ZERO:
                continue
            any_negative_cj = True
            ratio: None|Frac = None
            isel = -1 # selected row
            colinc: None|Frac = None # amount of objective decrease
            for i in range(m):
                bi = self._tab.getBi(i)
                aij = self._tab.getAij(i,j)
                if aij <= ZERO:
                    continue
                r = bi/aij
                if ratio is None or r < ratio:
                    ratio = r
                    colinc = -cj*r
                    isel = i
                elif r == ratio and (colinc is not None and -cj*r > colinc):
                    colinc = -cj*r
                    isel = i
            if colinc is None: # no valid pivot found
                return 'unbounded'
            if inc is None or colinc > inc:
                inc = colinc
                si,sj = isel,j
        if not any_negative_cj:
            return 'optimal'
        if do_pivot:
            self._pivot(si,sj)
        return si,sj # guaranteed to be valid

    def findPivotAll(self) -> list[tuple[int,int]]:
        '''
        find all possible pivots that maintain canonical form
        assumes the tableau is in canonical form
        does not check for optimal or unbounded form
        pivots may move the objective value farther from optimality
        '''
        ret: list[tuple[int,int]] = []
        m,n = self._tab.getTableauSize()
        for j in range(n):
            # keep track of all pivots with this ratio
            # reset when a better minimum ratio is found
            ratio: None|Frac = None
            pivotlist: list[tuple[int,int]] = []
            for i in range(m):
                aij = self._tab.getAij(i,j)
                if aij <= ZERO:
                    continue
                r = self._tab.getBi(i)/aij
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

    def __str__(self) -> str:
        ret = str(self._tab)
        vars = []
        vals = []
        for i,j in enumerate(self._bfs):
            vars.append(self._tab.getVarName(j))
            vals.append(str(self._tab.getBi(i)))
        cw = [max(len(vars[i]),len(vals[i])) for i in range(len(self._bfs))]
        pad = lambda s,l: ' '*(l-len(s)) + s
        vars = [pad(v,cw[i]) for i,v in enumerate(vars)]
        vals = [pad(v,cw[i]) for i,v in enumerate(vals)]
        ret += f'BFS: ({",".join(vars)})\n'
        ret += f'   = ({",".join(vals)})\n'
        return ret

    def __repr__(self) -> str:
        return f'<{type(self).__name__} object at {hex(id(self))}, ' \
            f'm = {self._tab._m}, n = {self._tab._n}'
