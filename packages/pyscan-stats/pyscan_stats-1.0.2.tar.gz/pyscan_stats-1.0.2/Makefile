.PHONY: init cpp py test clean build upload upload-test
SHELL := /bin/bash

init:
	uv venv .venv --python 3.12
	source .venv/bin/activate && uv pip install ".[dev]"

cpp:
	@echo "Building..."
	mkdir -p build
	source .venv/bin/activate && cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DPYSCAN_BUILD_TESTS=ON
	source .venv/bin/activate && cmake --build build

py:
	@echo "Reinstalling Python package..."
	source .venv/bin/activate && uv pip install . --no-deps --no-build-isolation --force-reinstall

test:
	@echo "Running tests..."
	source .venv/bin/activate && ctest --output-on-failure --test-dir build

clean:
	rm -rf build dist *.egg-info

build:
	@echo "Building source package..."
	@rm -rf build dist *.egg-info
	python -m build --sdist
	@echo "Building wheels..."
	CIBW_BEFORE_ALL="yum install -y boost-devel CGAL-devel gsl-devel" \
	CIBW_PRINT_BUILD_IDENTIFIERS=1 \
 	cibuildwheel --output-dir dist

upload:
	@echo "Uploading to PyPI..."
	python -m twine check dist/*
	python -m twine upload dist/* --verbose

upload-test:
	@echo "Uploading to Test PyPI..."
	python -m twine check dist/*
	python -m twine upload --repository testpypi dist/* --verbose
