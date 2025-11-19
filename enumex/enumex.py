import threading
from types import DynamicClassAttribute
from abc import ABC, ABCMeta
import enum
from enum import Enum, IntEnum, Flag, IntFlag
from enum import _EnumDict, _make_class_unpicklable
from typing import Callable

__all__ = [
        'EnumExMeta',
        'EnumEx', 'IntEnumEx', 'FlagEx', 'IntFlagEx',
        ]

# Dummy value for Enum and Flag as there are explicit checks for them
# before they have been created.
# This is also why there are checks in EnumType like `if Enum is not None`
EnumEx = FlagEx = EJECT = ReprEnumEx = None
# EnumEx = FlagEx = EJECT = _stdlib_enumexs = ReprEnumEx = None

def _is_std_enum_type(type):
    return type in (Enum, IntEnum, Flag, IntFlag)

def _is_abstract_enum(cls):
    if issubclass(cls, EnumEx):
        # Call EnumMeta directly to avoid checking thread state
        if enum.EnumMeta.__getattribute__(cls, "_isabstractenum_") and hasattr(cls, "__abstractmethods__"):
            abstract_methods = enum.EnumMeta.__getattribute__(cls, "__abstractmethods__")
            if abstract_methods and len(abstract_methods) != 0:
                return True

    return False

def _enforce_abstract(cls):
    """
    Raises a TypeError if an attempt to instantiate an unimplemented abstract enum is made.

    The EnumTypeEx metaclass does not create instances with __init__(), so we have to check for unimplemented abstract methods manually.
    """

    if _is_abstract_enum(cls):
        # Call EnumMeta directly to avoid checking thread state
        methods = enum.EnumMeta.__getattribute__(cls, "__abstractmethods__")
        raise TypeError(f"Can't instantiate abstract class {cls.__name__} with abstract method{'' if len(methods) == 1 else 's'}", *methods)
    

class _AbstractEnumMethodWrapper:
    def __init__(self, func:Callable, enum_class):
        self.func = func
        self.enum_class = enum_class
        self.__name__ = func.__name__
        self.__qualname__ = func.__qualname__
        self.__isabstractmethod__ = True
        self.__doc__ = func.__doc__

        if hasattr(func, "__self__"):
            self.__self__ = func.__self__
    
    def __call__(self, *args, **kwds):
        raise TypeError(
                f"Cannot call abstract method '{self.func.__name__}' "
                f"on abstract enum '{self.enum_class.__name__}'"
            )
    
class _AbstractEnumPropertyWrapper(property):
    def __init__(self, prop:property, name, enum_class):
        super().__init__(prop.fget, prop.fset, prop.fdel, prop.__doc__)
        self.prop = prop
        self.enum_class = enum_class
        self.name = name
        # self.__doc__ = prop.__doc__
        
    def __get__(self, instance, owner = None):
        raise TypeError(
                f"Cannot get abstract property '{self.name}' "
                f"on abstract enum '{self.enum_class.__name__}'"
            )
    
    def __set__(self, instance, value):
        raise TypeError(
                f"Cannot set abstract property '{self.name}' "
                f"on abstract enum '{self.enum_class.__name__}'"
            )
    
    def __delete__(self, instance):
        raise TypeError(
                f"Cannot delete abstract property '{self.name}' "
                f"on abstract enum '{self.enum_class.__name__}'"
            )


_thread_state = threading.local()

def _reentering(key):
    return getattr(_thread_state, key, False)

def _enter(key):
    setattr(_thread_state, key, True)
    # _thread_state.in_check = True

def _exit(key):
    setattr(_thread_state, key, False)
    # _thread_state.in_check = False

