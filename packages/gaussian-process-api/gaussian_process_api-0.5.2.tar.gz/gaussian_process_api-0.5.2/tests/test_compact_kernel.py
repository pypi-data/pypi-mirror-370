#!/usr/env/bin python3
''' Test kernel functions for gp-api'''

######## Imports ########
import numpy as np
import time

######## Functions ########

def get_training_data(
                      dim=2,
                      train_res=11,
                      sample_res=10,
                     ):
    ''' a small and large grid for kernel evaluation '''
    from gp_api.utils import sample_hypercube
    limits = np.zeros((dim,2))
    limits[:,-1] = 1.
    x_train = sample_hypercube(limits, train_res)
    x_sample = sample_hypercube(limits, sample_res)
    return x_train, x_sample

def scotts_rule(x):
    # Compute value range
    train_range = np.max(x, axis=0) - np.min(x,axis=0)
    # Get dimensions of data
    dim = x.shape[1]
    # Compute scott's number
    n = x.shape[0]**(-1./(dim + 4.))
    # Compute coefficients
    scale = train_range*n
    return scale


######## Numpy ########

def test_compact_kernel_numpy(
                              x_train,
                              x_sample,
                              scale,
                              train_err,
                              order,
                             ):
    from gp_api.kernels.compact_kernel_evaluate import compact_kernel_evaluate
    t0 = time.time()
    K = compact_kernel_evaluate(
                                x_train,
                                x_sample,
                                scale=scale,
                                train_err=train_err,
                                q=order,
                               )
    t1 = time.time()
    print("  Numpy time:\t\t%f"%(t1-t0))
    return K

######## C extension ########

def test_compact_kernel_cext(
                             x_train,
                             x_sample,
                             scale,
                             train_err,
                             order,
                            ):
    from gp_api.kernels.compact_kernel import compact_kernel
    x_train = x_train
    x_sample = x_sample
    t0 = time.time()
    K = compact_kernel(
                       x_train,
                       x_sample,
                       scale=scale,
                       train_err=train_err,
                       order=order,
                      )
    t1 = time.time()
    print("  C extension time:\t%f"%(t1-t0))
    return K

######## Tests ########

def test_compact_kernel(
                        x_train,
                        x_sample=None,
                        scale=None,
                        train_err=None,
                        order=0
                       ):
    print("Testing Compact kernel")
    #print("  x = ", x_train)
    print("  x.shape = ", x_train.shape)
    if x_sample is None:
        print("  xp == x")
        print("  train_err: ", train_err)
        if not (train_err is None):
            train_err = np.ones(x_train.shape[0])*train_err
        x_sample = np.copy(x_train)
    else:
        print("  xp.shape = ",x_sample.shape)
        train_err = None
    scale = scotts_rule(x_train)
    print("  scale: ", scale)
    print("  order: ", order)
    K_numpy = test_compact_kernel_numpy(
                                        x_train,
                                        x_sample=x_sample,
                                        scale=scale,
                                        train_err=train_err,
                                        order=order,
                                       )
    K_cext = test_compact_kernel_cext(
                                      x_train,
                                      x_sample=x_sample,
                                      scale=scale,
                                      train_err=train_err,
                                      order=order,
                                     )
    assert np.allclose(K_numpy,K_cext)
    print("  cext pass!")


    

######## Main ########

def main():
    # It only makes sense to test this if gp_api works
    try:
        import gp_api
    except:
        print("No module gp_api. Skipping test")
        return
    # generate some training data
    x_train, x_sample = get_training_data()
    train_err = 0.01
    #test_compact_kernel(x_train)#, x_sample)
    test_compact_kernel(x_train, order=0)#, x_sample)
    test_compact_kernel(x_train, order=1)#, x_sample)
    test_compact_kernel(x_train, order=2)#, x_sample)
    test_compact_kernel(x_train, order=3)#, x_sample)
    test_compact_kernel(x_train, order=1, train_err=train_err)#, x_sample)
    test_compact_kernel(x_train, x_sample=x_sample, order=1)#, x_sample)

######## Execution ########

if __name__ == "__main__":
    main()
