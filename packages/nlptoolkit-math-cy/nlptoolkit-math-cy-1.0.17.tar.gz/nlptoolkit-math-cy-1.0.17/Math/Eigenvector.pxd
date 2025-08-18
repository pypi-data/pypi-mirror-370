from Math.Vector cimport Vector


cdef class Eigenvector(Vector):

    cdef float eigenvalue

    cpdef float getEigenvalue(self)
