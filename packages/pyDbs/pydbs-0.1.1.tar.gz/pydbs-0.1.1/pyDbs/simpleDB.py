from pyDbs.gpy import *
from pyDbs.base import _numtypes

class SimpleDB:
	def __init__(self, name = None, symbols = None, alias = None):
		self.name = name
		self.symbols = noneInit(symbols, {})
		self.updateAlias(alias = alias)

	def updateAlias(self,alias=None):
		self.alias = self.alias.union(pd.MultiIndex.from_tuples(noneInit(alias,[]), names = ['from','to'])) if hasattr(self,'alias') else pd.MultiIndex.from_tuples(noneInit(alias,[]), names = ['from','to'])

	def __iter__(self):
		return iter(self.symbols.values())

	def __len__(self):
		return len(self.symbols)

	def __delitem__(self,item):
		del(self.symbols[item])

	def copy(self):
		obj = type(self).__new__(self.__class__,None)
		obj.__dict__.update(deepcopy(self.__dict__).items())
		return obj

	def getTypes(self,types=['variable']):
		return {k:v for k,v in self.symbols.items() if v.type in types}

	def getDomains(self, setName, types = ['variable']):
		return {k:v for k,v in self.getTypes(types).items() if setName in v.domains}

	@property
	def aliasDict(self):
		return {k: self.alias.get_level_values(1)[self.alias.get_level_values(0) == k] for k in self.alias.get_level_values(0).unique()}

	@property
	def aliasDict0(self):
		return {key: self.aliasDict[key].insert(0,key) for key in self.aliasDict}

	def getAlias(self,x,index_=0):
		if x in self.alias.get_level_values(0):
			return self.aliasDict0[x][index_]
		elif x in self.alias.get_level_values(1):
			return self.aliasDict0[self.alias.get_level_values(0)[self.alias.get_level_values(1)==x][0]][index_]
		elif x in self.getTypes(['set']) and index_==0:
			return x
		else:
			raise TypeError(f"{x} is not aliased")

	def __getitem__(self,item):
		try:
			return self.symbols[item]
		except KeyError:
			try:
				return self.symbols[self.getAlias(item)].rename(item)
			except TypeError:
				raise TypeError(f"Symbol {item} not in database")

	def __setitem__(self,item,value):
		self.symbols[item] = value

	def __call__(self, var, attr = 'v'):
		return getattr(self[var], attr)

	def get(self, var, attr = 'v'):
		""" Return attribute from Gpy symbol"""
		return getattr(self[var], attr)

	def set(self, var, value, attr = 'v', **kwargs):
		try:
			setattr(getattr(self[var], attr), value)
		except KeyError:
			self[var] = Gpy.c(value, **kwargs)

	def aom(self, name, symbol, **kwargs):
		if name in self.symbols:
			self[name].merge(symbol, **kwargs)
		else:
			self[name] = Gpy.c(symbol, **kwargs)

	def aomGpy(self, name, symbol, **kwargs):
		if name in self.symbols:
			self[name].mergeGpy(symbol, **kwargs)
		else:
			self[name] = symbol

	def mergeDbs(self, dbOther, **kwargs):
		[self.aomGpy(name, symbol, **kwargs) for name, symbol in dbOther.symbols.items()];

	def readSets(self, types = None):
		""" Read sets from database symbols """
		[self.aom(set_, symbol.index.get_level_values(set_).unique()) for symbol in self.getTypes(noneInit(types,['variable'])).values() for set_ in symbol.domains];
