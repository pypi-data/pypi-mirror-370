r"""**torchdensityestimation** is a package for the estimation of density transforms
(ratio, difference, etc.) based on PyTorch.

==================== =====================================================================
**Download**             https://pypi.python.org/pypi/torchdensityestimation/

**Source code**          https://github.com/FilippoAiraldi/torch-density-estimation/

**Report issues**        https://github.com/FilippoAiraldi/torch-density-estimation/issues
==================== =====================================================================


For density ratio estimation, this package implements the Relative unconstrained
Least-Squares Importance Fitting (RuLSIF) method for density ratio estimation [1,2,3].
For density difference estimation, it implements the Least-Squares Density-Difference
(LSDD) [4].

References
----------
.. [1] Yamada, M., Suzuki, T., Kanamori, T., Hachiya, H. and Sugiyama, M., 2013.
       Relative density-ratio estimation for robust distribution comparison. Neural
       computation, 25(5), pp.1324-1370.
.. [2] Liu, S., Yamada, M., Collier, N. and Sugiyama, M., 2013. Change-point detection
       in time-series data by relative density-ratio estimation. Neural Networks, 43,
       pp.72-83.
.. [3] Kanamori, T., Hido, S. and Sugiyama, M., 2009. A least-squares approach to direct
       importance estimation. The Journal of Machine Learning Research, 10,
       pp.1391-1445.
.. [4] Sugiyama, M., Suzuki, T., Kanamori, T., Du Plessis, M. C., Liu, S., & Takeuchi,
       I., 2013. Density-difference estimation. Neural Computation, 25(10),
       pp.2734-2775.
"""

__version__ = "1.0.0"

__all__ = ["ratio", "difference"]

from . import difference, ratio
