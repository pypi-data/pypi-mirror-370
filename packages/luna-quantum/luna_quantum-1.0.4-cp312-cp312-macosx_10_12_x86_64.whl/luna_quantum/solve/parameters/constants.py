# The default absolute tolerance that should be used for `numpy.isclose(...)`
# calls. Equal to the default used in `numpy.isclose(..)`.
DEFAULT_ATOL: float = 1.0e-8

# The default relative tolerance that should be used for ``numpy.isclose(...)``
# calls. Equal to the default used in ``numpy.isclose(..)``.
DEFAULT_RTOL: float = 1.0e-5

# The default timeout used for solver run with a specified target.
# Number of seconds before routine halts. Default is 2592000 for dimod.qbsolv.
DEFAULT_TIMEOUT: int = 10
