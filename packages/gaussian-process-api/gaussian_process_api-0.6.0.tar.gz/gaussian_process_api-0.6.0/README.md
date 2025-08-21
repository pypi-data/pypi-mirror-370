# Gaussian Process API

Some ground work for Gaussian Processes / storing to HDF5 in a clean API.

For use examples, check out the Jupyter notebooks!

## Installation:

Method 1:

This will only work with python 3.7+, and on a computer with cholmod installed (suitesparse, libsuitesparse-dev, etc...).
```
python3 -m pip install gaussian-process-api
```

Method 2:

This should work on any computer with anaconda:
```
conda create --name gp-api python=3.9
conda activate gp-api
conda install -c conda-forge scikit-sparse
python3 -m pip install gaussian-process-api
python3 -m pip install --upgrade ipykernel
python3 -m ipykernel install --user --name "gp-api" --display-name "gp-api" # For jupyter 
```

## Contributing

We are open to pull requests. 

If you would like to make a contribution, please explain what changes you are making and why.

## License

[MIT](https://choosealicense.com/licenses/mit)
