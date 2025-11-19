import threading
from abc import ABC, ABCMeta, update_abstractmethods
import enum
from enum import Enum, IntEnum, Flag, IntFlag, StrEnum, ReprEnum
from enum import _is_single_bit, _proto_member
from enum import _EnumDict
from enum import STRICT, CONFORM, EJECT, KEEP
from typing import Callable

__all__ = [
        'EnumExType', 'EnumExMeta',
        'EnumEx', 'IntEnumEx', 'StrEnumEx', 'FlagEx', 'IntFlagEx', 'ReprEnumEx',
        ]

# Dummy value for Enum and Flag as there are explicit checks for them
# before they have been created.
# This is also why there are checks in EnumType like `if Enum is not None`
EnumEx = FlagEx = ReprEnumEx = None
# EnumEx = FlagEx = _stdlib_enumexs = ReprEnumEx = None

def _is_std_enum_type(type):
    return type in (Enum, IntEnum, Flag, IntFlag, StrEnum, ReprEnum)

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
        member_type, first_enum, first_std_base = metacls._get_mixins_(cls, bases)
        if first_enum is not None:
            enum_dict['_generate_next_value_'] = getattr(
                    first_std_base, '_generate_next_value_', None,
                    )
        
        # Copy member values to enum_dict from base for _generate_next_value_
        metacls._copy_existing_members(cls, bases, enum_dict)
        return enum_dict
    
    @staticmethod
    def _copy_existing_members(cls, bases, enum_dict):
        if len(bases) > 0:
            members = getattr(bases[0], "__members__", None)
            if members:
                for k, v in members.items():
                    enum_dict[k] = v.value

    def __new__(metacls, cls, bases, classdict, *, boundary=None, _simple=False, **kwds):
        # an Enum class is final once enumeration items have been defined; it
        # cannot be mixed with other types (int, float, etc.) if it has an
        # inherited __new__ unless a new __new__ is defined (or the resulting
        # class will fail).
        #
        if _simple:
            return type.__new__(metacls, cls, bases, classdict, **kwds)
        #
        # remove any keys listed in _ignore_
        classdict.setdefault('_ignore_', []).append('_ignore_')
        ignore = classdict['_ignore_']
        for key in ignore:
            classdict.pop(key, None)
        #
        # grab member names
        member_names = classdict._member_names
        #
        # check for illegal enum names (any others?)
        invalid_names = set(member_names) & {'mro', ''}
        if invalid_names:
            raise ValueError('invalid enum member name(s) %s'  % (
                    ','.join(repr(n) for n in invalid_names)
                    ))
        #
        # adjust the sunders
        _order_ = classdict.pop('_order_', None)
        # convert to normal dict
        classdict = dict(classdict.items())
        #
        # data type of member and the controlling Enum class
        member_type, first_enum, std_base = metacls._get_mixins_(cls, bases)
        __new__, save_new, use_args = metacls._find_new_(
                classdict, member_type, first_enum,
                )
        classdict['_new_member_'] = __new__
        classdict['_use_args_'] = use_args
        #
        # convert future enum members into temporary _proto_members
        for name in member_names:
            value = classdict[name]
            classdict[name] = _proto_member(value)
        #
        # house-keeping structures
        classdict['_member_names_'] = []
        classdict['_member_map_'] = {}
        classdict['_value2member_map_'] = {}
        classdict['_unhashable_values_'] = []
        classdict['_member_type_'] = member_type
        # now set the __repr__ for the value
        classdict['_value_repr_'] = metacls._find_data_repr_(cls, bases)
        #
        # Flag structures (will be removed if final class is not a Flag
        classdict['_boundary_'] = (
                boundary
                or getattr(first_enum, '_boundary_', None)
                )
        classdict['_flag_mask_'] = 0
        classdict['_singles_mask_'] = 0
        classdict['_all_bits_'] = 0
        classdict['_inverted_'] = None
        try:
            exc = None
            enum_class = type.__new__(metacls, cls, bases, classdict, **kwds)
        except RuntimeError as e:
            # any exceptions raised by member.__new__ will get converted to a
            # RuntimeError, so get that original exception back and raise it instead
            exc = e.__cause__ or e
        if exc is not None:
            raise exc
        #
        # update classdict with any changes made by __init_subclass__
        classdict.update(enum_class.__dict__)
        #
        # double check that repr and friends are not the mixin's or various
        # things break (such as pickle)
        # however, if the method is defined in the Enum itself, don't replace
        # it
        #
        # Also, special handling for ReprEnum
        if ReprEnumEx is not None and ReprEnumEx in bases:
            if member_type is object:
                raise TypeError(
                        'ReprEnum subclasses must be mixed with a data type (i.e.'
                        ' int, str, float, etc.)'
                        )
            if '__format__' not in classdict:
                enum_class.__format__ = member_type.__format__
                classdict['__format__'] = enum_class.__format__
            if '__str__' not in classdict:
                method = member_type.__str__
                if method is object.__str__:
                    # if member_type does not define __str__, object.__str__ will use
                    # its __repr__ instead, so we'll also use its __repr__
                    method = member_type.__repr__
                enum_class.__str__ = method
                classdict['__str__'] = enum_class.__str__
        for name in ('__repr__', '__str__', '__format__', '__reduce_ex__'):
            if name not in classdict:
                # check for mixin overrides before replacing
                enum_method = getattr(first_enum, name)
                found_method = getattr(enum_class, name)
                object_method = getattr(object, name)
                data_type_method = getattr(member_type, name)
                if found_method in (data_type_method, object_method):
                    setattr(enum_class, name, enum_method)
        #
        # for Flag, add __or__, __and__, __xor__, and __invert__
        if FlagEx is not None and issubclass(enum_class, FlagEx):
            for name in (
                    '__or__', '__and__', '__xor__',
                    '__ror__', '__rand__', '__rxor__',
                    '__invert__'
                ):
                if name not in classdict:
                    enum_method = getattr(Flag, name)
                    setattr(enum_class, name, enum_method)
                    classdict[name] = enum_method
        #
        # replace any other __new__ with our own (as long as Enum is not None,
        # anyway) -- again, this is to support pickle
        if EnumEx is not None:
            # if the user defined their own __new__, save it before it gets
            # clobbered in case they subclass later
            if save_new:
                enum_class.__new_member__ = __new__
            enum_class.__new__ = EnumEx.__new__
        #
        # py3 support for definition order (helps keep py2/py3 code in sync)
        #
        # _order_ checking is spread out into three/four steps
        # - if enum_class is a Flag:
        #   - remove any non-single-bit flags from _order_
        # - remove any aliases from _order_
        # - check that _order_ and _member_names_ match
        #
        # step 1: ensure we have a list
        if _order_ is not None:
            if isinstance(_order_, str):
                _order_ = _order_.replace(',', ' ').split()
        #
        # remove Flag structures if final class is not a Flag
        if (
                FlagEx is None and cls != 'Flag'
                or FlagEx is not None and not issubclass(enum_class, FlagEx)
            ):
            delattr(enum_class, '_boundary_')
            delattr(enum_class, '_flag_mask_')
            delattr(enum_class, '_singles_mask_')
            delattr(enum_class, '_all_bits_')
            delattr(enum_class, '_inverted_')
        elif FlagEx is not None and issubclass(enum_class, FlagEx):
            # set correct __iter__
            member_list = [m._value_ for m in enum_class]
            if member_list != sorted(member_list):
                enum_class._iter_member_ = enum_class._iter_member_by_def_
            if _order_:
                # _order_ step 2: remove any items from _order_ that are not single-bit
                _order_ = [
                        o
                        for o in _order_
                        if o not in enum_class._member_map_ or _is_single_bit(enum_class[o]._value_)
                        ]
        #
        if _order_:
            # _order_ step 3: remove aliases from _order_
            _order_ = [
                    o
                    for o in _order_
                    if (
                        o not in enum_class._member_map_
                        or
                        (o in enum_class._member_map_ and o in enum_class._member_names_)
                        )]
            # _order_ step 4: verify that _order_ and _member_names_ match
            if _order_ != enum_class._member_names_:
                raise TypeError(
                        'member order does not match _order_:\n  %r\n  %r'
                        % (enum_class._member_names_, _order_)
                        )
            
        if issubclass(enum_class, ABC):
            enum_class.__abstractmethods__ = None
            update_abstractmethods(enum_class)
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

    @classmethod
    def _get_mixins_(mcls, class_name, bases):
        """
        Returns the type for creating enum members, and the first inherited
        enum class.

        bases: the tuple of bases that was given to __new__
        """
        if not bases or (len(bases) == 1 and bases[0] is Enum):
            return object, EnumEx, Enum

        # ensure final parent class is an EnumEx derivative, find any concrete
        # data type, and check that EnumEx has no members
        # If the last base is a std enum, skip it to find the first EnumEx base.
        first_enumex = bases[-1] if len(bases) == 1 or not _is_std_enum_type(bases[-1]) else bases[-2]
        if not isinstance(first_enumex, EnumExType):            
            raise TypeError("new enumerations should be created as "
                    "`EnumName([mixin_type, ...] [data_type,] enum_type)`")
        member_type = mcls._find_data_type_(class_name, bases) or object
        std_base = mcls._find_std_type_(class_name, bases)
        return member_type, first_enumex, std_base
    
    @classmethod
    def _find_std_type_(mcls, class_name, bases):
        for chain in bases:
            for base in chain.__mro__:
                if _is_std_enum_type(base):
                    return base
        raise TypeError("EnumEx missing a std Enum base.")
 
    @classmethod
    def _find_data_type_(mcls, class_name, bases):
        # a datatype has a __new__ method
        data_types = set()
        base_chain = set()
        for chain in bases:
            candidate = None
            for base in chain.__mro__:
                base_chain.add(base)
                if base is object:
                    continue
                # Skip standard Enum types, they are simply for instance checks.
                elif _is_std_enum_type(base):
                    continue
                elif isinstance(base, EnumExType):
                    if base._member_type_ is not object:
                        data_types.add(base._member_type_)
                        break
                elif '__new__' in base.__dict__ or '__dataclass_fields__' in base.__dict__:
                    if isinstance(base, EnumExType):
                        continue
                    data_types.add(candidate or base)
                    break
                else:
                    candidate = candidate or base
        if len(data_types) > 1:
            raise TypeError('too many data types for %r: %r' % (class_name, data_types))
        elif data_types:
            return data_types.pop()
        else:
            return None

    @classmethod
    def _find_new_(mcls, classdict, member_type, first_enum):
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
        save_new = first_enum is not None and __new__ is not None

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
        if first_enum is None or __new__ in (EnumEx.__new__, object.__new__):
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
        return super().__new__(cls, value)
    
