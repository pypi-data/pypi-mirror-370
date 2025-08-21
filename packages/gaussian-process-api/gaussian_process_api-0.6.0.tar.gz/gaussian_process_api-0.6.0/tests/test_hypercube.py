#!/usr/env/bin python3
'''Test the hypercube functionality'''

######## Imports ########
import numpy as np
from gp_api.utils import sample_hypercube

######## Functions ########

def test_shape(dim, shape):
    if len(shape) == 1:
        res = shape[0]
        shape = np.asarray(res)*np.ones(dim,dtype=int)
        assert isinstance(res, int)
    else:
        res = np.asarray(shape, dtype=int)
        shape = np.asarray(shape, dtype=int)
        assert(dim == res.size) 
    limits = np.zeros((dim, 2))
    limits[:,1] = 1.
    nsample = np.prod(shape)
    assert sample_hypercube(limits, res).shape == (nsample, dim)

######## Main ########

def main():
    test_shape(1, [10])
    test_shape(2, [10])
    test_shape(2, [2,4])
    return

######## Execution ########

if __name__ == "__main__":
    main()
