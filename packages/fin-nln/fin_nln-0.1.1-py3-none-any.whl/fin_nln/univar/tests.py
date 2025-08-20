# flin\univar\preconditional_tests\adf_test.py
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import bds
import nolds
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.tsatools import lagmat
from scipy.stats import jarque_bera
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import kpss as kpsstest
from arch.unitroot import PhillipsPerron
from scipy.stats import shapiro
from statsmodels.tsa.ar_model import AutoReg

# fin_nln\univar\pre_whiten.py

def pre_whiten(ts: np.ndarray) -> np.ndarray:
    """
    Fits an AR(1) model to the time series and returns the residuals.

    Parameters
    ----------
    ts : np.ndarray
        Input time series data.

    Returns
    -------
    np.ndarray
        Residuals from the AR(1) model.

    Notes
    -----
    Pre-whitening removes linear autocorrelation, which is useful before applying 
    nonlinear tests or estimating surrogate data.
    """
    ts = np.asarray(ts)
    model = AutoReg(ts, lags=1).fit()
    return model.resid

# Stationarity Checking

# fin_nln\univar\adf_wrapper.py

def adf_wrapper(ts: np.ndarray) -> dict:
    """
    Performs the Augmented Dickey-Fuller (ADF) test for stationarity on a time series.

    Parameters
    ----------
    ts : np.ndarray
        Input time series data.

    Returns
    -------
    dict
        A dictionary containing the ADF statistic and p-value from the test.

    Notes
    -----
    The ADF test is used to check whether a unit root is present in a time series, 
    i.e., whether the series is non-stationary.
    A p-value less than 0.05 typically indicates stationarity.
    """
    ts = np.asarray(ts)
    result = adfuller(ts)
    return {'ADF Statistic': result[0], 'p-value': result[1]}

# fin_nln\univar\kpss_wrapper.py

def kpss_wrapper(ts: np.ndarray, regression='c', nlags='auto') -> dict:
    """
    Performs the KPSS test for stationarity on a time series.

    Parameters
    ----------
    ts : np.ndarray
        Input time series data.
    regression : str, optional
        Type of regression ('c' for constant, 'ct' for constant and trend).
    nlags : str or int, optional
        Lag selection. 'auto' uses default rules.

    Returns
    -------
    dict
        A dictionary containing the KPSS statistic and p-value from the test.

    Notes
    -----
    The KPSS test checks for the null hypothesis of stationarity.
    A p-value less than 0.05 typically indicates non-stationarity.
    """
    ts = np.asarray(ts)
    statistic, p_value, _, _ = kpsstest(ts, regression=regression, nlags=nlags)
    return {'KPSS Statistic': statistic, 'p-value': p_value}

# fin_nln\univar\pp_wrapper.py

def pp_wrapper(ts: np.ndarray) -> dict:
    """
    Performs the Phillips-Perron (PP) test for stationarity on a time series.

    Parameters
    ----------
    ts : np.ndarray
        Input time series data.

    Returns
    -------
    dict
        A dictionary containing the PP statistic and p-value from the test.

    Notes
    -----
    The PP test is an alternative to the ADF test for detecting a unit root.
    A p-value less than 0.05 typically indicates stationarity.
    """
    ts = np.asarray(ts)
    result = PhillipsPerron(ts)
    return {'PP Statistic': result.stat, 'p-value': result.pvalue}

# Normality Tests

# fin_nln\univar\jb_wrapper.py

def jb_wrapper(ts: np.ndarray) -> dict:
    """
    Performs the Jarque-Bera test for normality based on skewness and kurtosis.

    Parameters
    ----------
    ts : np.ndarray
        Input time series data.

    Returns
    -------
    dict
        A dictionary containing the Jarque-Bera statistic and p-value from the test.

    Notes
    -----
    The Jarque-Bera test checks whether sample skewness and kurtosis match a normal distribution.
    A p-value less than 0.05 typically indicates non-normality.
    """
    ts = np.asarray(ts)
    stat, p_value = jarque_bera(ts)
    return {'Jarque-Bera Statistic': stat, 'p-value': p_value}

# fin_nln\univar\sw_wrapper.py

