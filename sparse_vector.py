class sparse_vector:

	def __init__(self, size, initial = None):

		assert size > 0

		self.size = size

		if size == 1:
			self.value = 0
		else:
			self.half = 2**((size-1).bit_length()-1)
			self.north = None
			self.south = None

		if initial:
			for (index, value) in initial:
				self[index] = value

	def copy(self):

		copy = sparse_vector(self.size)

		if self.size == 1:
			copy.value = self.value
			return copy

		if self.north:
			copy.north = self.north.copy()
		if self.south:
			copy.south = self.south.copy()

		return copy

	def __getitem__(self, index):

		assert index < self.size

		if self.size == 1:
			return self.value

		if index < self.half:
			if not self.north: return 0
			return self.north[index]
		else:
			if not self.south: return 0
			return self.south[index - self.half]

	def __setitem__(self, index, value):

		assert index < self.size

		if self.size == 1:
			self.value = value
			return

		if index < self.half:
			if not self.north: self.north = sparse_vector(self.half)
			self.north[index] = value
		else:
			if not self.south: self.south = sparse_vector(self.half)
			self.south[index - self.half] = value

	def __repr__(self):

		return "\n".join([repr(value) for value in self.values()])

	def values(self):

		yield from self._values(0)

	def _values(self, index):

		if self.size == 1:
			yield (index, self.value)
			return

		if self.north:
			yield from self.north._values(index)
		if self.south:
			yield from self.south._values(index + self.half)

	def __iadd__(self, other):

		assert self.size == other.size

		return self._add(other)

	def __add__(self, other):

		assert self.size == other.size

		return self.copy()._add(other)

	def _add(self, other):

		if self.size == 1:
			self.value += other.value
			return self

		if other.north:
			if not self.north:
				self.north = other.north.copy()
			else:
				self.north += other.north
		if other.south:
			if not self.south:
				self.south = other.south.copy()
			else:
				self.south += other.south

		return self

	def __isub__(self, other):

		assert self.size == other.size

		return self._sub(other)

	def __sub__(self, other):

		assert self.size == other.size

		return self.copy()._sub(other)

	def _sub(self, other):

		if self.size == 1:
			self.value -= other.value
			return self

		if other.north:
			if not self.north:
				self.north = other.north.copy()._mul(-1)
			else:
				self.north -= other.north
		if other.south:
			if not self.south:
				self.south = other.south.copy()._mul(-1)
			else:
				self.south -= other.south

		return self

	def __imul__(self, other):

		return self._mul(other)

	def __mul__(self, other):

		return self.copy()._mul(other)

	def _mul(self, other):

		if self.size == 1:
			self.value *= other
			return self

		if self.north:
			self.north._mul(other)
		if self.south:
			self.south._mul(other)

		return self

	def dot(self, other):

		if not other:
			return 0

		assert self.size == other.size

		if self.size == 1:
			return self.value*other.value.conjugate()

		if self.north and other.north:
			dot_north = self.north.dot(other.north)
		else:
			dot_north = 0
		if self.south and other.south:
			dot_south = self.south.dot(other.south)
		else:
			dot_south = 0

		return dot_north + dot_south