class EnumExType(enum.EnumMeta, ABCMeta):
    """
    Metaclass for EnumEx
    """

    @classmethod
    def __prepare__(metacls, cls, bases, **kwds):
        # create the namespace dict
        enum_dict = _EnumDict()
        enum_dict._cls_name = cls
        # inherit previous flags and _generate_next_value_ function
        member_type, first_enum = metacls._get_mixins_(cls, bases)
        first_std_base = metacls._find_std_type_(cls, bases)
        if first_enum is not None:
            enum_dict['_generate_next_value_'] = getattr(
                    first_std_base, '_generate_next_value_', None,
                    )
            
        metacls._copy_existing_members(cls, bases, enum_dict)

        return enum_dict
    
    @staticmethod
    def _copy_existing_members(cls, bases, enum_dict):
        if len(bases) > 0:
            members = getattr(bases[0], "__members__", None)
            if members:
                for k, v in members.items():
                    enum_dict[k] = v.value
    
    def __new__(metacls, cls, bases, classdict):
        # an Enum class is final once enumeration items have been defined; it
        # cannot be mixed with other types (int, float, etc.) if it has an
        # inherited __new__ unless a new __new__ is defined (or the resulting
        # class will fail).
        #
        # remove any keys listed in _ignore_
        classdict.setdefault('_ignore_', []).append('_ignore_')
        ignore = classdict['_ignore_']
        for key in ignore:
            classdict.pop(key, None)
        member_type, first_enum = metacls._get_mixins_(cls, bases)
        __new__, save_new, use_args = metacls._find_new_(classdict, member_type,
                                                        first_enum)

        # save enum items into separate mapping so they don't get baked into
        # the new class
        enum_members = {k: classdict[k] for k in classdict._member_names}
        for name in classdict._member_names:
            del classdict[name]

        # adjust the sunders
        _order_ = classdict.pop('_order_', None)

        # check for illegal enum names (any others?)
        invalid_names = set(enum_members) & {'mro', ''}
        if invalid_names:
            raise ValueError('Invalid enum member name: {0}'.format(
                ','.join(invalid_names)))

        # create a default docstring if one has not been provided
        if '__doc__' not in classdict:
            classdict['__doc__'] = 'An enumeration.'

        enum_class = type.__new__(metacls, cls, bases, classdict)
        enum_class._member_names_ = []               # names in definition order
        enum_class._member_map_ = {}                 # name->value map
        enum_class._member_type_ = member_type

        # save DynamicClassAttribute attributes from super classes so we know
        # if we can take the shortcut of storing members in the class dict
        dynamic_attributes = {
                k for c in enum_class.mro()
                for k, v in c.__dict__.items()
                if isinstance(v, DynamicClassAttribute)
                }

        # Reverse value->name map for hashable values.
        enum_class._value2member_map_ = {}

        # If a custom type is mixed into the Enum, and it does not know how
        # to pickle itself, pickle.dumps will succeed but pickle.loads will
        # fail.  Rather than have the error show up later and possibly far
        # from the source, sabotage the pickle protocol for this class so
        # that pickle.dumps also fails.
        #
        # However, if the new class implements its own __reduce_ex__, do not
        # sabotage -- it's on them to make sure it works correctly.  We use
        # __reduce_ex__ instead of any of the others as it is preferred by
        # pickle over __reduce__, and it handles all pickle protocols.
        if '__reduce_ex__' not in classdict:
            if member_type is not object:
                methods = ('__getnewargs_ex__', '__getnewargs__',
                        '__reduce_ex__', '__reduce__')
                if not any(m in member_type.__dict__ for m in methods):
                    _make_class_unpicklable(enum_class)

        # instantiate them, checking for duplicates as we go
        # we instantiate first instead of checking for duplicates first in case
        # a custom __new__ is doing something funky with the values -- such as
        # auto-numbering ;)
        for member_name in classdict._member_names:
            value = enum_members[member_name]
            if not isinstance(value, tuple):
                args = (value, )
            else:
                args = value
            if member_type is tuple:   # special case for tuple enums
                args = (args, )     # wrap it one more time
            if not use_args:
                enum_member = __new__(enum_class)
                if not hasattr(enum_member, '_value_'):
                    enum_member._value_ = value
            else:
                enum_member = __new__(enum_class, *args)
                if not hasattr(enum_member, '_value_'):
                    if member_type is object:
                        enum_member._value_ = value
                    else:
                        enum_member._value_ = member_type(*args)
            value = enum_member._value_
            enum_member._name_ = member_name
            enum_member.__objclass__ = enum_class
            enum_member.__init__(*args)
            # If another member with the same value was already defined, the
            # new member becomes an alias to the existing one.
            for name, canonical_member in enum_class._member_map_.items():
                if canonical_member._value_ == enum_member._value_:
                    enum_member = canonical_member
                    break
            else:
                # Aliases don't appear in member names (only in __members__).
                enum_class._member_names_.append(member_name)
            # performance boost for any member that would not shadow
            # a DynamicClassAttribute
            if member_name not in dynamic_attributes:
                setattr(enum_class, member_name, enum_member)
            # now add to _member_map_
            enum_class._member_map_[member_name] = enum_member
            try:
                # This may fail if value is not hashable. We can't add the value
                # to the map, and by-value lookups for this value will be
                # linear.
                enum_class._value2member_map_[value] = enum_member
            except TypeError:
                pass

        # double check that repr and friends are not the mixin's or various
        # things break (such as pickle)
        # however, if the method is defined in the Enum itself, don't replace
        # it
        for name in ('__repr__', '__str__', '__format__', '__reduce_ex__'):
            if name in classdict:
                continue
            class_method = getattr(enum_class, name)
            obj_method = getattr(member_type, name, None)
            enum_method = getattr(first_enum, name, None)
            if obj_method is not None and obj_method is class_method:
                setattr(enum_class, name, enum_method)

        # replace any other __new__ with our own (as long as Enum is not None,
        # anyway) -- again, this is to support pickle
        if EnumEx is not None:
            # if the user defined their own __new__, save it before it gets
            # clobbered in case they subclass later
            if save_new:
                enum_class.__new_member__ = __new__
            enum_class.__new__ = EnumEx.__new__

        # py3 support for definition order (helps keep py2/py3 code in sync)
        if _order_ is not None:
            if isinstance(_order_, str):
                _order_ = _order_.replace(',', ' ').split()
            if _order_ != enum_class._member_names_:
                raise TypeError('member order does not match _order_')
            
        if issubclass(enum_class, ABC):
            # This python version handles class initializing quite differently than newer versions.
            # Newer versions don't rely on object.__new__ to initialize values, where this version does not.
            # Using object.__new__ causes the "Can't insantiate abstract class..." error during value initialization.
            # Because we have to inherit ABCMeta to allow ABC to be used, and can't use ABCMeta.__new__ or the error will raise,
            # we have to handle updating __abstractmethods__ ourself (As well as raising the error).
            # We could import _abc._abc_init right here and call it, this would build __abstractmethods__ and avoid raising during value initialization,
            # but we'd still have to raise the error manually, because Enum internally does a lookup and never calls object.__new__,
            # and the only enum types that actually creates new instances are Flag, and IntFlag via _missing_/_create_pseudo.., and IntFlag uses int.__new__ instead.
            # This would also mean _abc_impl would be created and never used (apart from FlagEx).
            enum_class.__abstractmethods__ = None
            _update_abstractmethods(enum_class)
            setattr(enum_class, '_isabstractenum_', True)
            EnumExType._install_abstract_getattribute(enum_class)
            EnumExType._install_abstract_setattr(enum_class)
            EnumExType._install_abstract_delattr(enum_class)
        else:
            setattr(enum_class,'_isabstractenum_', False)
            
        return enum_class
    
    # Override type checks so ABCMeta doesn't raise errors
    # See more info in EnumExType.__new__, where _update_abstractmethods is invoked.
    def __subclasscheck__(cls, subclass):
        return cls in enum.EnumMeta.__getattribute__(subclass, "__mro__")
    
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(instance.__class__)

    @classmethod
    def _check_for_existing_members_(mcls, class_name, bases):
        pass # Allow inheritance

    @staticmethod
    def _find_std_type_(class_name, bases):
        for chain in bases:
            for base in chain.__mro__:
                if _is_std_enum_type(base):
                    return base
        raise TypeError("EnumEx missing a std Enum base.")
    
    @staticmethod
    def _get_mixins_(class_name, bases):
        """Returns the type for creating enum members, and the first inherited
        enum class.

        bases: the tuple of bases that was given to __new__

        """
        if not bases or (len(bases) == 1 and bases[0] is Enum):
            return object, EnumEx

        def _find_data_type(bases):
            data_types = []
            for chain in bases:
                candidate = None
                for base in chain.__mro__:
                    if base in (object, ABC):
                        continue
                    elif '__new__' in base.__dict__:
                        if issubclass(base, Enum):
                            continue
                        data_types.append(candidate or base)
                        break
                    elif not issubclass(base, Enum):
                        candidate = base
            if len(data_types) > 1:
                raise TypeError('%r: too many data types: %r' % (class_name, data_types))
            elif data_types:
                return data_types[0]
            else:
                return None

        # ensure final parent class is an Enum derivative, find any concrete
        # data type, and check that Enum has no members
        # If the last base is a std enum, skip it to find the first EnumEx base.
        first_enumex = bases[-1] if len(bases) == 1 or not _is_std_enum_type(bases[-1]) else bases[-2]
        if not issubclass(first_enumex, Enum):
            raise TypeError("new enumerations should be created as "
                    "`EnumName([mixin_type, ...] [data_type,] enum_type)`")
        member_type = _find_data_type(bases) or object
        return member_type, first_enumex
    
    # If enum.EnumMeta's _find_new_ is used, EnumEx.__new__ is called during class initialization instead of object.__new__
    @staticmethod
    def _find_new_(classdict, member_type, first_enum):
        """
        Returns the __new__ to be used for creating the enum members.


        classdict: the class dictionary given to __new__
        member_type: the data type whose __new__ will be used by default
        first_enum: enumeration to check for an overriding __new__

        """
        # now find the correct __new__, checking to see of one was defined
        # by the user; also check earlier enum classes in case a __new__ was
        # saved as __new_member__
        __new__ = classdict.get('__new__', None)

        # should __new__ be saved as __new_member__ later?
        save_new = __new__ is not None

        if __new__ is None:
            # check all possibles for __new_member__ before falling back to
            # __new__
            for method in ('__new_member__', '__new__'):
                for possible in (member_type, first_enum):
                    target = getattr(possible, method, None)
                    if target not in {
                            None,
                            None.__new__,
                            object.__new__,
                            Enum.__new__,
                            EnumEx.__new__,
                            }:
                        __new__ = target
                        break
                if __new__ is not None:
                    break
            else:
                __new__ = object.__new__

        # if a non-object.__new__ is used then whatever value/tuple was
        # assigned to the enum member name will be passed to __new__ and to the
        # new enum member's __init__
        if __new__ is object.__new__:
            use_args = False
        else:
            use_args = True
        return __new__, save_new, use_args
    
    def __getattribute__(cls, name):

        attr = super().__getattribute__(name)
        
        if EnumEx is None or _reentering('type_getattr'):
            return attr
        
        _enter('type_getattr')
        try:
            if callable(attr) and not isinstance(attr, type):
                # Check if enum is abstract before checking method, as this is called during initialization of __abstractmethods__
                # _isabstractenum_ is set after they are initialized, so it will return the real method until after.
                if _is_abstract_enum(cls) and getattr(attr, "__isabstractmethod__", False):
                    return _AbstractEnumMethodWrapper(attr, cls)
            elif isinstance(attr, property):
                if _is_abstract_enum(cls) and getattr(attr, "__isabstractmethod__", False):
                    return _AbstractEnumPropertyWrapper(attr, name, cls)

        except Exception as ex:
            raise ex
        finally:
            _exit('type_getattr')

        return attr
    
    # Installs __getattribute__ with abstract method checks on the enum class.
    # Installed at end of class creation to stop user defined __getattribute__ from avoiding abstract check.
    @staticmethod
    def _install_abstract_getattribute(cls:type):
        original_getattribute = cls.__getattribute__

        # Ensures custom_getattribute isn't called more than once
        if original_getattribute.__name__ == 'custom_getattribute':
            original_getattribute = original_getattribute._original_getattribute_

        def custom_getattribute(self, name):
            if EnumEx is None or _reentering('inst_getattr'):
                return original_getattribute(self, name)
            
            _enter('inst_getattr')
            try:
                # Find the descriptor on the class without triggering property.__get__
                descr = self.__class__.__dict__.get(name, None)

                if isinstance(descr, property):
                    # Unfortunately there is no way to invoke the base __getattribute__ without invoking the property,
                    # so just use the dictionary lookup value
                    attr = descr
                else:
                    attr = original_getattribute(self, name)

                if callable(attr) and not isinstance(attr, type):
                    cls = type(self)
                    # Check if method is abstract before checking class, as this may be called before the class is fully initialized.
                    if getattr(attr, "__isabstractmethod__", False) and _is_abstract_enum(cls):
                        return _AbstractEnumMethodWrapper(attr, cls)
                elif isinstance(attr, property):
                    cls = type(self)
                    if _is_abstract_enum(cls) and getattr(attr, "__isabstractmethod__", False):
                        raise TypeError(
                            f"Cannot get abstract property '{name}' "
                            f"on abstract enum '{cls.__name__}'"
                        )

            except Exception as ex:
                raise ex
            finally:
                _exit('inst_getattr')

            return attr

        cls.__getattribute__ = custom_getattribute
        cls.__getattribute__._original_getattribute_ = original_getattribute # Store the original base so custom_getattribute isn't called more than once
        
    # Installs __setattr__ with abstract property checks on the enum class.
    # Installed at end of class creation to stop python from invoking __set__ on the property
    # and to stop user defined __setattr__ from avoiding abstract check.
    @staticmethod
    def _install_abstract_setattr(cls:type):
        original_setattribute = cls.__setattr__

        # Ensures custom_getattribute isn't called more than once
        if original_setattribute.__name__ == 'custom_getattribute':
            original_setattribute = original_setattribute._original_setattribute_

        def custom_setattribute(self, name, value):
            if EnumEx is None or _reentering('inst_setattr'):
                return original_setattribute(self, name, value)
            
            _enter('inst_setattr')
            try:
                # Find the descriptor on the class without triggering property.__get__
                descr = self.__class__.__dict__.get(name, None)

                if isinstance(descr, property):
                    cls = type(self)
                    if _is_abstract_enum(cls) and getattr(descr, "__isabstractmethod__", False):
                        raise TypeError(
                                f"Cannot set abstract property '{name}' "
                                f"on abstract enum '{cls.__name__}'"
                            )
                else:
                    original_setattribute(self, name, value)

            except Exception as ex:
                raise ex
            finally:
                _exit('inst_setattr')

        cls.__setattr__ = custom_setattribute
        cls.__setattr__._original_setattribute_ = original_setattribute # Store the original base so custom_setattribute isn't called more than once

    # Installs __delattr__ with abstract property checks on the enum class.
    # Installed at end of class creation to stop python from invoking __delete__ on the property
    # and to stop user defined __delattr__ from avoiding abstract check.
    @staticmethod
    def _install_abstract_delattr(cls:type):
        original___delattr__ = cls.__delattr__

        # Ensures custom_getattribute isn't called more than once
        if original___delattr__.__name__ == 'custom_getattribute':
            original___delattr__ = original___delattr__._original__delattr__

        def custom_delattr(self, name):
            if EnumEx is None or _reentering('inst_delattr'):
                return original___delattr__(self, name)
            
            _enter('inst_delattr')
            try:
                # Find the descriptor on the class without triggering property.__get__
                descr = self.__class__.__dict__.get(name, None)

                if isinstance(descr, property):
                    cls = type(self)
                    if _is_abstract_enum(cls) and getattr(descr, "__isabstractmethod__", False):
                        raise TypeError(
                                f"Cannot delete abstract property '{name}' "
                                f"on abstract enum '{cls.__name__}'"
                            )
                else:
                    original___delattr__(self, name)

            except Exception as ex:
                raise ex
            finally:
                _exit('inst_delattr')

        cls.__delattr__ = custom_delattr
        cls.__delattr__._original__delattr__ = original___delattr__ # Store the original base so custom___delattr__ isn't called more than once
        
    