def sw_wrapper(ts: np.ndarray) -> dict:
    """
    Performs the Shapiro-Wilk test for normality on a time series.

    Parameters
    ----------
    ts : np.ndarray
        Input time series data.

    Returns
    -------
    dict
        A dictionary containing the Shapiro-Wilk statistic and p-value from the test.

    Notes
    -----
    The Shapiro-Wilk test evaluates whether the data follows a normal distribution.
    A p-value less than 0.05 typically indicates non-normality.
    """
    ts = np.asarray(ts)
    stat, p_value = shapiro(ts)
    return {'Shapiro-Wilk Statistic': stat, 'p-value': p_value}

# Nonlinear Tests

# fin_nln\univar\bds_wrapper.py

def bds_wrapper(ts: np.ndarray, max_dim: int = 2):
    """
    BDS test for independence and identically distributed (i.i.d.) behavior in time series.

    The BDS test checks for nonlinearity by testing the null hypothesis that 
    the series is i.i.d. Rejection of the null suggests nonlinearity or dependence.

    Parameters
    ----------
    ts : np.ndarray
        The input time series residuals.
    max_dim : int, optional
        Maximum embedding dimension to test (default is 2).

    Returns
    -------
    dict
        Dictionary containing:
        - 'stat': The BDS test statistic.
        - 'p_value': The p-value of the test.

    Reference
    ---------
    Brock, Dechert, Scheinkman (1987). A Test for Independence Based on the Correlation Dimension.
    """
    ts = np.asarray(ts)
    result = bds(ts, max_dim=max_dim)
    return {
        "stat": result[0],
        "p_value": result[1]
    }

# fin_nln\univar\ramsey_reset.py

def ramsey_reset(
    y: np.ndarray,
    lags: int = 1,
    powers: list = [2, 3]
) -> dict:
    """
    Performs the Ramsey RESET test for omitted nonlinearity in a time series.

    This test checks for model misspecification by including higher powers
    of the fitted values and testing their joint significance.

    Parameters
    ----------
    y : np.ndarray
        A 1-D array of time series values.
    lags : int, optional
        Number of autoregressive lags to include in the base model (default is 1).
    powers : list of int, optional
        The powers of fitted values to include as nonlinear terms (default is [2, 3]).

    Returns
    -------
    dict
        A dictionary containing:
        - 'F_stat': The F-statistic testing the additional powers.
        - 'p_value': The p-value associated with the test.

    Reference
    ---------
    Ramsey, J. B. (1969). Tests for Specification Errors in Classical Linear 
    Least Squares Regression Analysis. Journal of the Royal Statistical Society.
    """
    y = np.asarray(y)
    X = lagmat(y, lags, trim='both')
    y = y[lags:]  # Align y with lagged X
    X_lin = add_constant(X)

    # Step 1: Fit base linear model
    linear_model = OLS(y, X_lin).fit()
    y_hat = linear_model.fittedvalues

    # Step 2: Augment with polynomial terms of predicted values
    nonlinear_terms = [y_hat**p for p in powers]
    X_aug = np.column_stack([X_lin] + nonlinear_terms)

    # Step 3: Fit augmented model and compute F-test
    reset_model = OLS(y, X_aug).fit()
    df_diff = len(powers)
    RSS0 = linear_model.ssr
    RSS1 = reset_model.ssr

    F_stat = ((RSS0 - RSS1) / df_diff) / (RSS1 / reset_model.df_resid)

    # Construct restriction matrix for last `df_diff` columns
    restriction_matrix = np.hstack([
        np.zeros((df_diff, X_aug.shape[1] - df_diff)),
        np.identity(df_diff)
    ])

    p_value = float(reset_model.f_test(restriction_matrix).pvalue)

    return {
        "F_stat": F_stat,
        "p_value": p_value
    }

# fin_nln\univar\keenan.py

def keenan(y: np.ndarray, lag: int = 1) -> dict:
    """
    Keenan's test for nonlinearity in time series.

    This test detects quadratic (second-order) nonlinearity by regressing 
    the residuals of a linear model on the squared fitted values.

    Parameters
    ----------
    y : np.ndarray
        The univariate time series residuals.
    lag : int, optional
        Number of lags for the autoregressive linear model (default is 1).

    Returns
    -------
    dict
        A dictionary containing:
        - "F_stat": The F-statistic from the auxiliary regression.
        - "p_value": The corresponding p-value indicating significance of nonlinearity.

    Reference
    ---------
    Keenan, D. M. (1985). A Tukey nonadditivity-type test for time series nonlinearity.
    Biometrika, 72(1), 39–44.
    """
    y = np.asarray(y)
    X = lagmat(y, lag, trim='both')
    y = y[lag:]
    X = add_constant(X)

    linear_model = OLS(y, X).fit()
    residuals = linear_model.resid
    fitted_squared = linear_model.fittedvalues ** 2

    aux_model = OLS(residuals, add_constant(fitted_squared)).fit()

    return {
        "F_stat": aux_model.fvalue,
        "p_value": aux_model.f_pvalue
    }

