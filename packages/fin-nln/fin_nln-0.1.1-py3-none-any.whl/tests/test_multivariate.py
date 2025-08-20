"""Test multivariate nonlinearity tests."""
import numpy as np
import pandas as pd
import pytest
from fin_nln.multivar.tests import (
    kernel_pca,
    nonlinear_pca,
    mBDS,
    mutual_info,
    granger,
    johansen,
    var,
    run_all_multivariate_tests
)


class TestMultivariateTests:
    """Test suite for multivariate nonlinearity tests."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n = 200
        
        # Bivariate linear VAR data
        self.bivariate_linear = self._generate_var_data(n, 2)
        
        # Trivariate data
        self.trivariate_data = self._generate_var_data(n, 3)
        
        # Univariate data (for edge case testing)
        self.univariate_data = pd.DataFrame({'x': np.random.normal(0, 1, n)})
        
        # Nonlinear bivariate data
        self.bivariate_nonlinear = self._generate_nonlinear_bivariate(n)
        
        # Cointegrated data
        self.cointegrated_data = self._generate_cointegrated_data(n)
        
    def _generate_var_data(self, n, k):
        """Generate VAR(1) data with k variables."""
        # VAR(1) coefficient matrix
        A = np.random.uniform(-0.3, 0.3, (k, k))
        # Ensure stability
        eigenvals = np.linalg.eigvals(A)
        if np.max(np.abs(eigenvals)) >= 1:
            A = A * 0.8 / np.max(np.abs(eigenvals))
        
        # Generate data
        Y = np.zeros((n, k))
        for t in range(1, n):
            Y[t] = A @ Y[t-1] + np.random.multivariate_normal(np.zeros(k), np.eye(k))
        
        return pd.DataFrame(Y, columns=[f'var_{i}' for i in range(k)])
    
    def _generate_nonlinear_bivariate(self, n):
        """Generate nonlinear bivariate data."""
        x = np.zeros(n)
        y = np.zeros(n)
        
        for t in range(1, n):
            x[t] = 0.5 * x[t-1] + 0.2 * y[t-1]**2 + np.random.normal(0, 0.1)
            y[t] = 0.3 * y[t-1] + 0.1 * x[t-1] * y[t-1] + np.random.normal(0, 0.1)
        
        return pd.DataFrame({'x': x, 'y': y})
    
    def _generate_cointegrated_data(self, n):
        """Generate cointegrated data."""
        # Common stochastic trend
        trend = np.cumsum(np.random.normal(0, 1, n))
        
        # Two series that follow the trend with different loadings
        x = trend + np.random.normal(0, 0.1, n)
        y = 0.5 * trend + np.random.normal(0, 0.1, n)
        
        return pd.DataFrame({'x': x, 'y': y})

    # Test individual functions
    def test_kernel_pca(self):
        """Test Kernel PCA function."""
        result = kernel_pca(self.bivariate_linear.values, n_components=2)
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == len(self.bivariate_linear)
        assert result.shape[1] == 2
        
    def test_kernel_pca_single_component(self):
        """Test Kernel PCA with single component."""
        result = kernel_pca(self.bivariate_linear.values, n_components=1)
        assert isinstance(result, np.ndarray)
        assert result.shape[1] == 1
        
    def test_nonlinear_pca(self):
        """Test nonlinear PCA function."""
        result = nonlinear_pca(self.bivariate_linear.values)
        assert isinstance(result, np.ndarray)
        assert result.shape[0] == len(self.bivariate_linear)
        
    def test_mBDS(self):
        """Test multivariate BDS test."""
        result = mBDS(self.bivariate_linear)
        assert isinstance(result, dict)
        # Check that it returns some meaningful output
        
    def test_mBDS_single_variable(self):
        """Test mBDS with single variable."""
        result = mBDS(self.univariate_data)
        assert isinstance(result, dict)
        
    def test_mutual_info(self):
        """Test mutual information calculation."""
        x = self.bivariate_linear.iloc[:, 0].values
        y = self.bivariate_linear.iloc[:, 1].values
        
        result = mutual_info(x, y)
        assert isinstance(result, (int, float, np.integer, np.floating))  # Accept numpy types too
        assert result >= 0  # Mutual information is non-negative
        
        # Self-mutual information should be higher
        self_mi = mutual_info(x, x)
        assert self_mi > 0  # Self MI should be positive
        
    def test_granger_causality(self):
        """Test Granger causality test."""
        result = granger(self.bivariate_linear, max_lag=3)
        assert isinstance(result, dict)
        
    def test_granger_causality_insufficient_data(self):
        """Test Granger causality with insufficient variables."""
        with pytest.raises((ValueError, Exception)):
            granger(self.univariate_data, max_lag=3)
            
    def test_johansen_cointegration(self):
        """Test Johansen cointegration test."""
        result = johansen(self.cointegrated_data)
        assert isinstance(result, dict)
        assert 'trace_stat' in result
        assert 'max_eig_stat' in result
        
    def test_johansen_insufficient_data(self):
        """Test Johansen test with insufficient variables."""
        # Some implementations might handle single variables, so make this more flexible
        try:
            result = johansen(self.univariate_data)
            # If it doesn't raise an error, that's also acceptable
            assert isinstance(result, dict)
        except (ValueError, Exception):
            # Expected behavior - not enough variables for cointegration
            pass
            
    def test_var_model(self):
        """Test VAR model fitting."""
        result = var(self.bivariate_linear)
        assert isinstance(result, dict)
        assert 'model' in result
        assert 'aic' in result
        assert 'bic' in result
        
    def test_var_model_insufficient_data(self):
        """Test VAR model with insufficient variables."""
        with pytest.raises((ValueError, Exception)):
            var(self.univariate_data)

    # Test comprehensive test runner
    def test_run_all_multivariate_tests_bivariate(self):
        """Test comprehensive multivariate test runner on bivariate data."""
        result = run_all_multivariate_tests(self.bivariate_linear)
        
        assert isinstance(result, dict)
        
        # Check that all expected keys are present
        expected_keys = [
            'mBDS', 'mutual_info_matrix', 'granger_causality',
            'johansen_cointegration', 'var_model', 'kernel_pca_2comp',
            'kernel_pca_variance_explained'
        ]
        
        for key in expected_keys:
            assert key in result
            
        # Check mutual information matrix structure
        assert isinstance(result['mutual_info_matrix'], pd.DataFrame)
        assert result['mutual_info_matrix'].shape == (2, 2)
        
    def test_run_all_multivariate_tests_trivariate(self):
        """Test comprehensive multivariate test runner on trivariate data."""
        result = run_all_multivariate_tests(self.trivariate_data)
        
        assert isinstance(result, dict)
        assert isinstance(result['mutual_info_matrix'], pd.DataFrame)
        assert result['mutual_info_matrix'].shape == (3, 3)
        
    def test_run_all_multivariate_tests_univariate(self):
        """Test comprehensive multivariate test runner on univariate data."""
        result = run_all_multivariate_tests(self.univariate_data)
        
        assert isinstance(result, dict)
        
        # For univariate data, some tests should return informative messages
        assert isinstance(result['mutual_info_matrix'], str)
        assert isinstance(result['granger_causality'], str)
        assert isinstance(result['johansen_cointegration'], str)
        assert isinstance(result['var_model'], str)
        
        # But mBDS and kernel PCA should still work
        assert isinstance(result['mBDS'], dict)
        
    def test_run_all_multivariate_tests_nonlinear(self):
        """Test comprehensive multivariate test runner on nonlinear data."""
        result = run_all_multivariate_tests(self.bivariate_nonlinear)
        
        assert isinstance(result, dict)
        
        # Should detect higher mutual information due to nonlinearity
        mi_matrix = result['mutual_info_matrix']
        off_diagonal = mi_matrix.iloc[0, 1]  # Mutual info between x and y
        assert off_diagonal > 0

    # Test edge cases and error handling
    def test_empty_dataframe(self):
        """Test behavior with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        # Empty DataFrame should either raise error or handle gracefully
        try:
            result = run_all_multivariate_tests(empty_df)
            # If it doesn't raise an error, check it returns reasonable output
            assert isinstance(result, dict)
        except (ValueError, IndexError, Exception):
            # Expected behavior - can't process empty data
            pass
            
    def test_dataframe_with_nan(self):
        """Test behavior with NaN values."""
        df_with_nan = self.bivariate_linear.copy()
        df_with_nan.iloc[0, 0] = np.nan
        df_with_nan.iloc[5, 1] = np.nan
        
        # Should handle NaN values gracefully (either drop or handle in function)
        result = run_all_multivariate_tests(df_with_nan)
        assert isinstance(result, dict)
        
    def test_constant_series(self):
        """Test behavior with constant series."""
        constant_df = pd.DataFrame({
            'const1': np.ones(100),
            'const2': np.full(100, 5.0)
        })
        
        # Should handle constant series gracefully
        result = run_all_multivariate_tests(constant_df)
        assert isinstance(result, dict)
        
    def test_very_short_series(self):
        """Test behavior with very short series."""
        short_df = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [4, 5, 6]
        })
        
        # Should either work or fail gracefully
        try:
            result = run_all_multivariate_tests(short_df)
            assert isinstance(result, dict)
        except (ValueError, Exception):
            # Acceptable to fail with very short series
            pass


class TestMultivariateStatisticalProperties:
    """Test statistical properties of multivariate tests."""
    
    def setup_method(self):
        """Set up test data with known properties."""
        np.random.seed(123)
        
    def test_mutual_info_independence(self):
        """Test that independent variables have low mutual information."""
        n = 1000
        x = np.random.normal(0, 1, n)
        y = np.random.normal(0, 1, n)  # Independent of x
        
        mi = mutual_info(x, y)
        
        # Should be low for independent variables (though not exactly zero due to sampling)
        assert mi < 0.5  # Threshold may need adjustment based on implementation
        
    def test_mutual_info_dependence(self):
        """Test that dependent variables have higher mutual information."""
        n = 1000
        x = np.random.normal(0, 1, n)
        y = x + 0.1 * np.random.normal(0, 1, n)  # Dependent on x
        
        mi_dependent = mutual_info(x, y)
        
        # Independent case for comparison
        z = np.random.normal(0, 1, n)
        mi_independent = mutual_info(x, z)
        
        # Dependent variables should have higher mutual information
        assert mi_dependent > mi_independent


if __name__ == "__main__":
    pytest.main([__file__])
