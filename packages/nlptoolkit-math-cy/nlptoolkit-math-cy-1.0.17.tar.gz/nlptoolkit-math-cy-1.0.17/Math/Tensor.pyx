# cython: boundscheck=False, wraparound=False
import array

cdef class Tensor:
    def __init__(self, data, shape=None):
        """
        Initializes a Tensor from nested list data with an optional shape.

        Parameters
        ----------
        data : nested list
            The input data for the tensor.
        shape : tuple, optional
            The shape to be used for the tensor. If None, it is inferred from data.
        """
        if shape is None:
            shape = self._infer_shape(data)

        flat_data = self._flatten(data)
        total_elements = self._compute_num_elements(shape)

        if total_elements != len(flat_data):
            raise ValueError("Shape does not match the number of elements in data.")

        self._shape = shape
        self._strides = self._compute_strides(shape)
        data_array = array.array('d', flat_data)
        self._data = data_array

    @property
    def shape(self):
        """Returns the shape of the tensor."""
        return self._shape

    @property
    def strides(self):
        """Returns the strides used in indexing."""
        return self._strides

    @property
    def data(self):
        """Returns the raw flat data."""
        return self._data

    cdef tuple _infer_shape(self, object data):
        """
        Recursively infers the shape of nested list data.

        Parameters
        ----------
        data : list
            A potentially nested list representing tensor data.

        Returns
        -------
        tuple
            Inferred shape of the tensor.
        """
        if isinstance(data, list):
            if len(data) == 0:
                return (0,)
            return (len(data),) + self._infer_shape(data[0])
        return ()

    cdef list _flatten(self, object data):
        """
        Recursively flattens nested list data.

        Parameters
        ----------
        data : list
            A potentially nested list of tensor data.

        Returns
        -------
        list
            A flattened list of float values.
        """
        if isinstance(data, list):
            result = []
            for sub in data:
                result.extend(self._flatten(sub))
            return result
        return [data]

    cdef tuple _compute_strides(self, tuple shape):
        """
        Computes strides needed for indexing.

        Parameters
        ----------
        shape : tuple
            Tensor shape.

        Returns
        -------
        tuple
            Strides corresponding to each dimension.
        """
        cdef list strides = []
        cdef int product = 1
        for dim in reversed(shape):
            strides.append(product)
            product *= dim
        return tuple(reversed(strides))

    cdef int _compute_num_elements(self, tuple shape):
        """
        Computes total number of elements from the shape.

        Parameters
        ----------
        shape : tuple
            Tensor shape.

        Returns
        -------
        int
            Number of elements.
        """
        cdef int product = 1
        for dim in shape:
            product *= dim
        return product

    cdef void _validate_indices(self, tuple indices):
        """
        Validates that indices are within the valid range for each dimension.

        Parameters
        ----------
        indices : tuple
            Index tuple to validate.

        Raises
        ------
        IndexError
            If any index is out of bounds.
        """
        cdef int i
        if len(indices) != len(self._shape):
            raise IndexError(f"Expected {len(self._shape)} indices but got {len(indices)}.")
        for i in range(len(indices)):
            if indices[i] < 0 or indices[i] >= self._shape[i]:
                raise IndexError(f"Index {indices} is out of bounds for shape {self._shape}.")

    cpdef float get(self, tuple indices):
        """
        Retrieve an element by its multi-dimensional index.

        Parameters
        ----------
        indices : tuple
            Multi-dimensional index for accessing the tensor value.

        Returns
        -------
        float
            The value at the specified index.
        """
        self._validate_indices(indices)

        cdef Py_ssize_t flat_index = 0
        cdef int i
        for i in range(len(indices)):
            flat_index += indices[i] * self._strides[i]
        return self._data[flat_index]

    cpdef void set(self, tuple indices, float value):
        """
        Set a value at a specific index in the tensor.

        Parameters
        ----------
        indices : tuple
            Multi-dimensional index for accessing the tensor.
        value : float
            The value to be assigned at the specified index.
        """
        self._validate_indices(indices)

        cdef Py_ssize_t flat_index = 0
        cdef int i
        for i in range(len(indices)):
            flat_index += indices[i] * self._strides[i]
        self._data[flat_index] = value

    cpdef Tensor reshape(self, tuple new_shape):
        """
        Reshapes the tensor into a new shape without changing the data.

        Parameters
        ----------
        new_shape : tuple
            New desired shape.

        Returns
        -------
        Tensor
            Tensor with new shape.

        Raises
        ------
        ValueError
            If total number of elements mismatches.
        """
        if self._compute_num_elements(new_shape) != self._compute_num_elements(self._shape):
            raise ValueError("Total number of elements must remain the same.")
        # Convert self._data to a flat list before passing to Tensor
        return Tensor(list(self._data), new_shape)

    cpdef Tensor transpose(self, tuple axes=None):
        """
        Transposes the tensor according to the given axes.

        Parameters
        ----------
        axes : tuple, optional
            The order of axes. If None, the axes are reversed.

        Returns
        -------
        Tensor
            A new tensor with transposed data.
        """
        cdef int ndim = len(self._shape)

        if axes is None:
            axes = tuple(range(ndim - 1, -1, -1))
        else:
            if sorted(axes) != list(range(ndim)):
                raise ValueError("Invalid transpose axes.")

        cdef list shape_list = []
        cdef int axis
        for axis in axes:
            shape_list.append(self._shape[axis])
        cdef tuple new_shape = tuple(shape_list)

        cdef list flattened_data = self._transpose_flattened_data(axes, new_shape)

        return Tensor(flattened_data, new_shape)

    cdef list _transpose_flattened_data(self, tuple axes, tuple new_shape):
        """
        Rearranges the flattened data for transposition.

        Parameters
        ----------
        axes : tuple
            Tuple representing the order of axes.
        new_shape : tuple
            Tuple representing the new shape.

        Returns
        -------
        list
            Flattened list of transposed data.
        """
        cdef tuple new_strides = self._compute_strides(new_shape)
        cdef list flattened_data = []
        cdef int i, dim
        cdef tuple new_indices
        cdef list original_indices

        for i in range(self._compute_num_elements(new_shape)):
            new_indices = self._unflatten_index(i, new_strides)
            original_indices = [new_indices[axes.index(dim)] for dim in range(len(self._shape))]
            flattened_data.append(self.get(tuple(original_indices)))

        return flattened_data

    cdef tuple _unflatten_index(self, int flat_index, tuple strides):
        """
        Converts flat index to multi-dimensional index using strides.

        Parameters
        ----------
        flat_index : int
            Flat index into the tensor.
        strides : tuple
            Strides for each dimension.

        Returns
        -------
        tuple
            Multi-dimensional index.
        """
        cdef list indices = []
        for stride in strides:
            indices.append(flat_index // stride)
            flat_index %= stride
        return tuple(indices)

    cdef tuple _broadcast_shape(self, tuple shape1, tuple shape2):
        """
        Calculates broadcasted shape from two input shapes.

        Parameters
        ----------
        shape1 : tuple
            Shape of the first tensor.
        shape2 : tuple
            Shape of the second tensor.

        Returns
        -------
        tuple
            Broadcasted shape.
        """
        cdef list r1 = list(reversed(shape1))
        cdef list r2 = list(reversed(shape2))
        cdef list result = []
        for i in range(min(len(r1), len(r2))):
            d1 = r1[i]
            d2 = r2[i]
            if d1 == d2:
                result.append(d1)
            elif d1 == 1 or d2 == 1:
                result.append(max(d1, d2))
            else:
                raise ValueError(f"Shapes {shape1} and {shape2} not broadcastable")
        result.extend(r1[len(r2):])
        result.extend(r2[len(r1):])
        return tuple(reversed(result))

    cpdef Tensor broadcast_to(self, tuple target_shape):
        """
        Broadcasts the tensor to a new shape.

        Parameters
        ----------
        target_shape : tuple
            Target shape to broadcast the current tensor to.

        Returns
        -------
        Tensor
            New tensor with broadcasted data.

        Raises
        ------
        ValueError
            If broadcasting is not possible.
        """
        cdef int i, j, rank, size
        cdef tuple expanded, targ_strides, strides
        cdef list new_data
        cdef tuple idx
        cdef list orig_idx
        rank = len(target_shape)
        size = self._compute_num_elements(target_shape)
        expanded = (1,) * (rank - len(self._shape)) + self._shape
        for i in range(rank):
            if not (expanded[i] == target_shape[i] or expanded[i] == 1):
                raise ValueError(f"Cannot broadcast shape {self._shape} to {target_shape}")

        targ_strides = self._compute_strides(target_shape)
        strides = self._strides
        new_data = [0.0] * size
        for i in range(size):
            idx = self._unflatten_index(i, targ_strides)
            orig_idx = []
            for j in range(rank):
                if expanded[j] > 1:
                    orig_idx.append(idx[j])
                else:
                    orig_idx.append(0)
            # Only use the last len(self._shape) indices for get()
            get_indices = tuple(orig_idx[-len(self._shape):])
            new_data[i] = self.get(get_indices)

        return Tensor(new_data, target_shape)

    cpdef Tensor multiply(self, Tensor other):
        """
        Performs matrix multiplication (batched if necessary).

        For tensors of shape (..., M, K) and (..., K, N), returns (..., M, N).

        :param other: Tensor with shape compatible for matrix multiplication.
        :return: Tensor resulting from matrix multiplication.
        """
        if self._shape[len(self._shape)-1] != other._shape[len(other._shape)-2]:
            raise ValueError(f"Shapes {self._shape} and {other._shape} are not aligned for multiplication.")

        cdef tuple batch_shape = self._shape[:-2]
        cdef int m = self._shape[len(self._shape)-2]
        cdef int k1 = self._shape[len(self._shape)-1]
        cdef int k2 = other._shape[len(other._shape)-2]
        cdef int n = other._shape[len(other._shape)-1]

        if k1 != k2:
            raise ValueError("Inner dimensions must match for matrix multiplication.")

        # Broadcasting batch shape if necessary
        cdef tuple broadcast_shape
        cdef Tensor self_broadcasted
        cdef Tensor other_broadcasted
        
        if batch_shape != other._shape[:-2]:
            broadcast_shape = self._broadcast_shape(self._shape[:-2], other._shape[:-2])
            self_broadcasted = self.broadcast_to(broadcast_shape + (m, k1))
            other_broadcasted = other.broadcast_to(broadcast_shape + (k2, n))
        else:
            broadcast_shape = batch_shape
            self_broadcasted = self
            other_broadcasted = other

        cdef tuple result_shape = broadcast_shape + (m, n)
        cdef list result_data = []
        cdef int num_elements = self._compute_num_elements(result_shape)
        cdef tuple result_strides = self._compute_strides(result_shape)
        cdef int i, k
        cdef tuple indices, batch_idx
        cdef int row, col
        cdef double sum_result
        cdef tuple a_idx, b_idx

        for i in range(num_elements):
            indices = self._unflatten_index(i, result_strides)
            batch_idx = indices[:-2]
            row = indices[len(indices)-2]
            col = indices[len(indices)-1]

            sum_result = 0.0
            for k in range(k1):
                a_idx = batch_idx + (row, k)
                b_idx = batch_idx + (k, col)
                sum_result += self_broadcasted.get(a_idx) * other_broadcasted.get(b_idx)

            result_data.append(sum_result)

        return Tensor(result_data, result_shape)

    cpdef Tensor add(self, Tensor other):
        """
        Adds two tensors element-wise with broadcasting.

        :param other: The other tensor to add.
        :return: New tensor with the result of the addition.
        """
        cdef tuple broadcast_shape = self._broadcast_shape(self._shape, other._shape)
        cdef Tensor tensor1 = self.broadcast_to(broadcast_shape)
        cdef Tensor tensor2 = other.broadcast_to(broadcast_shape)
        cdef int num_elements = self._compute_num_elements(broadcast_shape)
        cdef list result_data = []
        cdef int i
        cdef tuple indices1, indices2
        
        for i in range(num_elements):
            indices1 = self._unflatten_index(i, tensor1._strides)
            indices2 = self._unflatten_index(i, tensor2._strides)
            result_data.append(tensor1.get(indices1) + tensor2.get(indices2))
        
        return Tensor(result_data, broadcast_shape)

    cpdef Tensor subtract(self, Tensor other):
        """
        Subtracts one tensor from another element-wise with broadcasting.

        :param other: The other tensor to subtract.
        :return: New tensor with the result of the subtraction.
        """
        cdef tuple broadcast_shape = self._broadcast_shape(self._shape, other._shape)
        cdef Tensor tensor1 = self.broadcast_to(broadcast_shape)
        cdef Tensor tensor2 = other.broadcast_to(broadcast_shape)
        cdef int num_elements = self._compute_num_elements(broadcast_shape)
        cdef list result_data = []
        cdef int i
        cdef tuple indices1, indices2
        
        for i in range(num_elements):
            indices1 = self._unflatten_index(i, tensor1._strides)
            indices2 = self._unflatten_index(i, tensor2._strides)
            result_data.append(tensor1.get(indices1) - tensor2.get(indices2))
        
        return Tensor(result_data, broadcast_shape)

    cpdef Tensor hadamardProduct(self, Tensor other):
        """
        Multiplies two tensors element-wise with broadcasting.

        :param other: The other tensor to multiply.
        :return: New tensor with the result of the multiplication.
        """
        cdef tuple broadcast_shape = self._broadcast_shape(self._shape, other._shape)
        cdef Tensor tensor1 = self.broadcast_to(broadcast_shape)
        cdef Tensor tensor2 = other.broadcast_to(broadcast_shape)
        cdef int num_elements = self._compute_num_elements(broadcast_shape)
        cdef list result_data = []
        cdef int i
        cdef tuple indices1, indices2
        
        for i in range(num_elements):
            indices1 = self._unflatten_index(i, tensor1._strides)
            indices2 = self._unflatten_index(i, tensor2._strides)
            result_data.append(tensor1.get(indices1) * tensor2.get(indices2))
        
        return Tensor(result_data, broadcast_shape)

    cpdef Tensor partial(self, tuple start_indices, tuple end_indices):
        """
        Extracts a sub-tensor from the given start indices to the end indices.

        :param start_indices: Tuple specifying the start indices for each dimension.
        :param end_indices: Tuple specifying the end indices (exclusive) for each dimension.
        :return: A new Tensor containing the extracted sub-tensor.
        """
        if len(start_indices) != len(self._shape) or len(end_indices) != len(self._shape):
            raise ValueError("start_indices and end_indices must match the number of dimensions.")

        # Compute the new shape of the extracted sub-tensor
        cdef list new_shape_list = []
        cdef int i
        for i in range(len(start_indices)):
            new_shape_list.append(end_indices[i] - start_indices[i])
        cdef tuple new_shape = tuple(new_shape_list)

        # Extract data from the original tensor
        cdef list sub_data = []
        cdef int num_elements = self._compute_num_elements(new_shape)
        cdef tuple new_strides = self._compute_strides(new_shape)
        cdef tuple sub_indices, original_indices
        cdef list orig_indices_list
        cdef int j

        for i in range(num_elements):
            sub_indices = self._unflatten_index(i, new_strides)
            orig_indices_list = []
            for j in range(len(start_indices)):
                orig_indices_list.append(start_indices[j] + sub_indices[j])
            original_indices = tuple(orig_indices_list)
            sub_data.append(self.get(original_indices))

        return Tensor(sub_data, new_shape)

    def __repr__(self):
        """
        Returns a string representation of the tensor.

        :return: String representing the tensor.
        """
        def format_tensor(data, shape):
            if len(shape) == 1:
                return data
            stride = self._compute_num_elements(shape[1:])
            return [format_tensor(data[i * stride:(i + 1) * stride], shape[1:]) for i in range(shape[0])]

        formatted_data = format_tensor(self._data, self._shape)
        return f"Tensor(shape={self._shape}, data={formatted_data})"