# fin_nln\univar\ljung_box.py

def ljung_box(ts: np.ndarray, lags: int = 20) -> pd.DataFrame:
    """
    Ljung-Box test for autocorrelation in a time series.

    Tests the null hypothesis that the data are independently distributed 
    (i.e., the autocorrelations at all lags up to the specified number are zero).

    Parameters
    ----------
    ts : np.ndarray
        Input time series data.
    lags : int, optional
        Number of lags to include in the test (default is 20).

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the Ljung-Box Q-statistics and corresponding p-values
        for each lag up to `lags`.

    Reference
    ---------
    Ljung, G. M. and Box, G. E. P. (1978). On a Measure of a Lack of Fit in Time Series Models.
    """
    ts = np.asarray(ts)
    result = acorr_ljungbox(ts, lags=lags, return_df=True)
    return result

# fin_nln\univar\mcleod_li.py

def mcleod_li(ts, lags=20):
    """
    Performs the Mcleod Li Test for nonlinearity.

    The test is based on the squared residuals of an autoregressive model. It is used to detect the conditional heteroskedasticity in 
    a univariate time series. 

    Parameters
    ----------
    ts : np.ndarray
        The input time series (1-D array-like).
        A 1-D array of time series values.
    lags : int, optional
        The number of lags to use (default is 20).

    Returns
    -------
    dict
        A dictionary containing:
        - 'F_stat': The F-statistic comparing linear vs nonlinear model.
        - 'p_value': The p-value for the added nonlinearity terms.

    Reference
    ---------
    Chen, Y. (2002). On the Robustness of Ljung-Box and McLeod-Li Q Tests: A Simulation Study. 
    Economics Bulletin, 3, 1-10.
    """
    # Step 1: Fit an AR model (or ARIMA, depending on your data)
    model = sm.tsa.AutoReg(ts, lags=1, old_names=False).fit()
    residuals = model.resid

    # Step 2: Square the residuals
    squared_resid = residuals**2

    # Step 3: Ljung-Box test on squared residuals
    ljung_box_results = acorr_ljungbox(squared_resid, lags=lags, return_df=True)
    return ljung_box_results

# fin_nln\univar\terasvirta

def terasvirta(y: np.ndarray, lag: int = 1, B: int = 1000, seed: int = 42) -> dict:
    """
    Terasvirta Neural Network Test with bootstrap p-value and multivariate lag expansion.

    Parameters
    ----------
    y : np.ndarray
        1D array of time series data.
    lag : int
        Number of lags to use.
    B : int
        Number of bootstrap replications.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    dict with F_stat, bootstrap_p_value, R2_increase.
    """
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    X = lagmat(y, lag, trim='both')
    y = y[lag:]

    # Linear model
    X_lin = add_constant(X)
    lin_model = OLS(y, X_lin).fit()

    # Nonlinear model: expand all lags (z^1, z^2, z^3)
    z_poly = np.column_stack([X**i for i in range(1, 4)])
    X_nnet = np.column_stack([X_lin, z_poly])
    nnet_model = OLS(y, X_nnet).fit()

    df_diff = z_poly.shape[1]
    RSS0 = lin_model.ssr
    RSS1 = nnet_model.ssr
    F_stat = ((RSS0 - RSS1) / df_diff) / (RSS1 / nnet_model.df_resid)

    # Bootstrap F-statistic
    f_stats_boot = []
    for _ in range(B):
        y_boot = rng.permutation(y)
        Xb = lagmat(y_boot, lag, trim='both')
        yb = y_boot[lag:]
        if len(yb) != Xb.shape[0]:
            continue  # skip bad resample
        Xb_lin = add_constant(Xb)
        zb_poly = np.column_stack([Xb**i for i in range(1, 4)])
        Xb_nnet = np.column_stack([Xb_lin, zb_poly])
        try:
            lin_b = OLS(yb, Xb_lin).fit()
            nnet_b = OLS(yb, Xb_nnet).fit()
            RSS0b = lin_b.ssr
            RSS1b = nnet_b.ssr
            Fb = ((RSS0b - RSS1b) / df_diff) / (RSS1b / nnet_b.df_resid)
            f_stats_boot.append(Fb)
        except:
            continue

    bootstrap_p = np.mean(np.array(f_stats_boot) >= F_stat)

    return {
        "F_stat": F_stat,
        "bootstrap_p_value": bootstrap_p,
        "R2_increase": nnet_model.rsquared - lin_model.rsquared
    }