EnumExMeta = EnumExType

class EnumEx(Enum, metaclass=EnumExMeta):
    
    def __new__(cls, value):
        _enforce_abstract(cls)
        return Enum.__new__(cls, value)

class IntEnumEx(IntEnum, EnumEx):
    """Enum where members are also (and must be) ints"""

class FlagEx(Flag, EnumEx):
    def _get_value(self, flag):
        if (isinstance(flag, self.__class__) 
            # If right(flag) is a base of left, return its value to stop it from creating a base instance.
            or (isinstance(flag, FlagEx) and isinstance(self, flag.__class__))):
            return flag._value_
        elif self._member_type_ is not object and isinstance(flag, self._member_type_):
            return flag
        return NotImplemented
    
    def __or__(self, other):
        other_value = self._get_value(other)
        if other_value is NotImplemented:
            return NotImplemented
        value = self._value_
        return self.__class__(value | other_value)

    def __and__(self, other):
        other_value = self._get_value(other)
        if other_value is NotImplemented:
            return NotImplemented
        value = self._value_
        return self.__class__(value & other_value)

    def __xor__(self, other):
        other_value = self._get_value(other)
        if other_value is NotImplemented:
            return NotImplemented
        value = self._value_
        return self.__class__(value ^ other_value)
    
    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__
    