class ReprEnumEx(ReprEnum, EnumEx):
    """
    Only changes the repr(), leaving str() and format() to the mixed-in type.
    """

class IntEnumEx(IntEnum, ReprEnumEx):
    """
    Enum where members are also (and must be) ints
    """

class FlagEx(Flag, EnumEx, boundary=STRICT):
    """
    Support for flags
    """
    def _get_value(self, flag):
        if (isinstance(flag, self.__class__) 
            # If right(flag) is a base of left, return its value to stop it from creating a base instance.
            or (isinstance(flag, FlagEx) and isinstance(self, flag.__class__))
            # If left(self) is IntFlag, and right is abstract int based enum, get value to avoid "Can't instantiate abstract..." error
            # TODO: Check if self is IntFlag instead? Currently int to support custom int based Flag types
            or (isinstance(self, int) and isinstance(flag, int) and _is_abstract_enum(flag.__class__))):
            return flag._value_
        elif self._member_type_ is not object and isinstance(flag, self._member_type_):
            return flag
        return NotImplemented
    
class IntFlagEx(IntFlag, ReprEnumEx, FlagEx, boundary=KEEP):
    """
    Support for integer-based Flags
    """

class StrEnumEx(StrEnum, ReprEnumEx):
    """
    Enum where members are also (and must be) strings
    """

# _stdlib_enumexs = IntEnumEx, StrEnumEx, IntFlagEx

def _enforce_abstract(cls):
    """
    Raises a TypeError if an attempt to instantiate an unimplemented abstract enum is made.

    The EnumTypeEx metaclass does not create instances with __init__(), so we have to check for unimplemented abstract methods manually.
    """

    if _is_abstract_enum(cls):
        methods = cls.__abstractmethods__
        raise TypeError(f"Can't instantiate abstract class {cls.__name__} with abstract method{'' if len(methods) == 1 else 's'}", *methods)
