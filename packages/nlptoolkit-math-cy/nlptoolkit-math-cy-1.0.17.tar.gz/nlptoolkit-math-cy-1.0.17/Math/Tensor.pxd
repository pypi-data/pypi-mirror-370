cdef class Tensor:
    cdef double[:] _data
    cdef tuple _shape
    cdef tuple _strides

    cpdef float get(self, tuple indices)
    cpdef void set(self, tuple indices, float value)
    cpdef Tensor broadcast_to(self, tuple target_shape)
    cpdef Tensor add(self, Tensor other)
    cpdef Tensor subtract(self, Tensor other)
    cpdef Tensor hadamardProduct(self, Tensor other)
    cpdef Tensor multiply(self, Tensor other)
    cpdef Tensor partial(self, tuple start_indices, tuple end_indices)
    cpdef Tensor transpose(self, tuple axes=?)
    cpdef Tensor reshape(self, tuple new_shape)

    cdef list _flatten(self, object data)
    cdef tuple _infer_shape(self, object data)
    cdef int _compute_num_elements(self, tuple shape)
    cdef tuple _compute_strides(self, tuple shape)
    cdef tuple _unflatten_index(self, int flat_index, tuple strides)
    cdef tuple _broadcast_shape(self, tuple shape1, tuple shape2)
    cdef void _validate_indices(self, tuple indices)
    cdef list _transpose_flattened_data(self, tuple axes, tuple new_shape)
