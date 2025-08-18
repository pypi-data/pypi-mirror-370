import math


cdef class DiscreteDistribution(dict):

    def __init__(self, **kwargs):
        """
        A constructor of DiscreteDistribution class which calls its super class.
        """
        super().__init__(**kwargs)
        self.__sum = 0.0

    cpdef addItem(self, str item):
        """
        The addItem method takes a String item as an input and if this map contains a mapping for the item it puts the
        item with given value + 1, else it puts item with value of 1.

        PARAMETERS
        ----------
        item : string
            String input.
        """
        if item in self:
            self[item] = self[item] + 1
        else:
            self[item] = 1
        self.__sum = self.__sum + 1

    cpdef removeItem(self, str item):
        """
        The removeItem method takes a String item as an input and if this map contains a mapping for the item it puts
        the item with given value - 1, and if its value is 0, it removes the item.

        PARAMETERS
        ----------
        item : string
            String input.
        """
        if item in self:
            self[item] = self[item] - 1
            if self[item] == 0:
                self.pop(item)
            self.__sum = self.__sum - 1

    cpdef addDistribution(self, DiscreteDistribution distribution):
        """
        The addDistribution method takes a DiscreteDistribution as an input and loops through the entries in this
        distribution and if this map contains a mapping for the entry it puts the entry with its value + entry,
        else it puts entry with its value. It also accumulates the values of entries and assigns to the sum variable.

        PARAMETERS
        ----------
        distribution : DiscreteDistribution
            DiscreteDistribution type input.
        """
        for entry in distribution:
            if entry in self:
                self[entry] = self[entry] + distribution[entry]
            else:
                self[entry] = distribution[entry]
            self.__sum += distribution[entry]

    cpdef removeDistribution(self, DiscreteDistribution distribution):
        """
        The removeDistribution method takes a DiscreteDistribution as an input and loops through the entries in this
        distribution and if this map contains a mapping for the entry it puts the entry with its key - value, else it
        removes the entry. It also decrements the value of entry from sum and assigns to the sum variable.

        PARAMETERS
        ----------
        distribution : DiscreteDistribution
            DiscreteDistribution type input.
        """
        for entry in distribution:
            if self[entry] - distribution[entry] != 0:
                self[entry] -= distribution[entry]
            else:
                self.pop(entry)
            self.__sum -= distribution[entry]

    cpdef float getSum(self):
        """
        The getter for sum variable.

        RETURNS
        -------
        float
            sum
        """
        return self.__sum

    cpdef int getIndex(self, str item):
        """
        The getIndex method takes an item as an input and returns the index of given item.

        PARAMETERS
        ----------
        item : string
            item to search for index.

        RETURNS
        -------
        int
            index of given item.
        """
        return list(self.keys()).index(item)

    cpdef bint containsItem(self, str item):
        """
        The containsItem method takes an item as an input and returns true if this map contains a mapping for the
        given item.

        PARAMETERS
        ----------
        item : string
            item to check.

        RETURNS
        -------
        boolean
            true if this map contains a mapping for the given item.
        """
        return item in self

    cpdef str getItem(self, int index):
        """
        The getItem method takes an index as an input and returns the item at given index.

        PARAMETERS
        ----------
        index : int
            index is used for searching the item.

        RETURNS
        -------
        string
            the item at given index.
        """
        return list(self.keys())[index]

    cpdef int getValue(self, int index):
        """
        The getValue method takes an index as an input and returns the value at given index.

        PARAMETERS
        ----------
        index : int
            index is used for searching the value.

        RETURNS
        -------
        int
            the value at given index.
        """
        return list(self.values())[index]

    cpdef int getCount(self, str item):
        """
        The getCount method takes an item as an input returns the value to which the specified item is mapped, or ""
        if this map contains no mapping for the key.

        PARAMETERS
        ----------
        item : string

        RETURNS
        -------
        int
            the value to which the specified item is mapped
        """
        return self[item]

    cpdef str getMaxItem(self):
        """
        The getMaxItem method loops through the entries and gets the entry with maximum value.

        RETURNS
        -------
        string
            the entry with maximum value.
        """
        cdef int maxValue
        cdef str maxItem
        maxValue = -1
        maxItem = ""
        for item in self:
            if self[item] > maxValue:
                maxValue = self[item]
                maxItem = item
        return maxItem

    cpdef str getMaxItemIncludeTheseOnly(self, list includeTheseOnly):
        """
        Another getMaxItem method which takes a list of Strings. It loops through the items in this list
        and gets the item with maximum value.

        PARAMETERS
        ----------
        includeTheseOnly : list
            list of Strings.

        RETURNS
        -------
        string
            the item with maximum value.
        """
        cdef int maxValue, frequency
        cdef str maxItem
        maxValue = -1
        maxItem = ""
        for item in includeTheseOnly:
            frequency = 0
            if item in self:
                frequency = self[item]
            if frequency > maxValue:
                maxValue = frequency
                maxItem = item
        return maxItem

    cpdef float getProbability(self, str item):
        """
        The getProbability method takes an item as an input returns the value to which the specified item is mapped over
        sum, or 0.0 if this map contains no mapping for the key.

        PARAMETERS
        ----------
        item : string
            is used to search for probability.

        RETURNS
        -------
        float
            the probability to which the specified item is mapped.
        """
        if item in self:
            return self[item] / self.__sum
        else:
            return 0.0

    cpdef dict getProbabilityDistribution(self):
        """
        Returns the distribution as a probability distribution
        :return: Probability distribution
        """
        result = {}
        for item in self:
            result[item] = self.getProbability(item)
        return result

    cpdef float getProbabilityLaplaceSmoothing(self, str item):
        """
        The getProbabilityLaplaceSmoothing method takes an item as an input returns the smoothed value to which the
        specified item is mapped over sum, or 1.0 over sum if this map contains no mapping for the key.
        PARAMETERS
        ----------
        item : string
            is used to search for probability.

        RETURNS
        -------
        float
            the smoothed probability to which the specified item is mapped.
        """
        if item in self:
            return (self[item] + 1) / (self.__sum + len(self) + 1)
        else:
            return 1.0 / (self.__sum + len(self) + 1)

    cpdef float entropy(self):
        """
        The entropy method loops through the values and calculates the entropy of these values.

        RETURNS
        -------
        float
            entropy value.
        """
        cdef float total, probability
        cdef int count
        total = 0.0
        for count in self.values():
            probability = count / self.__sum
            total += -probability * math.log2(probability)
        return total
