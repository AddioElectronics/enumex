# enumex

An extension to the standard enum with polymorphism, and abstract methods.

## Install

**Python**: 3.9.0 to 3.13.x

Each package version is tightly coupled to the minor Python version.
Depending on which Python version your environment is currently using, pip will install the correct package.

``` bash
pip install enumex
```


## Usage

### Importing

EnumEx works alongside the standard library’s `enum` module.  
Use `EnumEx` from `enumex`, and `auto` from `enum`:

``` python
from enumex import EnumEx
from enum import auto
```

**EnumEx Types**:
| Type | Min Version |
|--|--|
| EnumEx | all |
| IntEnumEx | all |
| FlagEx | all |
| IntFlagEx | all |
| StrEnumEx | 3.11 |
| ReprEnumEx | 3.11 |

### Example

EnumEx behaves like the standard enum, but supports inheritance and abstract enum classes.

``` python
from enumex import EnumEx
from enum import auto

class A(EnumEx):
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
# > B Val3 : 3
# > B Val4 : 4
```

### Abstract Methods

- **Defining Abstract Enum Classes**  
To define an abstract enum class, you must include `ABC` as a mixin.  
Using `ABCMeta` as the metaclass is **not** enough by itself.
`EnumExMeta` inherits from `enum.EnumMeta`, and to avoid metaclass conflicts when combining it with `ABC`, it must also inherit from `ABCMeta`.  
Because of this, abstract-method enforcement was changed to only activate when the enum **actually subclasses `ABC`**.

- **Member Access Behavior**  
  Enum members of an abstract enum (e.g., `A.Flag1`) are still accessible.  
  This is by design: abstractness is enforced only when invoking abstract methods.

- **Instantiation Behavior**  
  Even though calling an enum class (`A(1)`) normally just performs a member lookup, an exception is still raised when the class is abstract.  

``` python
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
	v  =  A(1)
	print(v)
except  Exception  as  e:
	print(f"Error:", e)  

print(f"B(5) = {B(5):#b}")  
 

print(f"\nA.Flag1 | B.Flag3 = ", end='')
try:
	v = A.Flag1 | B.Flag3 # Attempts to create A instance
	print(v)
except Exception  as  e:
	print(f"Error:", e)

v = B.Flag3 | A.Flag1
print(f"B.Flag3 | A.Flag1 = {v:#b}") 

try:
	print("\nInvoking A.print...")
	for  e  in  A:
		e.print()
except  Exception  as  ex:
	print("Error: ", ex)
  
print("\nManually Printing A...")
for  e  in  A:
	print(f"{e.__class__.__name__}  {e.name} : {e.value}") 

print("\nInvoking B.print...")
for  e  in  B:
	e.print()
  
# > A(1) = Error: ("Can't instantiate abstract class A with abstract method", 'print')
# > B(5) = 0b101
# >
# > A.Flag1 | B.Flag3 = Error: ("Can't instantiate abstract class A with abstract method", 'print')
# > B.Flag3 | A.Flag1 = 0b101
# >
# > Invoking A.print...
# > Error: Cannot call abstract method 'print' on abstract enum 'A'
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
```




## License
[Python](https://github.com/python/cpython/blob/main/LICENSE)