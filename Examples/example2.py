# Adding package path to reference enumex
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from enum import auto
from enumex import IntFlagEx

class A(IntFlagEx):
    Val1 = auto()
    Val2 = auto()

    def print(self):
        print(f"{self.__class__.__name__} {self.name} : {self.value}")

class B(A):
    Val3 = auto()
    Val4 = auto()

print("Printing A...")
for e in A:
    e.print()

print("\nPrinting B...")
for e in B:
    e.print()

# > Printing A...
# > A Val1 : 1
# > A Val2 : 2
# > 
# > Printing B...
# > B Val1 : 1
# > B Val2 : 2
# > B Val3 : 4
# > B Val4 : 8