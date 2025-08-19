from pyDbs.base import *
from pyDbs.base import _numtypes
_adjF = adj.rc_pd

def type_(s):
	if isinstance(s, pd.Index):
		return 'set'
	elif isinstance(s, (pd.DataFrame, pd.Series)):
		return 'variable'
	elif isinstance(s,_numtypes):
		return 'scalar'

class Gpy_:
	def __init__(self, symbol, **kwargs):
		self.initFromSym(symbol, **kwargs)
	def __len__(self):
		return len(self.v)
	@property
	def index(self):
		return self.v.index
	@property
	def domains(self):
		return self.index.names
	def adj(self, rc, **kwargs):
		self.v = _adjF(self.v, rc, **kwargs)
		return self.v

class GpySet(Gpy_):
	def initFromSym(self, symbol, name = None, **kwargs):
		self.v = symbol
		self.name = noneInit(name, self.v.name)
		self.type ='set'
	@property
	def index(self):
		return self.v

	def merge(self, symbol, priority = 'second', union = True, **kwargs):
		if priority == 'replace':
			self.v = symbol
		else:
			self.v = self.v.union(symbol) if union else self.v.intersection(symbol)
		return self.v

	def mergeGpy(self, symbol, priority = 'second', union = True, **kwargs):
		""" Update self.v from Gpy instance of similar subclass type"""
		return self.merge(symbol.v, priority=priority, union = union, **kwargs)

class GpyVariable(Gpy_):
	def initFromSym(self, symbol, name = None, **kwargs):
		if isinstance(symbol, pd.Series):
			self.v = symbol
			self.lo = None
			self.up = None
		elif isinstance(symbol, pd.DataFrame):
			self.v = symbol['v']
			self.lo = symbol['lo'] if 'lo' in symbol.columns else None
			self.up = symbol['up'] if' up' in symbol.columns else None
		else:
			raise TypeError(f"Can only initialize variable with pd.Series or pd.DataFrame")
		self.name = noneInit(name, self.v.name)
		self.type ='variable'

	def adj(self, rc, **kwargs):
		if self.lo is not None:
			self.lo = _adjF(self.lo, rc, **kwargs)
		if self.up is not None:
			self.up = _adjF(self.up, rc, **kwargs)
		return super().adj(rc, **kwargs)

	def mergeGpy(self, symbol, priority = 'second', **kwargs):
		""" Update self.v from Gpy instance of similar subclass type"""
		return self.merge(symbol.v, lo =  symbol.lo, up = symbol.up, priority=priority, **kwargs)

	def merge(self, v, lo = None, up = None, priority = 'second', **kwargs):
		self.mergeV(v, priority=priority, **kwargs)
		if lo:
			self.mergeLo(lo, priority=priority,**kwargs)
		if up:
			self.mergeUp(up, priority=priority,**kwargs)
		return self.v

	def mergeV(self, symbol, attr = 'v', priority='second', **kwargs):
		if priority == 'second':
			setattr(self, attr, getattr(self, attr).combine_first(symbol))
		elif priority == 'first':
			setattr(self, attr, symbol.combine_first(getattr(self, attr)))
		elif priority == 'replace':
			setattr(self, attr, symbol)
		return getattr(self, attr)

	def mergeLo(self, symbol, priority='second', **kwargs):
		if symbol is None:
			pass
		elif self.lo is None:
			self.lo = symbol
		else:
			return self.mergeV(symbol, attr = 'lo', priority=priority, **kwargs)

	def mergeUp(self, symbol, priority='second', **kwargs):
		if symbol is None:
			pass
		elif self.up is None:
			self.up = symbol
		else:
			return self.mergeV(symbol, attr = 'up', priority=priority, **kwargs)

class GpyScalar(Gpy_):
	def initFromSym(self, symbol, lo = None, up = None, name = None, **kwargs):
		self.v = symbol
		self.lo = lo
		self.up = up
		self.name = name
		self.type ='scalarPar'
	@property
	def index(self):
		return None
	@property
	def domains(self):
		return []
	def adj(self, rc, **kwargs):
		return self.v

	def mergeGpy(self, symbol, priority = 'second', **kwargs):
		""" Update self.v from Gpy instance of similar subclass type"""
		return self.merge(symbol.v, priority=priority, **kwargs)

	def merge(self, v, priority = 'second', **kwargs):
		if priority in ('first', 'replace'):
			self.v = symbol
		return self.v



_GpyClasses = {'variable': GpyVariable, 'scalar': GpyScalar, 'set': GpySet}
class Gpy(Gpy_):
	""" Convenience class. """
	@staticmethod
	def c(symbol, *args, **kwargs):
		""" Add symbol and detect what it is from the symbol type."""
		if isinstance(symbol, Gpy_):
			s = symbol.__class__.__new__(symbol.__class__)
			s.__dict__ = deepcopy(symbol.__dict__)
			return s
		else:
			return Gpy.create(type_(symbol), symbol, *args, **kwargs)

	@staticmethod
	def create(version: str, *args, **kwargs):
		cls = _GpyClasses[version]
		return cls(*args, **kwargs)

