from fractions import Fraction as Frac
from typing import Any
import unittest

from . import LinVar

class LinVarTest(unittest.TestCase):
    '''
    tests for (integer) linear programming variable
    '''

    def setUp(self):
        # continuous
        self.a1 = LinVar('x',False)
        self.a2 = LinVar('x',False,0)
        self.a3 = LinVar('x',False,None,0)
        self.a4 = LinVar('x',False,-5,5)
        self.a5 = LinVar('x',False,'1/3','4/3')
        self.a6 = LinVar('x',False,'1/5','4/5')
        self.a7 = LinVar('x',False,'-9/7','-5/7')
        self.a8 = LinVar('x',False,'1/2','-1/2')
        self.a9 = LinVar('x',False,'3/2','1/2')
        self._a_all = [self.a1,self.a2,self.a3,self.a4,self.a5,
                       self.a6,self.a7,self.a8,self.a9]
        # integral
        self.b1 = LinVar('x',True)
        self.b2 = LinVar('x',True,0)
        self.b3 = LinVar('x',True,None,0)
        self.b4 = LinVar('x',True,-5,5)
        self.b5 = LinVar('x',True,'1/3','4/3')
        self.b6 = LinVar('x',True,'1/5','4/5')
        self.b7 = LinVar('x',True,'-9/7','-5/7')
        self.b8 = LinVar('x',True,'1/2','-1/2')
        self.b9 = LinVar('x',True,'3/2','1/2')
        self._b_all = [self.b1,self.b2,self.b3,self.b4,self.b5,
                       self.b6,self.b7,self.b8,self.b9]

    def tearDown(self):
        pass

    def test_copy(self):
        for a in self._a_all+self._b_all:
            self.assertEqual(a,a.copy())

    def assertEqBounds(self, a: tuple[Any,Any], b: tuple[Any,Any]):
        a0,a1 = a
        b0,b1 = b
        if a0 is not None:
            a0 = Frac(a0)
        if a1 is not None:
            a1 = Frac(a1)
        if b0 is not None:
            b0 = Frac(b0)
        if b1 is not None:
            b1 = Frac(b1)
        self.assertTrue(a0 == b0 and a1 == b1, f'{a} != {b}')

    def test_getBounds(self):
        self.assertEqBounds(self.a1.getBounds(),(None,None))
        self.assertEqBounds(self.a2.getBounds(),(0,None))
        self.assertEqBounds(self.a3.getBounds(),(None,0))
        self.assertEqBounds(self.a4.getBounds(),(-5,5))
        self.assertEqBounds(self.a5.getBounds(),('1/3','4/3'))
        self.assertEqBounds(self.a6.getBounds(),('1/5','4/5'))
        self.assertEqBounds(self.a7.getBounds(),('-9/7','-5/7'))
        self.assertEqBounds(self.a8.getBounds(),('1/2','-1/2'))
        self.assertEqBounds(self.a9.getBounds(),('3/2','1/2'))
        self.assertEqBounds(self.b1.getBounds(),(None,None))
        self.assertEqBounds(self.b2.getBounds(),(0,None))
        self.assertEqBounds(self.b3.getBounds(),(None,0))
        self.assertEqBounds(self.b4.getBounds(),(-5,5))
        self.assertEqBounds(self.b5.getBounds(),(1,1))
        self.assertEqBounds(self.b6.getBounds(),(1,0))
        self.assertEqBounds(self.b7.getBounds(),(-1,-1))
        self.assertEqBounds(self.b8.getBounds(),(1,-1))
        self.assertEqBounds(self.b9.getBounds(),(2,0))

    def test_boundAbove(self):
        self.a1.boundAbove('-8/7')
        self.assertEqBounds(self.a1.getBounds(),(None,'-8/7'))
        self.a1.boundAbove(3)
        self.assertEqBounds(self.a1.getBounds(),(None,'-8/7'))
        self.a1.boundAbove(-2)
        self.assertEqBounds(self.a1.getBounds(),(None,-2))
        self.b1.boundAbove('7/2')
        self.assertEqBounds(self.b1.getBounds(),(None,3))
        self.b1.boundAbove(-2)
        self.assertEqBounds(self.b1.getBounds(),(None,-2))
        self.b1.boundAbove(-Frac(1,2))
        self.assertEqBounds(self.b1.getBounds(),(None,-2))

    def test_boundBelow(self):
        self.a1.boundBelow(-3)
        self.assertEqBounds(self.a1.getBounds(),(-3,None))
        self.a1.boundBelow(-Frac(17,5))
        self.assertEqBounds(self.a1.getBounds(),(-3,None))
        self.a1.boundBelow(Frac(1,2))
        self.assertEqBounds(self.a1.getBounds(),(Frac(1,2),None))
        self.b1.boundBelow(-Frac(17,5))
        self.assertEqBounds(self.b1.getBounds(),(-3,None))
        self.b1.boundBelow(2)
        self.assertEqBounds(self.b1.getBounds(),(2,None))
        self.b1.boundBelow(Frac(9,5))
        self.assertEqBounds(self.b1.getBounds(),(2,None))

    def test_isFeasible(self):
        self.assertTrue(self.a1.isFeasible())
        self.assertTrue(self.a2.isFeasible())
        self.assertTrue(self.a3.isFeasible())
        self.assertTrue(self.a4.isFeasible())
        self.assertTrue(self.a5.isFeasible())
        self.assertTrue(self.a6.isFeasible())
        self.assertTrue(self.a7.isFeasible())
        self.assertFalse(self.a8.isFeasible())
        self.assertFalse(self.a9.isFeasible())
        self.assertTrue(self.b1.isFeasible())
        self.assertTrue(self.b2.isFeasible())
        self.assertTrue(self.b3.isFeasible())
        self.assertTrue(self.b4.isFeasible())
        self.assertTrue(self.b5.isFeasible())
        self.assertFalse(self.b6.isFeasible())
        self.assertTrue(self.b7.isFeasible())
        self.assertFalse(self.b8.isFeasible())
        self.assertFalse(self.b9.isFeasible())

    def test_str(self):
        self.assertEqual(str(self.a1),'x@R[-inf,+inf]')
        self.assertEqual(str(self.a2),'x@R[0,+inf]')
        self.assertEqual(str(self.a3),'x@R[-inf,0]')
        self.assertEqual(str(self.a4),'x@R[-5,5]')
        self.assertEqual(str(self.a5),'x@R[1/3,4/3]')
        self.assertEqual(str(self.a6),'x@R[1/5,4/5]')
        self.assertEqual(str(self.a7),'x@R[-9/7,-5/7]')
        self.assertEqual(str(self.a8),'x@R[1/2,-1/2]')
        self.assertEqual(str(self.a9),'x@R[3/2,1/2]')
        self.assertEqual(str(self.b1),'x@Z[-inf,+inf]')
        self.assertEqual(str(self.b2),'x@Z[0,+inf]')
        self.assertEqual(str(self.b3),'x@Z[-inf,0]')
        self.assertEqual(str(self.b4),'x@Z[-5,5]')
        self.assertEqual(str(self.b5),'x@Z[1,1]')
        self.assertEqual(str(self.b6),'x@Z[1,0]')
        self.assertEqual(str(self.b7),'x@Z[-1,-1]')
        self.assertEqual(str(self.b8),'x@Z[1,-1]')
        self.assertEqual(str(self.b9),'x@Z[2,0]')

    def test_repr(self):
        for a in self._a_all+self._b_all:
            self.assertTrue(eval(repr(a)) == a)
