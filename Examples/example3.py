# Adding package path to reference enumex
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from abc import ABC, abstractmethod
from enumex import IntFlagEx
from enum import auto

class A(ABC, IntFlagEx):
    Flag1 = auto()
    Flag2 = auto()

    @abstractmethod
    def print(self):
        pass

class B(A):
    Flag3 = auto()
    Flag4 = auto()

    def print(self):
        print(f"{self.__class__.__name__} {self.name} : {self.value}")

print(f"A(1) = ", end='')
try:
    v = A(1)
    print(v)
except Exception as e:
    print(f"Error:", e)

print(f"B(5) = {B(5):#b}")


print(f"\nA.Flag1 | B.Flag3 = ", end='')
try:
    v = A.Flag1 | B.Flag3 # Attempts to create A instance
    print(v)
except Exception as e:
    print(f"Error:", e)

v = B.Flag3 | A.Flag1
print(f"B.Flag3 | A.Flag1 = {v:#b}")


try:
	print("\nInvoking A.print...")
	for e in A:
	    e.print()  
except Exception as ex:
    print("Error: ", ex)

    print("\nManually Printing A...")
    for e in A:
        print(f"{e.__class__.__name__} {e.name} : {e.value}")

print("\nInvoking B.print...")
for e in B:
    e.print()

# > A(1) = Error: ("Can't instantiate abstract class A with abstract method", 'print')
# > B(5) = 0b101
# > 
# > A.Flag1 | B.Flag3 = Error: ("Can't instantiate abstract class A with abstract method", 'print')
# > B.Flag3 | A.Flag1 = 0b101
# > 
# > Invoking A.print...
# > Error:  Cannot call abstract method 'print' on abstract enum 'A'
# > 
# > Manually Printing A...
# > A Flag1 : 1
# > A Flag2 : 2
# > 
# > Invoking B.print...
# > B Flag1 : 1
# > B Flag2 : 2
# > B Flag3 : 4
# > B Flag4 : 8