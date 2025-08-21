.PHONY: tests install clean build-dist testpypi
######## Installation ########
VERSION = 0.6.0
DIST=dist/gaussian_process_api-${VERSION}.tar.gz
version: clean
	echo "__version__ = '${VERSION}'" > __version__.py
	echo "__version__ = '${VERSION}'" > src/gp_api/__version__.py

tests: clean install \
	test_compact_kernel \
    test_hypercube \
	test_linear_fit_plot.png \
	test_gauss_2d_plot.png \
	test_serialization_fit.hdf5 \
	test_multigauss_plot.png \
	test_density_plot.png \
	test_marginals_plot.png \
	test_matern_plot.png 

test_compact_kernel: install
	python3 tests/test_compact_kernel.py

test_hypercube: install
	python3 tests/test_hypercube.py

test_linear_fit_plot.png: install
	python3 tests/test_linear_fit.py

test_matern_plot.png: install
	python3 tests/test_matern.py

test_serialization_fit.hdf5: install
	python3 tests/test_serialization.py

test_gauss_2d_plot.png: install
	python3 tests/test_gauss_nd.py

test_multigauss_plot.png: install
	python3 tests/test_multigauss.py

test_density_plot.png: install
	python3 tests/test_density.py

test_marginals_plot.png: install
	python3 tests/test_marginals.py

test_sample_gp_plot.png: install
	python3 tests/test_sample_gp.py

$(DIST): clean version
	python3 -m build

install: $(DIST)
	python3 -m pip install $(DIST)

testpypi: clean install tests
	python3 -m twine upload --repository testpypi $(DIST)

pypi: testpypi
	python3 -m twine upload $(DIST)

clean:
	rm -rf .eggs
	rm -rf src/gp_api.egg-info
	rm -rf .tox
	rm -f test_*.png
	rm -f src/gp_api/kernels/matern_kernel_cython.c
	rm -f src/gp_api/kernels/compact_kernel_cython.c
	rm -f src/gp_api/compat*so
	rm -f src/*so
	rm -f src/compac*so
	rm -f test_serialization_fit.hdf5
