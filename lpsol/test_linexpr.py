from fractions import Fraction as Frac
import unittest

from . import LinExpr, LinCon

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

    def test_getConstant(self):
        self.assertEqual(self.a1.getConstant(),0)
        self.assertEqual(self.a2.getConstant(),Frac(2,3))
        self.assertEqual(self.a3.getConstant(),-Frac(1,6))
        self.assertEqual(self.a4.getConstant(),-2)
        self.assertEqual(self.b1.getConstant(),0)
        self.assertEqual(self.b2.getConstant(),Frac(2,7))
        self.assertEqual(self.b3.getConstant(),Frac(-1,16))
        self.assertEqual(self.b4.getConstant(),0)

    def test_getCoefficient(self):
        self.assertEqual(self.a1.getCoefficient('x1'),0)
        self.assertEqual(self.a4.getCoefficient('some_var'),0)
        self.assertEqual(self.b1.getCoefficient('x1'),1)
        self.assertEqual(self.b3.getCoefficient('x3'),Frac(1,2))
        self.assertEqual(self.b2.getCoefficient('s1'),0)
        self.assertEqual(self.b4.getCoefficient('s2'),1)

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

    def test_constraintEq(self):
        self.assertEqual(self.a1.constrantEq(self.a2),LinCon(self.a1,'==',self.a2))
        self.assertEqual(self.a3.constrantEq(self.a4),LinCon(self.a3,'==',self.a4))
        self.assertEqual(self.b1.constrantEq(self.b2),LinCon(self.b1,'==',self.b2))
        self.assertEqual(self.b3.constrantEq(self.b4),LinCon(self.b3,'==',self.b4))

    def test_constraintLeq(self):
        self.assertEqual(self.a1.constraintLeq(self.a2),LinCon(self.a1,'<=',self.a2))
        self.assertEqual(self.a3.constraintLeq(self.a4),LinCon(self.a3,'<=',self.a4))
        self.assertEqual(self.b1.constraintLeq(self.b2),LinCon(self.b1,'<=',self.b2))
        self.assertEqual(self.b3.constraintLeq(self.b4),LinCon(self.b3,'<=',self.b4))

    def test_constraintGeq(self):
        self.assertEqual(self.a1.constraintGeq(self.a2),LinCon(self.a1,'>=',self.a2))
        self.assertEqual(self.a3.constraintGeq(self.a4),LinCon(self.a3,'>=',self.a4))
        self.assertEqual(self.b1.constraintGeq(self.b2),LinCon(self.b1,'>=',self.b2))
        self.assertEqual(self.b3.constraintGeq(self.b4),LinCon(self.b3,'>=',self.b4))

    def test_evaluate(self):
        zeros = {
            'x1': 0,
            'x2': 0,
            'x3': 0,
            's1': 0,
            's2': 0
        }
        for e in self._all:
            self.assertEqual(e.evaluate(zeros),e.getConstant())
        self.assertEqual(self.a3.evaluate({}),-Frac(1,6))
        self.assertEqual(self.a4.evaluate({}),-2)
        self.assertEqual(self.b1.evaluate({'x1':1,'x2':2,'x3':2}),4)
        self.assertEqual(self.b2.evaluate({'s1':51,'s2':'3/5','x1':'1/2'}),
                         Frac(-11,35))

    def test_substitute(self):
        for e in self._all:
            self.assertEqual(e,e.substitute({}))
        sub1 = {
            'x1': LinExpr(1,'s1',-1,'x4',1),
            'x2': LinExpr('1/4','x3','-3/2','x4',Frac(1,3))
        }
        self.assertEqual(self.b1.substitute(sub1),LinExpr(1,'s1',-4,'x4',Frac(5,3)))
        sub2 = {
            'x1': LinExpr(5),
            'x2': LinExpr(Frac(5,2),'x3',-1)
        }
        self.assertEqual(self.b3.substitute(sub2),LinExpr('-9/2','x3','-89/16'))
