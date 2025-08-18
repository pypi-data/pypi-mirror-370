cdef class DiscreteDistribution(dict):

    cdef float __sum

    cpdef addItem(self, str item)
    cpdef removeItem(self, str item)
    cpdef addDistribution(self, DiscreteDistribution distribution)
    cpdef removeDistribution(self, DiscreteDistribution distribution)
    cpdef float getSum(self)
    cpdef int getIndex(self, str item)
    cpdef bint containsItem(self, str item)
    cpdef str getItem(self, int index)
    cpdef int getValue(self, int index)
    cpdef int getCount(self, str item)
    cpdef str getMaxItem(self)
    cpdef str getMaxItemIncludeTheseOnly(self, list includeTheseOnly)
    cpdef float getProbability(self, str item)
    cpdef dict getProbabilityDistribution(self)
    cpdef float getProbabilityLaplaceSmoothing(self, str item)
    cpdef float entropy(self)