# fin_nln\univar\tsay_test.py

def tsay_test(y: np.ndarray, max_lag: int = 5) -> dict:
    """
    Performs the Tsay test for nonlinearity in time series data.

    This test evaluates threshold autoregressive (TAR) structures to assess
    nonlinearity based on squared lagged values.

    Parameters
    ----------
    y : np.ndarray
        A 1-D array or pandas Series representing the time series data.
    max_lag : int, optional
        The maximum lag to use for constructing lagged variables (default is 5).

    Returns
    -------
    dict
        A dictionary containing:
        - 'F_stat': The F-statistic value.
        - 'p_value': The corresponding p-value for the nonlinear terms.

    Reference
    ---------
    Tsay, R. S. (1986). Nonlinearity Tests for Time Series. Biometrika.
    """
    if isinstance(y, pd.Series):
        y = y.values

    y = y - np.mean(y)  # Demean the series
    n = len(y)

    # Step 1: Fit linear AR model
    X_lagged = lagmat(y, max_lag, trim='both')
    Y_target = y[max_lag:]
    X_lagged = add_constant(X_lagged)
    linear_model = OLS(Y_target, X_lagged).fit()
    residuals = linear_model.resid

    # Step 2: Construct squared threshold variables
    Z = X_lagged[:, 1:]  # Drop the constant column
    Z_squared = Z ** 2
    Z_all = np.hstack([X_lagged, Z_squared])  # Combine original and squared lags

    # Step 3: Fit auxiliary regression
    aux_model = OLS(Y_target, Z_all).fit()

    # Step 4: Compute F-statistic
    k = Z.shape[1]
    RSS0 = linear_model.ssr
    RSS1 = aux_model.ssr
    F_stat = ((RSS0 - RSS1) / k) / (RSS1 / (n - 2 * k - 1))

    # Step 5: Use f_test to compute p-value for squared terms
    R = np.zeros((k, Z_all.shape[1]))  # Shape: (k, 2k+1)
    R[:, -k:] = np.identity(k)         # Only test last k columns (squared terms)
    p_value = float(aux_model.f_test(R).pvalue)

    return {
        "F_stat": F_stat,
        "p_value": p_value
    }

# NOTE THAT THESE TESTS SHOULD BE USED ON DETERMINISTIC NONLINEAR SYSTEMS 

# fin_nln\univar\lyapunov_exponent.py

def lyapunov_exponent(ts: np.ndarray) -> float:
    """
    Computes the largest Lyapunov exponent of a time series using the
    Rosenstein method, which is suitable for detecting chaos and 
    nonlinearity in dynamical systems.

    Parameters
    ----------
    ts : np.ndarray
        The input time series (1-D array-like).

    Returns
    -------
    float
        Estimated largest Lyapunov exponent. A positive value indicates
        chaos or sensitive dependence on initial conditions.

    Reference
    ---------
    Rosenstein, M.T., Collins, J.J., & De Luca, C.J. (1993).
    A practical method for calculating largest Lyapunov exponents 
    from small data sets. Physica D: Nonlinear Phenomena.
    """
    ts = np.asarray(ts)
    return max(nolds.lyap_e(ts)) #lyap_r(ts) gives an error and this is more computationally expensive

# fin_nln\univar\hurst_exponent.py

def hurst_exponent(ts: np.ndarray) -> float:
    """
    Calculates the Hurst exponent of a time series.

    The Hurst exponent is used to assess the long-term memory of a time series.
    A value H > 0.5 indicates persistence (trend-reinforcing), 
    H < 0.5 suggests mean reversion (anti-persistence), and 
    H ≈ 0.5 implies a random walk (no memory).

    Parameters
    ----------
    ts : np.ndarray
        The raw time series.

    Returns
    -------
    float
        The estimated Hurst exponent.

    Reference
    ---------
    Hurst, H. E. (1951). Long-term storage capacity of reservoirs.
    Transactions of the American Society of Civil Engineers, 116(1), 770–799.
    """
    ts = np.asarray(ts)
    return nolds.hurst_rs(ts)

