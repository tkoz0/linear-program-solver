from fractions import Fraction as Frac
import unittest

from . import LinExpr

class LinExprTest(unittest.TestCase):
    '''
    tests for linear expression
    '''

    def setUp(self):
        # depends on __init__
        self.a1 = LinExpr()
        self.a2 = LinExpr('2/3')
        self.a3 = LinExpr(Frac(-1,6))
        self.a4 = LinExpr(-2)
        self.b1 = LinExpr(1,'x1',2,'x2',-Frac(1,2),'x3')
        self.b2 = LinExpr(0,'s1',-1,'s2',Frac(2,7))
        self.b3 = LinExpr('-3/2','x1',Frac(1,2),'x3',-2,'x2','-1/16')
        self.b4 = LinExpr(4,'x3','3/2','x1',-1,'s1',1,'s2')
        self._all = [
            self.a1, self.a2, self.a3, self.a4,
            self.b1, self.b2, self.b3, self.b4
        ]

    def tearDown(self):
        pass

    def test_copy(self):
        for e in self._all:
            self.assertEqual(e.copy(),e)

    def test_str(self):
        self.assertEqual(str(self.a1),'0')
        self.assertEqual(str(self.a2),'2/3')
        self.assertEqual(str(self.a3),'-1/6')
        self.assertEqual(str(self.a4),'-2')
        self.assertEqual(str(self.b1),'1*x1 + 2*x2 - 1/2*x3')
        self.assertEqual(str(self.b2),'- 1*s2 + 2/7')
        self.assertEqual(str(self.b3),'- 3/2*x1 - 2*x2 + 1/2*x3 - 1/16')
        self.assertEqual(str(self.b4),'- 1*s1 + 1*s2 + 3/2*x1 + 4*x3')
        self.assertNotEqual(str(self.a1),'')
        self.assertNotEqual(str(self.a4),'2')

    def test_repr(self):
        for e in self._all:
            self.assertEqual(eval(repr(e)),e)

    def test_iadd(self):
        # depends on copy
        a = self.a1.copy()
        a += '2/3'
        self.assertEqual(a,self.a2)
        a += self.a3
        self.assertEqual(a,LinExpr('1/2'))
        self.assertEqual(a,Frac(1,2))
        self.assertEqual(a,'1/2')
        self.assertEqual(a,'2/4')
        a += self.b3
        self.assertEqual(a,LinExpr('-3/2','x1',-2,'x2','1/2','x3','7/16'))
        a += LinExpr('3/2','x1',Frac(-1,2),'x3',Frac(-7,16))
        self.assertEqual(a,LinExpr(-2,'x2'))
        a += LinExpr(1,'x1',2,'x2',-1)
        self.assertEqual(a,LinExpr(1,'x1',-1))

    def test_isub(self):
        # depends on copy
        a = self.a1.copy()
        a -= '-5'
        self.assertEqual(a,LinExpr(5))
        a -= self.a3
        self.assertEqual(a,LinExpr(-Frac(-31,6)))
        a -= self.b2
        self.assertEqual(a,LinExpr('1','s2','205/42'))
        a -= LinExpr(1,'s2',Frac(205,42))
        self.assertEqual(a,0)
        self.assertEqual(a,'0')
        a -= self.b4
        self.assertEqual(a,LinExpr(1,'s1',-1,'s2',-4,'x3',-Frac(3,2),'x1'))
        a -= self.b3
        self.assertEqual(a,LinExpr('-9/2','x3',0,'x1',2,'x2',
                                   -1,'s2',1,'s1',Frac(1,16)))

    def test_neg(self):
        self.assertEqual(-self.a1,LinExpr())
        self.assertEqual(-self.a2,'-2/3')
        self.assertEqual(-self.a3,'1/6')
        self.assertEqual(-self.a4,2)
        self.assertEqual(-self.b1,LinExpr('1/2','x3',-2,'x2',-1,'x1'))
        self.assertEqual(-self.b2,LinExpr('1','s2','-2/7'))
        self.assertEqual(-self.b3,LinExpr(Frac(3,2),'x1',2,'x2',-Frac(1,2),'x3',
                                          Frac(1,16)))
        self.assertEqual(-self.b4,LinExpr(1,'s1',-1,'s2',Frac(-3,2),'x1',
                                          -4,'x3'))

    def test_pos(self):
        for e in self._all:
            self.assertEqual(+e,e)

    def test_add(self):
        self.assertEqual(self.a3+self.a4,'-13/6')
        self.assertEqual(self.a2+'-2/3',0)
        self.assertEqual(self.a1+self.b3,self.b3)
        self.assertEqual(self.b3+self.b4,LinExpr(-1,'s1',1,'s2',0,'x1',
                                                 -2,'x2','9/2','x3','-1/16'))
        self.assertEqual(self.a2+LinExpr('2/3','x1'),LinExpr('2/3','x1','2/3'))

    def test_radd(self):
        self.assertEqual(6+self.b1,LinExpr(1,'x1',2,'x2','-1/2','x3',6))
        self.assertEqual('3/2'+LinExpr(),'3/2')

    def test_sub(self):
        self.assertEqual(self.a3-self.a4,'11/6')
        self.assertEqual(self.a4-self.b2,LinExpr(1,'s2',-Frac(16,7)))
        self.assertEqual(self.b4-self.b1,LinExpr('9/2','x3','1/2','x1',-1,
                                                 's1',1,'s2',-2,'x2'))

    def test_rsub(self):
        self.assertEqual('2/3'-self.a2,self.a1)
        self.assertEqual(3-self.b2,LinExpr(1,'s2',Frac(19,7)))

    def test_conEq(self):
        pass

    def test_conLe(self):
        pass

    def test_conGe(self):
        pass

    def test_subst(self):
        pass
