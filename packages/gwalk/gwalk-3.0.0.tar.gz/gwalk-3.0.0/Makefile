.PHONY: all

######## Variables ########
VERSION = 3.0.0
DIST=dist/gwalk-${VERSION}.tar.gz
version: clean
	echo "__version__ = ${VERSION}" > __version__.py
	echo "__version__ = ${VERSION}" > src/gwalk/__version__.py

# Location of catalog
FNAME_CATALOG = data/catalog_samples.hdf5
# Location of GWXXXXXX.h5 files from LIGO release
# May require some renaming of files (or linking)
GWTC_1_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_1_sample_release
GWTC_2_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_2
GWTC_2p1_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_2p1
GWTC_3_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_3
######## Installation ########

$(DIST): clean version
	python3 -m build

install: $(DIST)
	python3 -m pip install $(DIST)

testpypi: install unit_tests
	python3 -m twine upload --repository testpypi $(DIST)

pypi: testpypi
	python3 -m twine upload $(DIST)

######## Unit tests ########

unit_tests: \
	test_maha \
	test_decomposition \
	test_pdf \
	test_object \
	test_kl \
	test_grid

test_maha: install
	python3 tests/test_maha.py

test_decomposition: install
	python3 tests/test_decomposition.py

test_pdf: test_maha test_decomposition
	python3 tests/test_pdf.py

test_object: install
	python3 tests/test_object.py

test_kl: test_object test_pdf
	python3 tests/test_kl.py

test_grid: install test_kl
	python3 tests/test_grid.py

test_dpgmm: install test_kl
	python3 tests/test_dpgmm.py

######## Catalog ########

build-catalog: 
	mkdir -p data
	python3 tools/build_catalog.py $(FNAME_CATALOG) clean
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-1 		$(GWTC_1_RELEASE)
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-2 		$(GWTC_2_RELEASE)
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-2p1 	$(GWTC_2p1_RELEASE)
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-3 		$(GWTC_3_RELEASE)

######## Clean ########

clean:
	rm -rf .eggs
	rm -rf src/gwalk.egg-info
	rm -rf .tox
	rm -rf dist
	rm -rf build
	rm -f test_matern_plot.png
	rm -f src/gp_api/kernels/compact_kernel_cython.c
	rm -f src/gwalk/compat*so
	rm -f src/*so
	rm -f test_mesh.hdf5
	rm -rf test_*.png
	rm -rf test_*.hdf5