# fin_nln\univar\run_all_tests.py

def run_all_univariate_tests(ts: np.ndarray) -> pd.DataFrame:
    """
    Runs all univariate tests (stationarity, normality, nonlinearity) on the time series.

    Parameters
    ----------
    ts : np.ndarray
        The raw time series.

    Returns
    -------
    pd.DataFrame
        A table of all test results (Test name, statistic, p-value, interpretation).
    """
    ts = np.asarray(ts)
    tests = []

    # Stationarity Tests
    adf = adf_wrapper(ts)
    tests.append(['ADF', adf['ADF Statistic'], adf['p-value'], 'Stationary' if adf['p-value'] < 0.05 else 'Non-stationary'])

    kpss = kpss_wrapper(ts)
    tests.append(['KPSS', kpss['KPSS Statistic'], kpss['p-value'], 'Non-stationary' if kpss['p-value'] < 0.05 else 'Stationary'])

    pp = pp_wrapper(ts)
    tests.append(['PP', pp['PP Statistic'], pp['p-value'], 'Stationary' if pp['p-value'] < 0.05 else 'Non-stationary'])

    # Normality Tests
    jb = jb_wrapper(ts)
    tests.append(['Jarque-Bera', jb['Jarque-Bera Statistic'], jb['p-value'], 'Non-normal' if jb['p-value'] < 0.05 else 'Normal'])

    sw = sw_wrapper(ts)
    tests.append(['Shapiro-Wilk', sw['Shapiro-Wilk Statistic'], sw['p-value'], 'Non-normal' if sw['p-value'] < 0.05 else 'Normal'])

    # Nonlinearity Tests
    resid = pre_whiten(ts)

    bds = bds_wrapper(resid)
    tests.append(['BDS', bds['stat'], bds['p_value'], 'Nonlinear/Dependent' if bds['p_value'] < 0.05 else 'IID'])

    ramsey = ramsey_reset(resid)
    tests.append(['Ramsey RESET', ramsey['F_stat'], ramsey['p_value'], 'Nonlinear effects present' if ramsey['p_value'] < 0.05 else 'No evidence of nonlinearity'])

    keenan_test = keenan(resid)
    tests.append(['Keenan', keenan_test['F_stat'], keenan_test['p_value'], 'Quadratic nonlinearity present' if keenan_test['p_value'] < 0.05 else 'No quadratic nonlinearity'])

    ljung = ljung_box(resid)
    ljung_pvalue = ljung['lb_pvalue'].iloc[-1]
    ljung_stat = ljung['lb_stat'].iloc[-1]
    tests.append(['Ljung-Box (lag 20)', ljung_stat, ljung_pvalue, 'Autocorrelation present' if ljung_pvalue < 0.05 else 'No significant autocorrelation'])

    mcleod_li_results = mcleod_li(resid)
    mcleod_li_pvalue = mcleod_li_results['lb_pvalue'].iloc[-1]
    mcleod_li_stat = mcleod_li_results['lb_stat'].iloc[-1]
    tests.append(['McLeod-Li (lag 20)', mcleod_li_stat, mcleod_li_pvalue, 'Conditional heteroskedasticity present' if mcleod_li_pvalue < 0.05 else 'No conditional heteroskedasticity'])

    terasvirta_test = terasvirta(resid)
    tests.append(['Terasvirta NN', terasvirta_test['F_stat'], terasvirta_test["bootstrap_p_value"], 'Nonlinearity present' if terasvirta_test['bootstrap_p_value'] < 0.05 else 'No evidence of nonlinearity'])

    tsay = tsay_test(ts)
    tests.append(['Tsay Test', tsay['F_stat'], tsay['p_value'], 'Threshold nonlinearity present' if tsay['p_value'] < 0.05 else 'No threshold nonlinearity'])

    # Chaos and Memory
    lyap_exp = lyapunov_exponent(ts)
    tests.append(['Largest Lyapunov Exponent', lyap_exp, None, 'Chaos detected' if lyap_exp > 0 else 'No chaos detected'])

    hurst_exp = hurst_exponent(ts)
    if hurst_exp > 0.5:
        interp = 'Persistence'
    elif hurst_exp < 0.5:
        interp = 'Anti-persistence'
    else:
        interp = 'Random walk'
    tests.append(['Hurst Exponent', hurst_exp, None, interp])

    df = pd.DataFrame(tests, columns=['Test', 'Statistic', 'p-value', 'Interpretation'])
    return df
