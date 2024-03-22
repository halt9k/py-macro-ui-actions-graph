from functools import wraps

from typing_extensions import override as typing_extensions_override


def virutalmethod(method):
	""" Decorator to hint that optional override is possible """

	method.__isvirtualmethod__ = True
	return method


def check_method(method, self):
	base_class = self.__class__
	base_method = getattr(base_class, method.__name__)

	is_abstract = getattr(base_method, '__isabstractmeathod__', False)
	is_virtual = getattr(base_method, '__isvirtualmethod__', False)
	is_override = getattr(base_method, '__override__', False)

	if not (is_abstract or is_virtual or is_override):
		module = base_method.__module__
		qualname = base_method.__qualname__
		print(f"WARNING: {module}.{qualname} has no inheritance decorator")


# TODO implement instead @inheritance_decorators_strict_mode
def override(method):
	"""
	Optional, just verifies inheritance decorators.
	Not an optimal way to check and will be replaced later.
	"""

	@wraps(method)
	@typing_extensions_override
	def method_with_override(self, *args, **kwargs):
		if not hasattr(method, "__override_check_done__"):
			check_method(method, self)
			method.__override_check_done__ = True
		return method(self, *args, **kwargs)

	return method_with_override
