# fin_nln\multivar\tests.py

import numpy as np
import pandas as pd
from sklearn.decomposition import KernelPCA
from scipy.spatial.distance import pdist, squareform
from sklearn.feature_selection import mutual_info_regression
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.api import VAR

# essentially same as nonlinear_pca - equivalent name
def kernel_pca(X, kernel='rbf', gamma=15, n_components=None):
    """
    Perform Kernel Principal Component Analysis (Kernel PCA) on the dataset.
    
    Parameters:
    - X: np.ndarray or pd.DataFrame, the data to be transformed.
    - kernel: str, the kernel to use for mapping data to a higher-dimensional space.
      Common options are 'linear', 'poly', 'rbf', 'sigmoid'.
    - gamma: float, parameter for the 'rbf', 'poly', and 'sigmoid' kernels.
    - n_components: int or None, number of components to keep. If None, all components are kept.
    
    Returns:
    - transformed_data: np.ndarray, the data transformed into a lower-dimensional space.
    """
    kpca = KernelPCA(kernel=kernel, gamma=gamma, n_components=n_components)
    transformed_data = kpca.fit_transform(X)
    return transformed_data

# essentially same as kernel_pca - equivalent name
def nonlinear_pca(X: np.ndarray) -> np.ndarray:
    """
    Performs nonlinear PCA using Kernel Principal Component Analysis (Kernel PCA) with an RBF kernel.

    Parameters
    ----------
    X : np.ndarray
        Input data of shape (n_samples, n_features) to perform Kernel PCA on.

    Returns
    -------
    np.ndarray
        Transformed data after applying Kernel PCA, with the same number of samples but potentially fewer features.

    Notes
    -----
    KernelPCA is a generalization of PCA using kernel methods. The 'rbf' kernel is often used for 
    capturing nonlinear structures in the data.
    """
    kpca = KernelPCA(kernel='rbf', gamma=15)
    return kpca.fit_transform(X)

def mBDS(X: pd.DataFrame, epsilon=0.5, m=2) -> dict:
    """
    Multivariate BDS (mBDS) Test for detecting general nonlinearity.

    The mBDS test is a generalization of the BDS test to multivariate time series.
    It detects nonlinearity by comparing the correlation integral of the embedded
    phase space with the product of correlation integrals of the marginal distributions.

    Parameters
    ----------
    X : pd.DataFrame
        Multivariate time series data of shape (N, d), where N is the number of time 
        points and d is the number of dimensions (variables).
    epsilon : float, optional, default=0.5
        Threshold distance for the correlation integral.
    m : int, optional, default=2
        Embedding dimension.

    Returns
    -------
    dict
        A dictionary containing the following keys:
        - "C_m": The correlation integral for the reconstructed phase space.
        - "C_1_prod": The product of correlation integrals of the marginals.
        - "BDS_stat": The BDS statistic value.

    Notes
    -----
    The BDS statistic measures the difference between the correlation integral
    of the embedded time series and the product of correlation integrals of the 
    individual marginal distributions. A significantly high BDS statistic indicates 
    nonlinearity in the multivariate time series.

    The Chebyshev distance metric is used for computing pairwise distances.
    """
    X = X.dropna().values
    N, d = X.shape
    T = N - m + 1

    # Phase space reconstruction
    embedded = np.zeros((T, d * m))
    for i in range(m):
        embedded[:, i * d:(i + 1) * d] = X[i:T + i, :]

    # Compute pairwise distances in the embedded space
    D = squareform(pdist(embedded, metric='chebyshev'))
    C_m = np.sum(D < epsilon) / (T * (T - 1))

    # Univariate equivalent (product of marginals)
    C_1s = []
    for j in range(d):
        X_1d = np.zeros((T, m))
        for i in range(m):
            X_1d[:, i] = X[i:T + i, j]
        D1 = squareform(pdist(X_1d, metric='chebyshev'))
        C_1s.append(np.sum(D1 < epsilon) / (T * (T - 1)))

    C_1_prod = np.prod(C_1s)
    BDS_stat = np.sqrt(T) * (C_m - C_1_prod)

    return {
        "C_m": C_m,
        "C_1_prod": C_1_prod,
        "BDS_stat": BDS_stat
    }

