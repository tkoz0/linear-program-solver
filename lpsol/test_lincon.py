from fractions import Fraction as Frac
import unittest

from . import LinExpr, LinCon

class LinConTest(unittest.TestCase):
    '''
    tests for linear constraints
    '''

    def setUp(self):
        # linear expressions
        self.a1 = LinExpr()
        self.a2 = LinExpr(Frac(5,2))
        self.a3 = LinExpr(-Frac(2,3))
        self.b1 = LinExpr(1,'x1',2,'x2',3)
        self.b2 = LinExpr(5,'x1',3,'x2',-1)
        self._alle = [self.a1,self.a2,self.a3,self.b1,self.b2]
        # linear constraints
        self.c1 = LinCon(self.b1,'==',self.b2)
        self.c2 = LinCon(self.b1,'<=',self.b2)
        self.c3 = LinCon(self.b2,'>=',self.b1)
        self._allc = [self.c1,self.c2,self.c3]

    def tearDown(self):
        pass

    def test_copy(self):
        for c in self._allc:
            self.assertEqual(c,c.copy())

    def test_str(self):
        self.assertEqual(str(LinCon(self.a1,'<=',self.b1)),
                         '0 <= 1*x1 + 2*x2 + 3')
        self.assertEqual(str(LinCon(self.b1,'>=',self.a3)),
                         '1*x1 + 2*x2 + 3 >= -2/3')
        self.assertEqual(str(LinCon(self.b1,'==',self.b2)),
                         '1*x1 + 2*x2 + 3 == 5*x1 + 3*x2 - 1')

    def test_repr(self):
        for c in self._allc:
            self.assertEqual(c,eval(repr(c)))

    def test_reverse(self):
        self.assertEqual(self.c1.reverse(),LinCon(self.b2,'==',self.b1))
        self.assertEqual(self.c2.reverse(),self.c3)
        self.assertEqual(self.c3.reverse(),self.c2)

    def test_simplify(self):
        self.assertEqual(self.c1.simplify(),
                         LinCon(LinExpr(-4,'x1',-1,'x2'),'==',-4))
        self.assertEqual(self.c2.simplify(),
                         LinCon(LinExpr(-4,'x1',-1,'x2'),'<=',-4))
        self.assertEqual(self.c3.simplify(),
                         LinCon(LinExpr(4,'x1',1,'x2'),'>=',4))

    def test_evaluate(self):
        self.assertTrue(self.c1.evaluate({'x1':1,'x2':0}))
        self.assertFalse(self.c1.evaluate({'x1':'1/2','x2':'-1/3'}))
        self.assertTrue(self.c2.evaluate({'x1':1,'x2':1}))
        self.assertFalse(self.c2.evaluate({'x1':0,'x2':0}))
        self.assertTrue(self.c3.evaluate({'x1':1,'x2':1}))
        self.assertFalse(self.c3.evaluate({'x1':0,'x2':0}))

    def test_addLeft(self):
        c = self.c1.copy()
        c.addLeft('-1/6')
        self.assertEqual(c,LinCon(self.b1+'-1/6','==',self.b2))
        c = self.c1.copy()
        c.addLeft(self.a2)
        self.assertEqual(c,LinCon(self.b1+self.a2,'==',self.b2))
        c = self.c1.copy()
        c.addLeft(self.b2)
        self.assertEqual(c,LinCon(self.b1+self.b2,'==',self.b2))

    def test_addRight(self):
        c = self.c1.copy()
        c.addRight('-1/6')
        self.assertEqual(c,LinCon(self.b1,'==',self.b2+'-1/6'))
        c = self.c1.copy()
        c.addRight(self.a2)
        self.assertEqual(c,LinCon(self.b1,'==',self.b2+self.a2))
        c = self.c1.copy()
        c.addRight(self.b2)
        self.assertEqual(c,LinCon(self.b1,'==',self.b2+self.b2))

    def test_subLeft(self):
        c = self.c1.copy()
        c.subLeft('-1/6')
        self.assertEqual(c,LinCon(self.b1-'-1/6','==',self.b2))
        c = self.c1.copy()
        c.subLeft(self.a2)
        self.assertEqual(c,LinCon(self.b1-self.a2,'==',self.b2))
        c = self.c1.copy()
        c.subLeft(self.b2)
        self.assertEqual(c,LinCon(self.b1-self.b2,'==',self.b2))

    def test_subRight(self):
        c = self.c1.copy()
        c.subRight('-1/6')
        self.assertEqual(c,LinCon(self.b1,'==',self.b2-'-1/6'))
        c = self.c1.copy()
        c.subRight(self.a2)
        self.assertEqual(c,LinCon(self.b1,'==',self.b2-self.a2))
        c = self.c1.copy()
        c.subRight(self.b2)
        self.assertEqual(c,LinCon(self.b1,'==',self.b2-self.b2))
