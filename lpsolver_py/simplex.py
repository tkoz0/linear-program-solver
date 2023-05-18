from fractions import Fraction as Frac
from typing import Literal

from .tableau import FracTableau

# fraction constants
ZERO = Frac(0)
ONE = Frac(1)

# literals for tableau form
L_opt = Literal['optimal']
L_unb = Literal['unbounded']
L_inf = Literal['infeasible']

class FracSimplex:
    '''
    state of the simplex algorithm with canonical form tableaus and pivoting
    between basic feasible solutions
    the constructor throws an exception if the problem is infeasible,
    leaving the tableau as the optimal solution to the artificial problem
    '''

    def __init__(self, tab: FracTableau):
        '''
        initializes an initial basic feasible solution
        exception if the original problem is infeasible
        in order to save memory, this does not copy the tableau
        if the tableau is modified using functions outside of this class,
        behavior is undefined
        '''
        self._tab = tab
        self._bfs = [-1]*tab.getNumCons()
        self.findBFS()

    def findBFS(self):
        '''
        convert the tableau into an initial basic feasible solution
        uses the method of artificial variables
        for efficiency, only adds missing columns instead of all
        '''
        raise NotImplementedError()
        raise ValueError('infeasible problem')

    def _pivot(self, r: int, c: int):
        ''' pivot without checking validity '''
        self._tab.pivot(r,c)

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
