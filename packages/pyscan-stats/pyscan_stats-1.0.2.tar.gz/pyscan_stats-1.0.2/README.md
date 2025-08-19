# pyscan-stats

**[pyscan-stats](https://pypi.org/project/pyscan-stats/)** is a Python package for spatial scan statistics, created from a fork of the original **[pyscan](https://github.com/michaelmathen/pyscan)** library by Michael Matheny.

## User Installation

Wheels for Linux and macOS 14+ are available on PyPI. To install, run:

```bash
pip install pyscan-stats
```

## Documentation

1. Read the original documentation at [https://michaelmathen.github.io/pyscan/](https://michaelmathen.github.io/pyscan/)
2. Ready to run examples with data are available at: [https://github.com/simonpedrogonzalez/pyscan-stats-resources](https://github.com/simonpedrogonzalez/pyscan-stats-resources)

# New Features

## Faster Numpy-based Net Grid Constructor

```python
grid = pyscan.Grid(
    unique_xs, unique_ys, # (N,) numpy arrays of sorted unique x and y coordinates
    m_arr, b_arr # (N, 3) numpy arrays (x, y, weight)
    )
```

Removes the burden of instantiating in Python the `pyscan.WPoint` for each data point, which can be slow for larger datasets.

## Area-Limited Max Convex Subgrid Scan

```python
prec = 1e-3
disc_f = pyscan.RKULLDORF
max_area = 750 # Maximum number of pixels in the subgrid
max_subgrid = pyscan.max_subgrid_convex(grid, prec, disc_f, max_area)
```

Allows for specifying a maximum area for the subgrid, useful when the interest is in smaller anomalies or when computational resources are limited. Usage example [here](https://github.com/simonpedrogonzalez/pyscan-stats-resources/blob/master/8_AreaLimitedGridScanning.py). The implementation uses a sliding window version of Kadane's algorithm.

## Improvements

- Support for new Python versions (3.10+)
- Project dependency update and organization for easier extension and maintenance.
- Updated examples.

# Dev installation

1. `git clone https://github.com/simonpedrogonzalez/pyscan`.
1. [Install `uv` package manager](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) if not already installed (you can use other package managers).
2. Install CMake, Boost, GSL, CGAL if not already installed. For example, on Mac:
    ```bash
    brew install cmake boost gsl cgal
    ```
3. Run `make init` to create a Python 3.12 venv in `.venv` and install dev dependencies.

You are all set to start developing! The following utility commands are available:

- `make cpp`: compiles C++ code into the `build/` directory.
- `make py`: builds the Python package and installs it in the venv, with the last compiled cpp binaries.
- `make test`: runs the C++ tests, only works after compiling the C++ code.
- `make clean`: removes `build/`, `dist/` and packaging artifacts.

Notes:
If an error occurs executing one of the commands, try:
- Manually activating the venv `source .venv/bin/activate` and running the command again.
- Running `make clean` before `make cpp` to ensure a clean build.
- This setup was tested both on macOS (15.6, M2) and Linux (Ubuntu 20.04).

# About pyscan

Pyscan is a python wrapper around a large number of anomaly detection algorithms written in c++. These algorithms are from several papers by Jeff M. Phillips, Michael Matheny, Dong Xie, Mingxuan Han, Raghvendra Singh, Liang Zhang, Kaiqiang Wang, Deepak Agarwal, Andrew McGregor, Suresh Venkatasubramanian and Zhengyuan Zhu:

- [The Kernel Scan Statistic](https://arxiv.org/abs/1906.09381)
- [Scalable Spatial Scan Statistics for Trajectories](https://arxiv.org/abs/1906.01693)
- [Computing Approximate Statistical Discrepancy](https://arxiv.org/abs/1804.11287)
- [Scalable Spatial Scan Statistics through Sampling](https://dl.acm.org/citation.cfm?id=2996939)
- [Spatial Scan Statistics: Approximations and Performance Studies](http://www.cs.utah.edu/~jeffp/papers/stat-disc-KDD06.pdf)
- [The Hunting of the Bump: On Maximizing Statistical Discrepancy](http://www.cs.utah.edu/~jeffp/papers/stat-disc-SODA06.pdf)


## 🛠️ Need Help?

Things never go as planned! Feel free to reach out:

📧 simon.pedro.g@gmail.com  
🐙 [GitHub Issues](https://github.com/simonpedrogonzalez/pyscan/issues)

