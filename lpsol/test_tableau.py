from fractions import Fraction as Frac
import unittest

from . import Tableau

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