class IntFlagEx(IntFlag, FlagEx):
    """Support for integer-based Flags"""

# _stdlib_enumexs = IntEnumEx, StrEnumEx, IntFlagEx



# We have to hold a copy from a newer python version because abc doesn't expose it.
def _update_abstractmethods(cls):
    """Recalculate the set of abstract methods of an abstract class.

    If a class has had one of its abstract methods implemented after the
    class was created, the method will not be considered implemented until
    this function is called. Alternatively, if a new abstract method has been
    added to the class, it will only be considered an abstract method of the
    class after this function is called.

    This function should be called before any use is made of the class,
    usually in class decorators that add methods to the subject class.

    Returns cls, to allow usage as a class decorator.

    If cls is not an instance of ABCMeta, does nothing.
    """
    if not hasattr(cls, '__abstractmethods__'):
        # We check for __abstractmethods__ here because cls might by a C
        # implementation or a python implementation (especially during
        # testing), and we want to handle both cases.
        return cls
    
    abstracts = set()
    # Check the existing abstract methods of the parents, keep only the ones
    # that are not implemented.
    for scls in cls.__bases__:
        for name in getattr(scls, '__abstractmethods__', ()):
            value = getattr(cls, name, None)
            if getattr(value, "__isabstractmethod__", False):
                abstracts.add(name)
    # Also add any other newly added abstract methods.
    for name, value in cls.__dict__.items():
        if getattr(value, "__isabstractmethod__", False):
            abstracts.add(name)
    cls.__abstractmethods__ = frozenset(abstracts)
    return cls