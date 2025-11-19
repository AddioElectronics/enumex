# Change Log

The change log contains a mix of functional and notable technical changes to enumex.py, for more info on the base changes you will need to see the Python change log.

## V3.11.0
- Mirroring changes to `enum.py`overrides
- Mirroring new features from `enum.py`
	- Added new `EnumEx` types:
		- `StrEnumEx`
		- `ReprEnumEx`

## V3.10.0
- Using `abc.update_abstractmethods` to populate `__abstractmethods__`

## V3.9.7 
- Mirroring changes to `enum.py`
	- Pickle compatibility safeguard: enums with mixin types that lack proper pickle methods are made explicitly unpicklable to avoid runtime errors.