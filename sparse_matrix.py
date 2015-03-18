from sparse_vector import *

class sparse_matrix:

	def __init__(self, size, initial = None):

		self.size = size

		if size == 1:
			self.value = 0
		else:
			self.half = 2**((size-1).bit_length()-1)
			self.northwest = None
			self.northeast = None
			self.southwest = None
			self.southeast = None

		if initial:
			for (index, value) in initial:
				self[index] = value

	def copy(self):

		copy = sparse_matrix(self.size)

		if self.size == 1:
			copy.value = self.value
			return copy

		if self.northwest:
			copy.northwest = self.northwest.copy()
		if self.northeast:
			copy.northeast = self.northeast.copy()
		if self.southwest:
			copy.southwest = self.southwest.copy()
		if self.southeast:
			copy.southeast = self.southeast.copy()

		return copy

	def __getitem__(self, index):

		return self._get(index[0], index[1])
		
	def _get(self, row, col):

		if self.size == 1:
			return self.value

		if row < self.half:
			if col < self.half:
				if not self.northwest:
					return 0
				return self.northwest._get(row, col)
			else:
				if not self.northeast:
					return 0
				return self.northeast._get(row, col - self.half)
		else:
			if col < self.half:
				if not self.southwest:
					return 0
				return self.southwest._get(row - self.half, col)
			else:
				if not self.southeast:
					return 0
				return self.southeast._get(row - self.half, col - self.half)

	def __setitem__(self, index, value):

		self._set(index[0], index[1], value)

	def _set(self, row, col, value):

		if self.size == 1:
			self.value = value
			return

		if row < self.half:
			if col < self.half:
				if not self.northwest:
					self.northwest = sparse_matrix(self.half)
				self.northwest._set(row, col, value)
			else:
				if not self.northeast:
					self.northeast = sparse_matrix(self.half)
				self.northeast._set(row, col - self.half, value)
		else:
			if col < self.half:
				if not self.southwest:
					self.southwest = sparse_matrix(self.half)
				self.southwest._set(row - self.half, col, value)
			else:
				if not self.southeast:
					self.southeast = sparse_matrix(self.half)
				self.southeast._set(row - self.half, col - self.half, value)

	def __repr__(self):

		return "\n".join([repr(value) for value in self])

	def __iter__(self):

		yield from self._iter()

	def _iter(self, row_index = 0, col_index = 0):

		if self.size == 1:
			yield ((row_index, col_index), self.value)
			return

		if self.northwest:
			yield from self.northwest._iter(row_index, col_index)
		if self.northeast:
			yield from self.northeast._iter(row_index, col_index + self.half)
		if self.southwest:
			yield from self.southwest._iter(row_index + self.half, col_index)
		if self.southeast:
			yield from self.southeast._iter(row_index + self.half, col_index + self.half)

	def row(self, row):

		return sparse_vector(self.size, self._row(row))

	def _row(self, row, col_index = 0):

		if self.size == 1:
			yield (col_index, self.value)
			return

		if row < self.half:
			if self.northwest:
				yield from self.northwest._row(row, col_index)
			if self.northeast:
				yield from self.northeast._row(row, col_index + self.half)
		else:
			if self.southwest:
				yield from self.southwest._row(row - self.half, col_index)
			if self.southeast:
				yield from self.southeast._row(row - self.half, col_index + self.half)

	def col(self, column):

		return sparse_vector(self.size, self._col(column))

	def _col(self, col, row_index = 0):

		if self.size == 1:
			yield (row_index, self.value)
			return

		if col < self.half:
			if self.northwest:
				yield from self.northwest._col(col, row_index)
			if self.southwest:
				yield from self.southwest._col(col, row_index + self.half)
		else:
			if self.northeast:
				yield from self.northeast._col(col - self.half, row_index)
			if self.southeast:
				yield from self.southeast._col(col - self.half, row_index + self.half)

	def __iadd__(self, other):

		return self._add(other)

	def __add__(self, other):

		return self.copy()._add(other)

	def _add(self, other):

		if self.size == 1:
			self.value += other.value
			return self

		if other.northwest:
			if not self.northwest:
				self.northwest = sparse_matrix(self.half)
			self.northwest += other.northwest
		if other.northeast:
			if not self.northeast:
				self.northeast = sparse_matrix(self.half)
			self.northeast += other.northeast
		if other.southwest:
			if not self.southwest:
				self.southwest = sparse_matrix(self.half)
			self.southwest += other.southwest
		if other.southeast:
			if not self.southeast:
				self.southeast = sparse_matrix(self.half)
			self.southeast += other.southeast

		return self

	def __isub__(self, other):

		return self._sub(other)

	def __sub__(self, other):

		return self.copy()._sub(other)

	def _sub(self, other):

		if self.size == 1:
			self.value -= other.value
			return self

		if other.northwest:
			if not self.northwest:
				self.northwest = sparse_matrix(self.half)
			self.northwest -= other.northwest
		if other.northeast:
			if not self.northeast:
				self.northeast = sparse_matrix(self.half)
			self.northeast -= other.northeast
		if other.southwest:
			if not self.southwest:
				self.southwest = sparse_matrix(self.half)
			self.southwest -= other.southwest
		if other.southeast:
			if not self.southeast:
				self.southeast = sparse_matrix(self.half)
			self.southeast -= other.southeast

		return self

	def __imul__(self, other):

		if isinstance(other, sparse_matrix):
			return self._mul_matrix(other)
		else:
			return self._mul_scalar(other)

	def __mul__(self, other):

		if isinstance(other, sparse_matrix):
			return self.copy()._mul_matrix(other)
		else:
			return self.copy()._mul_scalar(other)

	def _mul_scalar(self, other):

		if self.size == 1:
			self.value *= other
			return self

		if self.northwest:
			self.northwest *= other
		if self.northeast:
			self.northeast *= other
		if self.southwest:
			self.southwest *= other
		if self.southeast:
			self.southeast *= other

		return self

	def _mul_matrix(self, other):

		if self.size == 1:
			self.value *= other.value
			return self

		result = sparse_matrix(self.size)

		if (self.northwest and other.northwest) or (self.northeast and other.southwest):
			result.northwest = sparse_matrix(self.half)
			if self.northwest and other.northwest:
				result.northwest += self.northwest * other.northwest
			if self.northeast and other.southwest:
				result.northwest += self.northeast * other.southwest
		if (self.northwest and other.northeast) or (self.northeast and other.southeast):
			result.northeast = sparse_matrix(self.half)
			if self.northwest and other.northeast:
				result.northeast += self.northwest * other.northeast
			if self.northeast and other.southeast:
				result.northeast += self.northeast * other.southeast
		if (self.southwest and other.northwest) or (self.southeast and other.southwest):
			result.southwest = sparse_matrix(self.half)
			if self.southwest and other.northwest:
				result.southwest += self.southwest * other.northwest
			if self.southeast and other.southwest:
				result.southwest += self.southeast * other.southwest
		if (self.southwest and other.northeast) or (self.southeast and other.southeast):
			result.southeast = sparse_matrix(self.half)
			if self.southwest and other.northeast:
				result.southeast += self.southwest * other.northeast
			if self.southeast and other.southeast:
				result.southeast += self.southeast * other.southeast

		self = result

		return self