def mutual_info(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes the mutual information between two variables, x and y.

    This function measures the dependency between the variables, indicating 
    how much information is shared between them. A higher mutual information 
    means a higher dependence.

    Parameters
    ----------
    x : np.ndarray
        Input array of shape (n_samples,) for the first variable.
    y : np.ndarray
        Input array of shape (n_samples,) for the second variable.

    Returns
    -------
    float
        The mutual information between x and y.

    Notes
    -----
    The function uses `mutual_info_regression` from sklearn, which is typically 
    used for continuous variables. The input arrays x and y are reshaped to 
    ensure the correct dimensionality for `mutual_info_regression`.
    """
    return mutual_info_regression(x.reshape(-1, 1), y)[0]

def granger(df, max_lag: int):
    """
    Perform the Granger Causality test on multivariate time series data.

    This test checks whether one time series can predict another time series.
    It is based on the idea that if time series X Granger-causes time series Y, 
    then past values of X can provide information about future values of Y.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the multivariate time series data. Each column represents 
        a different time series (variable), and rows represent time periods (observations).
    max_lag : int
        The maximum number of lags to consider when testing for Granger causality.

    Returns
    -------
    dict
        The result of the Granger Causality test. The function returns a dictionary 
        where each key corresponds to a pair of time series (the columns of the input DataFrame), 
        and each value contains the test results for that pair.

    Notes
    -----
    The test results include:
    - Test statistics for each lag.
    - P-values for each lag.
    - F-statistics and their corresponding p-values.
    
    A low p-value (typically < 0.05) indicates that the time series in question 
    Granger-causes the other.
    """
    # Perform the Granger Causality test and return the results
    return grangercausalitytests(df, max_lag)

def johansen(df: pd.DataFrame, det_order=-1, k_ar_diff=1) -> dict:
    """
    Perform the Johansen cointegration test for multivariate time series data.

    This test evaluates the presence of cointegration among multiple time series.
    The function returns the trace and maximum eigenvalue test statistics, as well as their critical values.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the multivariate time series data. Each column represents 
        a different time series (variable), and rows represent time periods (observations).
    det_order : int, optional, default=-1
        The deterministic trend assumption in the model:
        - -1: No deterministic trend.
        - 0: Constant.
        - 1: Linear trend.
    k_ar_diff : int, optional, default=1
        The number of lags used in the differencing of the time series.

    Returns
    -------
    dict
        A dictionary containing the following keys:
        - "trace_stat": The trace test statistics.
        - "crit_vals_trace": The critical values for the trace test.
        - "max_eig_stat": The maximum eigenvalue test statistics.
        - "crit_vals_maxeig": The critical values for the maximum eigenvalue test.
        - "eigenvectors": The eigenvectors corresponding to the cointegration relationships.

    Notes
    -----
    The trace test and the maximum eigenvalue test are two popular tests for cointegration.
    The trace test tests the null hypothesis that the number of cointegrating vectors is less than 
    or equal to r, while the maximum eigenvalue test tests the null hypothesis that the number 
    of cointegrating vectors is exactly r.
    """
    # Drop missing values and perform the Johansen cointegration test
    df_clean = df.dropna()
    result = coint_johansen(df_clean, det_order, k_ar_diff)
    
    return {
        "trace_stat": result.lr1.tolist(),
        "crit_vals_trace": result.cvt.tolist(),
        "max_eig_stat": result.lr2.tolist(),
        "crit_vals_maxeig": result.cvm.tolist(),
        "eigenvectors": result.evec
    }

def var(df: pd.DataFrame, maxlags=5) -> dict:
    """
    Fit a Vector Autoregression (VAR) model to multivariate time series data.

    This function fits a VAR model using the specified maximum number of lags and 
    returns the model's results, including the AIC, BIC, and a summary of the model.

    Parameters
    ----------
    df : pd.DataFrame
        The input multivariate time series data of shape (N, d), where N is the number 
        of observations (time points) and d is the number of variables (dimensions).
    maxlags : int, optional, default=5
        The maximum number of lags to be considered for the VAR model.

    Returns
    -------
    dict
        A dictionary containing the following keys:
        - "model": The fitted VAR model results.
        - "aic": The Akaike Information Criterion (AIC) of the model.
        - "bic": The Bayesian Information Criterion (BIC) of the model.
        - "summary": The summary statistics of the fitted model.

    Notes
    -----
    The model is fitted using the AIC (Akaike Information Criterion) for lag selection.
    The summary includes various statistics such as coefficients, standard errors, t-statistics, 
    and p-values for each equation in the system.
    """
    # Drop missing values and fit the VAR model
    model = VAR(df.dropna())
    result = model.fit(maxlags=maxlags, ic='aic')
    
    return {
        "model": result,
        "aic": result.aic,
        "bic": result.bic,
        "summary": result.summary()
    }


def run_all_multivariate_tests(df: pd.DataFrame) -> dict:
    """
    Run comprehensive multivariate nonlinearity and dependence tests on a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input multivariate time series data with each column representing a different variable.

    Returns
    -------
    dict
        A dictionary containing results from all multivariate tests:
        - 'mBDS': Multivariate BDS test results
        - 'mutual_info_matrix': Pairwise mutual information matrix
        - 'granger_causality': Granger causality test results (if >1 variable)
        - 'johansen_cointegration': Johansen cointegration test results (if >1 variable)
        - 'var_model': VAR model fit results (if >1 variable)
        - 'kernel_pca_2comp': Kernel PCA transformation (2 components)
        - 'kernel_pca_variance_explained': Variance explained by first 2 components

    Notes
    -----
    This function provides a comprehensive suite of tests for:
    - Nonlinear dependence (mBDS)
    - Information-theoretic dependence (mutual information)
    - Linear causality (Granger causality)
    - Long-run relationships (cointegration)
    - Linear dynamics (VAR modeling)
    - Nonlinear dimensionality reduction (Kernel PCA)
    """
    results = {}
    
    try:
        # Multivariate BDS test
        results['mBDS'] = mBDS(df)
    except Exception as e:
        results['mBDS'] = {'error': str(e)}
    
    # Mutual information matrix (for all pairs of variables)
    if df.shape[1] > 1:
        n_vars = df.shape[1]
        mi_matrix = np.zeros((n_vars, n_vars))
        
        for i in range(n_vars):
            for j in range(n_vars):
                if i != j:
                    try:
                        mi_matrix[i, j] = mutual_info(df.iloc[:, i].values, df.iloc[:, j].values)
                    except Exception as e:
                        mi_matrix[i, j] = np.nan
                        
        results['mutual_info_matrix'] = pd.DataFrame(
            mi_matrix, 
            index=df.columns, 
            columns=df.columns
        )
    else:
        results['mutual_info_matrix'] = "Need at least 2 variables for mutual information"
    
    # Tests that require multiple variables
    if df.shape[1] > 1:
        try:
            results['granger_causality'] = granger(df, max_lag=5)
        except Exception as e:
            results['granger_causality'] = {'error': str(e)}
            
        try:
            results['johansen_cointegration'] = johansen(df)
        except Exception as e:
            results['johansen_cointegration'] = {'error': str(e)}
            
        try:
            results['var_model'] = var(df)
        except Exception as e:
            results['var_model'] = {'error': str(e)}
    else:
        results['granger_causality'] = "Need at least 2 variables for Granger causality"
        results['johansen_cointegration'] = "Need at least 2 variables for cointegration"
        results['var_model'] = "Need at least 2 variables for VAR model"
    
    # Kernel PCA (works with single variable too)
    try:
        # Transform data using Kernel PCA
        kpca_result = kernel_pca(df.values, n_components=min(2, df.shape[1]))
        results['kernel_pca_2comp'] = kpca_result
        
        # Estimate variance explained (approximate for kernel PCA)
        if df.shape[1] > 1:
            total_var = np.var(df.values, axis=0).sum()
            explained_var = np.var(kpca_result, axis=0).sum()
            results['kernel_pca_variance_explained'] = explained_var / total_var
        else:
            results['kernel_pca_variance_explained'] = "Variance explained not meaningful for single variable"
            
    except Exception as e:
        results['kernel_pca_2comp'] = {'error': str(e)}
        results['kernel_pca_variance_explained'] = {'error': str(e)}
    
    return results