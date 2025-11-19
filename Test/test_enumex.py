# Add package directory to path for debugging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest 
import enumex
from enumex import *
from enum import auto
from enum import Enum
from enum import IntEnum
from enum import Flag
from enum import IntFlag
from enum import StrEnum
from enum import ReprEnum
from enum import STRICT, CONFORM, EJECT, KEEP
from abc import ABC, abstractmethod
from typing import Union, Callable

class EnumExTests(unittest.TestCase):

    def test_standard_functionality(self):
        class A(EnumEx):
            V1 = auto()
            V2 = '2'
            V3 = 3

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(A.V1,     EnumEx)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual("A.V1",        str(A.V1))

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))

        with self.assertRaises(AttributeError) as ec:
            A.V1 = 1
        self.assertEqual("cannot reassign member 'V1'", ec.exception.args[0])

    def test_std_auto(self):
        class A(EnumEx):
            V1 = auto()
            V2 = auto()
        class B(A):
            V3 = auto()
            V4 = auto()

        self.assertEqual(1,     A.V1.value)
        self.assertEqual(2,     A.V2.value)
        self.assertEqual(3,     B.V3.value)
        self.assertEqual(4,     B.V4.value)

    def test_std_instancecheck(self):
        class A(EnumEx):
            V1 = auto()

        class B(IntEnumEx):
            V1 = auto()

        class C(FlagEx):
            V1 = auto()

        class D(IntFlagEx):
            V1 = auto()

        class E(StrEnumEx):
            V1 = auto()

        class F(int, ReprEnumEx):
            V1 = auto()

        def test_isinstance(localcls:type[EnumEx], intenum:bool, flag:bool, intflag:bool, reprenum:bool, strenum:bool):
            msg = f"Testing {localcls.__name__} is "
            value:EnumEx = localcls.V1
            self.assertIsInstance(                value, EnumEx,      msg + f"instance of EnumEx")
            self.assertEqual(intenum,  isinstance(value, IntEnumEx),  msg + f"{'' if intenum   else 'not '}instance of IntEnumEx")
            self.assertEqual(flag,     isinstance(value, FlagEx),     msg + f"{'' if flag      else 'not '}instance of FlagEx")
            self.assertEqual(intflag,  isinstance(value, IntFlagEx),  msg + f"{'' if intflag   else 'not '}instance of IntFlagEx")
            self.assertEqual(reprenum, isinstance(value, ReprEnumEx), msg + f"{'' if reprenum  else 'not '}instance of ReprEnumEx")
            self.assertEqual(strenum,  isinstance(value, StrEnumEx),  msg + f"{'' if strenum   else 'not '}instance of StrEnumEx")

        test_isinstance(A, intenum=False,  flag=False, intflag=False,  reprenum=False, strenum=False)   # EnumEx
        test_isinstance(B, intenum=True,   flag=False, intflag=False,  reprenum=True,  strenum=False)   # IntEnumEx
        test_isinstance(C, intenum=False,  flag=True,  intflag=False,  reprenum=False, strenum=False)   # FlagEx
        test_isinstance(D, intenum=False,  flag=True,  intflag=True,   reprenum=True,  strenum=False)   # IntFlagEx
        test_isinstance(E, intenum=False,  flag=False, intflag=False,  reprenum=True,  strenum=True)    # StrEnumEx
        test_isinstance(F, intenum=False,  flag=False, intflag=False,  reprenum=True,  strenum=False)   # ReprEnumEx

        def test_issubclass_std(extype:type[EnumEx], stdtype:type[Enum]):
            msg = f"Testing issubclass of {stdtype.__name__}"
            self.assertEqual(issubclass(EnumEx,      extype),    issubclass(EnumEx,      stdtype),  msg)
            self.assertEqual(issubclass(IntEnumEx,   extype),    issubclass(IntEnumEx,   stdtype),  msg)
            self.assertEqual(issubclass(IntFlagEx,   extype),    issubclass(IntFlagEx,   stdtype),  msg)
            self.assertEqual(issubclass(FlagEx,      extype),    issubclass(FlagEx,      stdtype),  msg)
            self.assertEqual(issubclass(ReprEnumEx,  extype),    issubclass(ReprEnumEx,  stdtype),  msg)
            self.assertEqual(issubclass(StrEnumEx,   extype),    issubclass(StrEnumEx,   stdtype),  msg)
    
            self.assertEqual(issubclass(A,           extype),    issubclass(A,           stdtype),  msg) # EnumEx
            self.assertEqual(issubclass(B,           extype),    issubclass(B,           stdtype),  msg) # IntEnumEx
            self.assertEqual(issubclass(C,           extype),    issubclass(C,           stdtype),  msg) # FlagEx
            self.assertEqual(issubclass(D,           extype),    issubclass(D,           stdtype),  msg) # IntFlagEx
            self.assertEqual(issubclass(E,           extype),    issubclass(E,           stdtype),  msg) # StrEnumEx
            self.assertEqual(issubclass(F,           extype),    issubclass(F,           stdtype),  msg) # ReprEnumEx

        def test_isinstance_std(localcls:type[EnumEx]):
            msg = f"Testing {localcls.__name__} isinstance of "
            val = localcls.V1
            self.assertIsInstance(      val, Enum,                                                  msg + f" {Enum.__name__}")
            self.assertEqual(isinstance(val, IntEnumEx),         isinstance(val, IntEnumEx),        msg + f" {IntEnumEx.__name__}")
            self.assertEqual(isinstance(val, IntFlagEx),         isinstance(val, IntFlagEx),        msg + f" {IntFlagEx.__name__}")
            self.assertEqual(isinstance(val, FlagEx),            isinstance(val, FlagEx),           msg + f" {FlagEx.__name__}")
            self.assertEqual(isinstance(val, ReprEnumEx),        isinstance(val, ReprEnumEx),       msg + f" {ReprEnumEx.__name__}")
            self.assertEqual(isinstance(val, StrEnumEx),         isinstance(val, StrEnumEx),        msg + f" {StrEnumEx.__name__}")

        test_issubclass_std(EnumEx,         Enum)
        test_issubclass_std(IntEnumEx,      IntEnum)
        test_issubclass_std(IntFlagEx,      IntFlag)
        test_issubclass_std(FlagEx,         Flag)
        test_issubclass_std(ReprEnumEx,     ReprEnum)
        test_issubclass_std(StrEnumEx,      StrEnum)

        test_isinstance_std(A)  # EnumEx
        test_isinstance_std(B)  # IntEnumEx
        test_isinstance_std(C)  # FlagEx
        test_isinstance_std(D)  # IntFlagEx
        test_isinstance_std(E)  # StrEnumEx
        test_isinstance_std(F)  # ReprEnumEx
    
    def test_enumex_auto_inheritance(self):
        class A(EnumEx):
            V1 = auto()
            V2 = '2'
            V3 = 3
        class B(A):
            V4 = auto()
            V5 = auto()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual(1,             B.V1.value)
        self.assertEqual('2',           B.V2.value)
        self.assertEqual(3,             B.V3.value)
        self.assertEqual(4,             B.V4.value)
        self.assertEqual(5,             B.V5.value)
        self.assertEqual("A.V1",        str(A.V1))
        self.assertEqual("B.V1",        str(B.V1))

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))
        self.assertListEqual([B.V1, B.V2, B.V3, B.V4, B.V5], list(B))

    def test_intenumex_auto_inheritance(self):
        class A(IntEnumEx):
            V1 = auto()
            V2 = auto()
            V3 = 3
        class B(A):
            V4 = auto()
            V5 = auto()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual(2,             A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual(1,             B.V1.value)
        self.assertEqual(2,             B.V2.value)
        self.assertEqual(3,             B.V3.value)
        self.assertEqual(4,             B.V4.value)
        self.assertEqual(5,             B.V5.value)
        self.assertGreater(B.V3,        A.V2)

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))
        self.assertListEqual([A.V1, A.V2, A.V3, B.V4, B.V5], list(B))

    def test_intflagex_auto_inheritance(self):
        class A(IntFlagEx):
            F1 = auto()
            F2 = auto()
            F3 = 0b1100
        class B(A):
            F4 = auto()
            F5 = auto()

        self.assertIsInstance(A.F1,     A)
        self.assertIsInstance(B.F1,     A)
        self.assertIsInstance(B.F4,     A)
        self.assertIsInstance(B.F1,     B)
        self.assertNotIsInstance(A.F1,  B)
        self.assertEqual(1,             A.F1.value)
        self.assertEqual(2,             A.F2.value)
        self.assertEqual(0b1100,        A.F3.value)
        self.assertEqual(1,             A.F1.value)
        self.assertEqual(2,             B.F2.value)
        self.assertEqual(0b1100,        B.F3.value)
        self.assertEqual(0b10000,       B.F4.value)
        self.assertEqual(0b100000,      B.F5.value)

        print(", ".join(str(v) for v in list(A)))
        print(", ".join(str(v) for v in list(B)))

        self.assertListEqual([A.F1, A.F2], list(A))
        self.assertListEqual([A.F1, A.F2, B.F4, B.F5], list(B))

    def test_strenumex_auto_inheritance(self):
        class A(StrEnumEx):
            V1 = auto()
            V2 = '2'
            V3 = V2
        class B(A):
            V4 = auto()
            V5 = auto()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertIsInstance(B.V1,     B)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual('v1',          A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual('2',           A.V3.value)
        self.assertEqual('v1',          B.V1.value)
        self.assertEqual('2',           B.V2.value)
        self.assertEqual('2',           B.V3.value)
        self.assertEqual('v4',          B.V4.value)
        self.assertEqual('v5',          B.V5.value)

        self.assertListEqual([A.V1, A.V3], list(A))
        self.assertListEqual([A.V1, A.V3, B.V4, B.V5], list(B))

    def test_errors(self):
        with self.assertRaises(TypeError) as ec:
            class A(EnumEx):
                V1 = auto()
                V2 = '2'
                V3 = 3
            class B(A):
                V3 = A.V3
        self.assertEqual("'V3' already defined as 3", ec.exception.args[0])
        
    def test_instance_methods(self):
        class A(EnumEx):
            V1 = auto()
            V2 = auto()

            def custom_format(self):
                return f"A.{self.name} : {self.value}"
        
        class B(A):
            V3 = auto()
            V4 = auto()

            def custom_format(self):
                return f"B.{self.name} : {self.value}"
        
        self.assertEqual("A.V1 : 1", A.V1.custom_format())
        self.assertEqual("B.V1 : 1", B.V1.custom_format())

    def test_abstract_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @abstractmethod
            def foo(self):
                pass

            @abstractmethod
            def bar(self):
                pass
            
            @abstractmethod
            def baz(self):
                pass

            @abstractmethod
            def doe(self):
                pass

            def doe(self):
                pass
            
        class B(A):
            V2 = auto()

            def foo(self):
                pass   

        class C(B):     
            def bar(self):
                pass
                   
        class D(C):
            def baz(self):
                pass

        class X(ABC, EnumEx):
            V1 = auto()
            def foo(self):
                pass

            @abstractmethod
            def foo(self):
                pass

        class Y(EnumEx):
            V1 = auto()
            def foo(self):
                pass

            @abstractmethod
            def foo(self):
                pass

        _assert_invalidabstract(self, A, 1, 'foo', 'bar', 'baz')
        _assert_invalidabstract(self, B, 1, 'bar', 'baz')
        _assert_invalidabstract(self, C, 1, 'baz')
        _assert_invalidabstract(self, X, 1, 'foo')

        v = D(1)
        v = Y(1)
        self.assertEqual(len(D.__abstractmethods__), 0, msg="D __abstractmethods__")

        with self.assertRaises(AttributeError) as ec:
            count = len(Y.__abstractmethods__)
        self.assertEqual("__abstractmethods__", ec.exception.args[0])
        # self.assertEqual(len(Y.__abstractmethods__), 1, msg="Y __abstractmethods__")

    def test_invoke_abstract_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @abstractmethod
            def foo(self):
                pass

        with self.assertRaises(TypeError) as ec:
            A.V1.foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0])

        foo = A.V1.foo
        self.assertIsInstance(foo, Callable)

        with self.assertRaises(TypeError) as ec:
            foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0])

    def test_invoke_derived_abstract_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @abstractmethod
            def foo(self):
                pass

        class B(A):
            V2 = auto()

        class C(A):
            V2 = auto()

            def foo(self):
                return 'bar'

        with self.assertRaises(TypeError) as ec:
            B.V1.foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'B'", ec.exception.args[0])

        foo = B.V1.foo
        self.assertIsInstance(foo, Callable)

        with self.assertRaises(TypeError) as ec:
            foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'B'", ec.exception.args[0])

        v = C.V2.foo()
        self.assertEqual('bar', v)

    def test_invoke_virtual_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @abstractmethod
            def foo(self):
                return "bar"

        class B(A):
            V2 = auto()

            def foo(self):
                return super().foo()

        res = B.V1.foo()
        self.assertEqual("bar", res)

        foo = B.V1.foo
        res = foo()
        self.assertEqual("bar", res)

    def test_invoke_abstract_properties(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @property
            @abstractmethod
            def foo(self):
                pass

        with self.assertRaises(TypeError) as ec:
            v = A.V1.foo
        self.assertEqual(f"Cannot get abstract property 'foo' on abstract enum 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            foo = getattr(A.V1, "foo")
        self.assertEqual("Cannot get abstract property 'foo' on abstract enum 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            A.V1.foo = "bar"
        self.assertEqual("Cannot set abstract property 'foo' on abstract enum 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            setattr(A.V1, "foo", "bar")
        self.assertEqual("Cannot set abstract property 'foo' on abstract enum 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            del A.V1.foo
        self.assertEqual("Cannot delete abstract property 'foo' on abstract enum 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            del A.V1.foo
        self.assertEqual("Cannot delete abstract property 'foo' on abstract enum 'A'", ec.exception.args[0])

        foo = A.foo
        self.assertIsInstance(foo, property) # enumex._AbstractEnumPropertyWrapper

        foo:property = getattr(A, "foo")
        self.assertIsInstance(foo, property) # enumex._AbstractEnumPropertyWrapper

        with self.assertRaises(TypeError) as ec:
            foo.__get__(A.V1) 
        self.assertEqual("Cannot get abstract property 'foo' on abstract enum 'A'", ec.exception.args[0])

    def test_invoke_abstract_class_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @classmethod
            @abstractmethod
            def foo(cls):
                pass

        with self.assertRaises(TypeError) as ec:
            A.foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0])

        foo = A.foo
        self.assertIsInstance(foo, Callable)

        with self.assertRaises(TypeError) as ec:
            foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0])

    def test_invoke_abstract_static_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @staticmethod
            @abstractmethod
            def foo():
                pass

        with self.assertRaises(TypeError) as ec:
            A.foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0])

        foo = A.foo
        self.assertIsInstance(foo, Callable)

        with self.assertRaises(TypeError) as ec:
            foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0])

    def test_invoke_abstract_methods_custom_getattr(self):
        class A(ABC, EnumEx):
            V1 = auto()
            
            @abstractmethod
            def foo(self):
                pass

            def __getattribute__(self, name):
                return Enum.__getattribute__(self, name)

        with self.assertRaises(TypeError) as ec:
            A.V1.foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0], msg="User defined __getattribute__ avoiding abstract check.")

        foo = A.V1.foo
        self.assertIsInstance(foo, Callable)

        with self.assertRaises(TypeError) as ec:
            foo()
        self.assertEqual("Cannot call abstract method 'foo' on abstract enum 'A'", ec.exception.args[0])

    def test_abstract_static_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()

            @staticmethod
            @abstractmethod
            def foo():
                pass
            
        class B(A):
            V2 = auto()    

            @staticmethod
            def foo():
                pass 

        _assert_invalidabstract(self, A, 1, 'foo')
        b = B(1)

    def test_abstract_class_methods(self):
        class A(ABC, EnumEx):
            V1 = auto()

            @classmethod
            @abstractmethod
            def foo(cls):
                pass
            
        class B(A):
            V2 = auto()    

            @classmethod
            def foo(cls):
                pass 

        _assert_invalidabstract(self, A, 1, 'foo')
        b = B(1)
        

    def test_abstract_properties(self):
        class A(ABC, EnumEx):
            V1 = auto()

            @property
            @abstractmethod
            def foo(self):
                pass
            
            @property
            @abstractmethod
            def bar(self):
                pass

            @abstractmethod
            def get_baz(self):
                pass

            @abstractmethod
            def set_baz(self, value):
                pass

            @abstractmethod
            def del_baz(self):
                pass

            baz = property(get_baz, set_baz, del_baz)  
            
        class B(A):
            V2 = auto()

            @property
            def foo(self):
                pass

            def get_baz(self):
                pass
            
            def set_baz(self, value):
                pass

            bar = property(get_baz)   

        class C(B):       
            @property
            def bar(self):
                return "C"

            def del_baz(self):
                pass

            baz = property(B.get_baz, B.set_baz, del_baz)  
            
        _assert_invalidabstract(self, A, 1, 'foo', 'bar', 'get_baz', 'set_baz', 'del_baz', 'baz')
        _assert_invalidabstract(self, B, 1, 'baz', 'del_baz') # TODO: Should it be returning baz? Older project version doesn't return it
        v = C(1)

    def test_flagex_operators(self):
        class A(FlagEx):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(Flag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
            F5 = auto()
            F6 = auto()

        or_std_result  = X.F3 | X.F1
        and_std_result = X.F1 & X.F1
        xor_std_result = X.F1 ^ X.F2
        or_result  = A.F3 | A.F1
        and_result = A.F1 & A.F1
        xor_result = A.F1 ^ A.F2

        self.assertIsInstance(or_result,  A,                        msg="OR is A")
        self.assertIsInstance(and_result, A,                        msg="AND is A")
        self.assertIsInstance(xor_result, A,                        msg="XOR is A")
        self.assertEqual(0b101,     or_result.value,                msg="A | A equal")
        self.assertEqual(1,         and_result.value,               msg="A & A equal")
        self.assertEqual(0b11,      xor_result.value,               msg="A ^ A equal")
        self.assertEqual(or_std_result.value, or_result.value,      msg="OR IntFlagEx == IntFlag")
        self.assertEqual(and_std_result.value, and_result.value,    msg="AND IntFlagEx == IntFlag")
        self.assertEqual(xor_std_result.value, xor_result.value,    msg="XOR IntFlagEx == IntFlag")

        or_std_result  = X.F3 | X.F1
        and_std_result = X.F1 & X.F1
        xor_std_result = X.F1 ^ X.F2
        or_result  = B.F3 | A.F1
        and_result = B.F1 & A.F1
        xor_result = B.F1 ^ A.F2

        self.assertIsInstance(or_result,  B,                        msg="OR is B")
        self.assertIsInstance(and_result, B,                        msg="AND is B")
        self.assertIsInstance(xor_result, B,                        msg="XOR is B")
        self.assertEqual(0b101,     or_result.value,                msg="B | A equal")
        self.assertEqual(1,         and_result.value,               msg="B & A equal")
        self.assertEqual(0b11,      xor_result.value,               msg="B ^ A equal")
        self.assertEqual(or_std_result.value, or_result.value,      msg="OR IntFlagEx == IntFlag")
        self.assertEqual(and_std_result.value, and_result.value,    msg="AND IntFlagEx == IntFlag")
        self.assertEqual(xor_std_result.value, xor_result.value,    msg="XOR IntFlagEx == IntFlag")

        with self.assertRaises(TypeError) as ec:
            or_result = 0b11 | A.F3
        self.assertEqual("unsupported operand type(s) for |: 'int' and 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            or_result = 0b11 & A.F3
        self.assertEqual("unsupported operand type(s) for &: 'int' and 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            or_result = 0b11 ^ A.F3
        self.assertEqual("unsupported operand type(s) for ^: 'int' and 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            shift_result = A.F1 << 2
        self.assertEqual("unsupported operand type(s) for <<: 'A' and 'int'", ec.exception.args[0])

    def test_flagex_operators_different_type(self):
        class A(FlagEx):
            F1 = auto()
            F2 = auto()

        class C(FlagEx):
            F1 = auto()
            F2 = auto()

        class D(ABC, FlagEx):
            F1 = auto()
            F2 = auto()

            @abstractmethod
            def foo(self):
                ...

        class E(ABC, IntFlagEx):
            F1 = auto()
            F2 = auto()

            @abstractmethod
            def foo(self):
                ...

        class F(ABC, IntEnumEx):
            F1 = auto()
            F2 = auto()

            @abstractmethod
            def foo(self):
                ...

        def test(right):
            with self.assertRaises(TypeError) as ec:
                result = A.F1 | right
            self.assertEqual(
                f"unsupported operand type(s) for |: 'A' and '{right.__class__.__name__}'", 
                ec.exception.args[0], 
                msg=f"FlagEx A OR {right.__class__.__name__} error message"
                )
 
            with self.assertRaises(TypeError) as ec:
                result = A.F1 & right
            self.assertEqual(
                f"unsupported operand type(s) for &: 'A' and '{right.__class__.__name__}'",
                  ec.exception.args[0],
                    msg=f"FlagEx A AND {right.__class__.__name__} error message"
                    )

            with self.assertRaises(TypeError) as ec:
                result = A.F1 ^ right
            self.assertEqual(
                f"unsupported operand type(s) for ^: 'A' and '{right.__class__.__name__}'", 
                ec.exception.args[0], 
                msg=f"FlagEx A XOR {right.__class__.__name__} error message"
                )

        test(C.F2)
        test(D.F2)
        test(E.F2)
        test(F.F2)

    def test_intflagex_operators_different_type_instance(self):
        class A(IntFlagEx):
            F1 = auto()
            F2 = auto()

        class C(IntFlagEx):
            F1 = auto()
            F2 = auto()

        class D(ABC, IntFlagEx):
            F1 = auto()
            F2 = auto()

            @abstractmethod
            def foo(self):
                ...

        class E(ABC, IntEnumEx):
            F1 = auto()
            F2 = auto()

            @abstractmethod
            def foo(self):
                ...

        class X(IntFlag):
            F1 = auto()
            F2 = auto()

        def test(left:IntFlagEx, right):
            or_result = left | right
            and_result = left & right
            xor_result = left ^ right

            self.assertIsInstance(or_result, left.__class__, msg=f"{left} OR {right} is {left.__class__.__name__}")
            self.assertIsInstance(and_result, left.__class__, msg=f"{left} AND {right} is {left.__class__.__name__}")
            self.assertIsInstance(xor_result, left.__class__, msg=f"{left} XOR {right} is {left.__class__.__name__}")

        test(A.F1, C.F2)
        test(A.F1, D.F2)
        test(A.F1, E.F2)
        test(A.F1, X.F2)

    def test_flagex_not_operator_default(self):
        from enum import Flag
        class A(FlagEx):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(Flag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class Y(Flag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
            F5 = auto()
            F6 = auto()

        std_result = ~X.F1
        not_result = ~A.F1
        expected = ~1 & 0b1111

        self.assertIsInstance(not_result, A,                    msg="NOT is A")
        self.assertEqual(expected, not_result.value,            msg="~ equal")
        self.assertEqual(std_result.value, not_result.value,    msg="~IntFlagEx == ~IntFlag")

        std_result = ~Y.F5
        not_result = ~B.F5
        expected = ~(1 << 4) & 0b111111

        self.assertIsInstance(not_result, B,                    msg="NOT is B")
        self.assertEqual(expected, not_result.value,            msg="~ equal")
        self.assertEqual(std_result.value, not_result.value,    msg="~IntFlagEx == ~IntFlag")

    def test_intflagex_operators(self):
        class A(IntFlagEx):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(IntFlag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()

        or_result       = A.F3 | 0b11
        and_result      = A.F1 & 0b11
        xor_result      = A.F1 ^ 0b11
        or_std_result   = X.F3 | 0b11
        and_std_result  = X.F1 & 0b11
        xor_std_result  = X.F1 ^ 0b11

        self.assertIsInstance(or_result,    A,              msg="OR is A")
        self.assertIsInstance(and_result,   A,              msg="AND is A")
        self.assertIsInstance(xor_result,   A,              msg="XOR is A")
        self.assertEqual(0b111,             or_result,      msg="A | int OR")
        self.assertEqual(1,                 and_result,     msg="A & int AND")
        self.assertEqual(0b10,              xor_result,     msg="A ^ int XOR")
        self.assertEqual(or_std_result,     or_result,      msg="IntFlagEx == IntFlag OR")
        self.assertEqual(and_std_result,    and_result,     msg="IntFlagEx == IntFlag AND")
        self.assertEqual(xor_std_result,    xor_result,     msg="IntFlagEx == IntFlag XOR")

        or_result  = A.F3 | A.F1
        and_result = A.F1 & A.F1
        xor_result = A.F1 ^ (A.F2 | 0b101)

        self.assertIsInstance(or_result,  A,    msg="OR is A")
        self.assertIsInstance(and_result, A,    msg="AND is A")
        self.assertIsInstance(xor_result, A,    msg="XOR is A")
        self.assertEqual(0b101,     or_result,  msg="A | A equal")
        self.assertEqual(1,         and_result, msg="A & A equal")
        self.assertEqual(0b110,     xor_result, msg="A ^ A equal")

        or_result  = B.F5 | 0b11
        and_result = B.F1 & 0b11
        xor_result = B.F1 ^ 0b10

        self.assertIsInstance(or_result,  B,    msg="OR is B")
        self.assertIsInstance(and_result, B,    msg="AND is B")
        self.assertIsInstance(xor_result, B,    msg="XOR is B")
        self.assertEqual(0b10011,   or_result,  msg="B | int equal")
        self.assertEqual(1,         and_result, msg="B & int equal")
        self.assertEqual(0b11,      xor_result, msg="B ^ int equal")

        or_result  = B.F3 | A.F1
        and_result = B.F1 & A.F1
        xor_result = B.F1 ^ A.F2

        self.assertIsInstance(or_result,  B,    msg="OR is B")
        self.assertIsInstance(and_result, B,    msg="AND is B")
        self.assertIsInstance(xor_result, B,    msg="XOR is B")
        self.assertEqual(0b101,     or_result,  msg="B | A equal")
        self.assertEqual(1,         and_result, msg="B & A equal")
        self.assertEqual(0b11,      xor_result, msg="B ^ A equal")

        or_result  = 0b11 | A.F3
        and_result = 0b11 & A.F1
        xor_result = 0b10 ^ A.F1

        self.assertIsInstance(or_result,  A,    msg="OR is A")
        self.assertIsInstance(and_result, A,    msg="AND is A")
        self.assertIsInstance(xor_result, A,    msg="XOR is A")
        self.assertEqual(0b111, or_result,      msg="int | A equal")
        self.assertEqual(1,     and_result,     msg="int & A equal")
        self.assertEqual(0b11,  xor_result,     msg="int ^ A equal")

    def test_intflagex_operators_abstract(self):
        class A(ABC, IntFlagEx):
            F1 = auto()
            F2 = auto()

            @abstractmethod
            def foo(self):
                pass

        class B(A):
            F3 = auto()
            F4 = auto()

            def foo(self):
                return 'foo'

        # Just test so see it doesnt raise
        or_result  = B.F3 | 0b11
        and_result = B.F1 & 0b11
        xor_result = B.F1 ^ 0b10
        a_lshift_result = A.F1 << 3
        a_rshift_result = A.F2 >> 1
        b_lshift_result = B.F1 << 3
        b_rshift_result = B.F4 >> 3

        self.assertIsInstance(or_result,  B,            msg="OR is B")
        self.assertIsInstance(and_result, B,            msg="AND is B")
        self.assertIsInstance(xor_result, B,            msg="XOR is B")
        self.assertIsInstance(a_lshift_result, int,     msg="A << is int")
        self.assertIsInstance(a_rshift_result, int,     msg="A >> is int")
        self.assertIsInstance(b_lshift_result, int,     msg="B << is int")
        self.assertIsInstance(b_rshift_result, int,     msg="B >> is int")
        self.assertNotIsInstance(a_lshift_result, A,    msg="A << is not A")
        self.assertNotIsInstance(a_rshift_result, A,    msg="A >> is not A")
        self.assertNotIsInstance(b_lshift_result, B,    msg="B << is not B")
        self.assertNotIsInstance(b_rshift_result, B,    msg="B >> is not B")
        self.assertEqual(0b111,     or_result,          msg="B | int equal")
        self.assertEqual(1,         and_result,         msg="B & int equal")
        self.assertEqual(0b11,      xor_result,         msg="B ^ int equal")
        self.assertEqual(0b1000,    a_lshift_result,    msg="A << int equal")
        self.assertEqual(0b1,       a_rshift_result,    msg="A >> int equal")
        self.assertEqual(0b1000,    b_lshift_result,    msg="B << int equal")
        self.assertEqual(0b1,       b_rshift_result,    msg="B >> int equal")

        or_result  = B.F3 | A.F1
        and_result = B.F1 & A.F1
        xor_result = B.F1 ^ A.F2
        a_lshift_result = A.F1 << A.F2
        a_rshift_result = A.F2 >> B.F1
        b_lshift_result = B.F1 << A.F2
        b_rshift_result = B.F4 >> A.F2

        self.assertIsInstance(or_result,  B,            msg="OR is B")
        self.assertIsInstance(and_result, B,            msg="AND is B")
        self.assertIsInstance(xor_result, B,            msg="XOR is B")
        self.assertIsInstance(a_lshift_result, int,     msg="A << is int")
        self.assertIsInstance(a_rshift_result, int,     msg="A >> is int")
        self.assertIsInstance(b_lshift_result, int,     msg="B << is int")
        self.assertIsInstance(b_rshift_result, int,     msg="B >> is int")
        self.assertNotIsInstance(a_lshift_result, A,    msg="A << is not A")
        self.assertNotIsInstance(a_rshift_result, A,    msg="A >> is not A")
        self.assertNotIsInstance(b_lshift_result, B,    msg="B << is not B")
        self.assertNotIsInstance(b_rshift_result, B,    msg="B >> is not B")
        self.assertEqual(0b101,     or_result,          msg="B | A equal")
        self.assertEqual(1,         and_result,         msg="B & A equal")
        self.assertEqual(0b11,      xor_result,         msg="B ^ A equal")
        self.assertEqual(0b100,     a_lshift_result,    msg="A << A equal")
        self.assertEqual(0b1,       a_rshift_result,    msg="A >> B equal")
        self.assertEqual(0b100,     b_lshift_result,    msg="B << A equal")
        self.assertEqual(0b10,      b_rshift_result,    msg="B >> A equal")

        # Test to ensure it raises
        _assert_invalidabstract(self, A, lambda: A.F1 | B.F3,  'foo')
        _assert_invalidabstract(self, A, lambda: A.F1 & B.F1,  'foo')
        _assert_invalidabstract(self, A, lambda: A.F1 ^ B.F2,  'foo')
        _assert_invalidabstract(self, A, lambda: ~A.F1,        'foo')

    def test_intflagex_lshift_operator(self):
        class A(IntFlagEx):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        shift_result = A.F1 << 3
        self.assertIsInstance(shift_result, int,   msg="A << is int")
        self.assertNotIsInstance(shift_result, A,  msg="A << is not int")
        self.assertEqual(0b1000, shift_result,     msg="A << equal")

        shift_result = B.F1 << 4
        self.assertIsInstance(shift_result, int,   msg="B << is int")
        self.assertNotIsInstance(shift_result, B,  msg="B << is not B")
        self.assertEqual(0b10000, shift_result,    msg="B << equal")

    def test_intflagex_rshift_operator(self):
        class A(IntFlagEx):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        shift_result = A.F4 >> 3
        self.assertIsInstance(shift_result, int,   msg="A >> is int")
        self.assertNotIsInstance(shift_result, A,  msg="A >> is not int")
        self.assertEqual(0b1, shift_result,        msg="A >> equal")

        shift_result = B.F6 >> 2
        self.assertIsInstance(shift_result, int,   msg="B >> is int")
        self.assertNotIsInstance(shift_result, B,  msg="B >> is not B")
        self.assertEqual(0b1000, shift_result,     msg="B >> equal")

    def test_flagex_missing(self):
        with self.assertRaises(ValueError) as ec:
            class A(FlagEx):
                V1 = auto()

            v = A(0b10)
        self.assertEqual("<flag 'A'> invalid value 2\n    given 0b0 10\n  allowed 0b0 01", ec.exception.args[0])

        class B(IntFlagEx):
            V1 = auto()

        v = B(0b10)
        self.assertIsInstance(v, B)
        self.assertEqual(0b10, v.value)

    def test_intflagex_not_operator_default(self):
        class A(IntFlagEx):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(IntFlag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class Y(IntFlag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
            F5 = auto()
            F6 = auto()

        std_result = ~X.F1
        not_result = ~A.F1
        expected = ~1 & 0b1111

        self.assertIsInstance(not_result, A,     msg="NOT is A")
        self.assertEqual(expected, not_result,   msg="~ equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

        std_result = ~Y.F5
        not_result = ~B.F5
        expected = ~(1 << 4) & 0b111111

        self.assertIsInstance(not_result, B,     msg="NOT is B")
        self.assertEqual(expected, not_result,   msg="~ equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

    def test_intflagex_not_operator_strict(self):
        class A(IntFlagEx, boundary=STRICT):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(IntFlag, boundary=STRICT):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()

        std_result = ~X.F1
        not_result = ~A.F1

        self.assertIsInstance(not_result, A,     msg="NOT is A")
        self.assertEqual(0b1110,    not_result,  msg="NOT equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

        not_result = ~B.F5
        self.assertIsInstance(not_result, B,     msg="NOT is B")
        self.assertEqual(0b101111,  not_result,  msg="NOT equal")

        with self.assertRaises(ValueError) as ec:
            not_result = ~(A(B.F5 | 0b10_000_000))
        self.assertEqual("<flag 'B'> invalid value 144\n    given 0b0 10010000\n  allowed 0b0 00111111",
                        ec.exception.args[0],
                        msg="STRICT NOT error message"
        )


    def test_intflagex_not_operator_conform(self):
        class A(IntFlagEx, boundary=CONFORM):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(IntFlag, boundary=CONFORM):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()

        std_result = ~X.F1
        not_result = ~A.F1

        self.assertIsInstance(not_result, A,     msg="NOT is A")
        self.assertEqual(0b1110,    not_result,  msg="NOT equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

        not_result = ~B.F5
        self.assertIsInstance(not_result, B,     msg="NOT is B")
        self.assertEqual(0b101111,  not_result,  msg="NOT equal")

        std_result = ~(X(B.F5 | 0b10_000_000))
        not_result = ~(A(B.F5 | 0b10_000_000))
        expected_result = ~0b10_010_000 & 0b1111
        self.assertIsInstance(not_result, A,            msg="NOT is A")
        self.assertEqual(expected_result, not_result,   msg="NOT equal")
        self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

    def test_intflagex_not_operator_eject(self):
        class A(IntFlagEx, boundary=EJECT):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(IntFlag, boundary=EJECT):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()

        std_result = ~X.F1
        not_result = ~A.F1

        self.assertIsInstance(not_result, A,     msg="NOT is A")
        self.assertEqual(0b1110,    not_result,  msg="NOT equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

        not_result = ~B.F5
        self.assertIsInstance(not_result, B,     msg="NOT is B")
        self.assertEqual(0b101111,  not_result,  msg="NOT equal")

        std_result = ~(X(B.F5 | 0b10_000_000))
        not_result = ~(A(B.F5 | 0b10_000_000))
        expected_result = ~0b10_010_000
        self.assertIsInstance(not_result, int,          msg="NOT is int")
        self.assertNotIsInstance(not_result, A,         msg="NOT is not A")
        self.assertEqual(expected_result, not_result,   msg="NOT equal")
        self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

    def test_intflagex_not_operator_keep(self):
        class A(IntFlagEx, boundary=KEEP):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class B(A):
            F5 = auto()
            F6 = auto()

        class X(IntFlag, boundary=KEEP):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()

        std_result = ~X.F1
        not_result = ~A.F1

        self.assertIsInstance(not_result, A,     msg="NOT is A")
        self.assertEqual(0b1110,    not_result,  msg="NOT equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

        not_result = ~B.F5
        self.assertIsInstance(not_result, B,     msg="NOT is B")
        self.assertEqual(0b101111,  not_result,  msg="NOT equal")

        # std_result = ~(X(0b10_000_000))
        # not_result = ~(A(0b10_000_000))
        # expected_result = ~0b10_000_000
        # self.assertIsInstance(not_result, A,            msg="NOT is A")
        # self.assertEqual(expected_result, not_result,   msg="NOT equal")
        # self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

        std_result = ~(X(B.F5 | 0b10_000_000))
        not_result = ~(A(B.F5 | 0b10_000_000))
        expected_result = ~0b10_010_000 & 0b11_111_111
        self.assertIsInstance(not_result, A,            msg="NOT is A")
        self.assertEqual(expected_result, not_result,   msg="NOT equal")
        self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

    def test_flagexboundary_strict(self):
        class A(IntFlagEx, boundary=STRICT):
            F1 = auto()

        with self.assertRaises(ValueError) as ec:
            v = A(2)
        self.assertEqual("<flag 'A'> invalid value 2\n    given 0b0 10\n  allowed 0b0 01", 
                        ec.exception.args[0],  msg="FlagExBoundary STRICT error message")

    def test_flagexboundary_conform(self):
        class A(IntFlagEx, boundary=CONFORM):
            F1 = auto()

        v = A(3)
        self.assertIsInstance(v, A,             msg="FlagExBoundary CONFORM isinstance A")
        self.assertEqual(A.F1, v,               msg="FlagExBoundary CONFORM equal")

    def test_flagexboundary_eject(self):
        class A(IntFlagEx, boundary=EJECT):
            F1 = auto()

        v = A(2)
        self.assertIsInstance(v, int,           msg="FlagExBoundary CONFORM isinstance int")
        self.assertNotIsInstance(v, FlagEx,     msg="FlagExBoundary CONFORM not isinstance FlagEx")
        self.assertEqual(2, v,                  msg="FlagExBoundary CONFORM equal")

    def test_flagexboundary_keep(self):
        class A(IntFlagEx, boundary=KEEP):
            F1 = auto()

        v = A(2)
        self.assertIsInstance(v, A,             msg="FlagExBoundary CONFORM isinstance A")
        self.assertEqual(2, v.value,            msg="FlagExBoundary CONFORM equal")

    def test__generate_next_value__references(self):
        class _EnumEx(EnumEx):
            V1 = auto()

        class _IntEnumEx(IntEnum):
            V1 = auto()

        class _FlagEx(FlagEx):
            V1 = auto()

        class _IntFlagEx(IntFlagEx):
            V1 = auto()

        class _StrEnumEx(StrEnumEx):
            V1 = auto()

        class _ReprEx(int, ReprEnumEx):
            V1 = auto()

        # TODO: Add other Flag methods
        self.assertIs(_FlagEx._generate_next_value_, Flag._generate_next_value_)
        self.assertIs(_IntFlagEx._generate_next_value_, IntFlag._generate_next_value_)
        self.assertIs(_StrEnumEx._generate_next_value_, StrEnum._generate_next_value_)

def _assert_invalidabstract(case:unittest.TestCase, cls:EnumEx, initvalue:Union[object,Callable], *args):
    with case.assertRaises(TypeError) as ec:
        if isinstance(initvalue, Callable):
            v = initvalue()
        else:
            v = cls(initvalue)
    count = len(args)
    case.assertEqual(len(cls.__abstractmethods__), count, msg="Assert __abstractmethods__")
    case.assertEqual(count + 1, len(ec.exception.args), msg="Exception args length of abstract methods")
    case.assertEqual(f"Can't instantiate abstract class {cls.__name__} with abstract method{'' if count == 1 else 's'}", ec.exception.args[0], msg="_enforce_abstract error message")
    method_args = ec.exception.args[1:]
    for arg in args:
        case.assertIn(arg, method_args, msg="Abstract method in exception args.")

def _get_raises(func:Callable, *args):
    try:
        func(*args)
        return False
    except:
        return True

if __name__ == "__main__":
    unittest.main()