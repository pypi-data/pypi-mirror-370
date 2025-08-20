# fin_nln\__init__.py
from . import data
from . import multivar
from . import univar

__all__ = ["data", "multivar", "univar"]

''' 
-->>>Note for SYON: I think we should keep our __init__.py free of imports outside our own library itself, 
we will import at each .py accordingly
from .data import DataAcquisition, Preprocessing
from .univariate.general_nonlinearity_tests import (
    bds_test, ramsey_reset_test, keenan_test,
    tsay_test, hinich_bicorrelation_test, engle_granger_test
)
from .univariate.linear_dependence_tests import (
    ljung_box_test, breusch_godfrey_test
)
from .univariate.nonlinear_tests import bds_test, ramsey_reset_test, keenan_test

__all__ = [
    'DataAcquisition',
    'Preprocessing',
    'bds_test',
    'ramsey_reset_test',
    'keenan_test',
    'tsay_test',
    'hinich_bicorrelation_test',
    'engle_granger_test',
    'ljung_box_test',
    'breusch_godfrey_test'
]

# Univariate Linearity Tests

'''

''' NOTE's
- Ljung-Box Test **(ENTER_METHOD_NAME)**
    - Tests for autocorrelation in residuals (linear dependence).

- Augmented Dickey-Fuller (ADF)	**(ENTER_METHOD_NAME)**
    - Stationarity check — helps determine linear time series behavior.

- AR Model Fit & Residual Analysis **(ENTER_METHOD_NAME)**
    - Fit AR(p) and inspect residuals for linear structure.

# Univariate **Non**-Linearity Tests

- Hurst Exponent (R/S Analysis)	**(ENTER_METHOD_NAME)**
    - Measures long memory (persistence or anti-persistence).

- BDS Test **(ENTER_METHOD_NAME)**
    - Detects general nonlinearity in residuals of a time series.

- Largest Lyapunov Exponent	**(ENTER_METHOD_NAME)**
    - Detects chaotic behavior via sensitivity to initial conditions.

- Tsay Test	**(ENTER_METHOD_NAME)**
    - A test for threshold nonlinearity in autoregressive processes.

# Multivariate Linearity Tests

- VAR Model Fit	**(ENTER_METHOD_NAME)**
    - Tests for linear interdependencies among variables.

- Granger Causality Test **(ENTER_METHOD_NAME)**
    - Determines if one time series linearly predicts another.

- Cointegration Tests (Johansen) **(ENTER_METHOD_NAME)**
    - Tests for linear long-run equilibrium relationships.

# Multivariate **Non**-Linearity Tests

- Multivariate BDS Test (mBDS) **(ENTER_METHOD_NAME)**
    - Extension of BDS to multivariate context.

- Mutual Information **(ENTER_METHOD_NAME)**
    - Measures nonlinear dependence among variables.

- Nonlinear PCA / Kernel PCA **(ENTER_METHOD_NAME)**
    - Uncovers nonlinear structures in multivariate data.

- Cross-Lyapunov Exponents	**(ENTER_METHOD_NAME)**
    - Tests chaotic synchronization across variables.'
'''