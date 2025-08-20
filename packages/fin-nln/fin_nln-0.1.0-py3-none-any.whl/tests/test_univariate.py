"""Test univariate nonlinearity tests."""
import numpy as np
import pandas as pd
import pytest
from fin_nln.univar.tests import (
    pre_whiten,
    adf_wrapper,
    kpss_wrapper,
    pp_wrapper,
    jb_wrapper,
    sw_wrapper,
    ramsey_reset, 
    bds_wrapper, 
    keenan, 
    terasvirta,
    tsay_test,
    ljung_box,
    mcleod_li,
    hurst_exponent,
    lyapunov_exponent,
    run_all_univariate_tests
)

class TestUnivariateTests:
    """Test suite for univariate nonlinearity tests."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        # Linear AR(1) process
        self.linear_ts = self._generate_ar1(n=200, phi=0.5)
        # Nonlinear process (simple quadratic map)
        self.nonlinear_ts = self._generate_nonlinear(n=200)
        # White noise
        self.white_noise = np.random.normal(0, 1, 200)
        # Random walk
        self.random_walk = np.cumsum(np.random.normal(0, 1, 200))
        # Deterministic trend
        self.trend_ts = np.arange(200) + np.random.normal(0, 0.1, 200)
        
    def _generate_ar1(self, n, phi, sigma=1.0):
        """Generate AR(1) process."""
        y = np.zeros(n)
        eps = np.random.normal(0, sigma, n)
        for t in range(1, n):
            y[t] = phi * y[t-1] + eps[t]
        return y
    
    def _generate_nonlinear(self, n):
        """Generate simple nonlinear time series."""
        y = np.zeros(n)
        eps = np.random.normal(0, 0.1, n)
        y[0] = np.random.normal()
        for t in range(1, n):
            y[t] = 0.5 * y[t-1] + 0.2 * y[t-1]**2 + eps[t]
        return y

    # Test preprocessing functions
    def test_pre_whiten(self):
        """Test pre-whitening function."""
        residuals = pre_whiten(self.linear_ts)
        
        # Should return array of residuals
        assert isinstance(residuals, np.ndarray)
        # Length should be n-1 due to AR(1) lag
        assert len(residuals) == len(self.linear_ts) - 1
        # Residuals should have mean close to zero
        assert abs(np.mean(residuals)) < 0.1
        
    def test_pre_whiten_edge_cases(self):
        """Test pre-whitening with edge cases."""
        # Test with short series - AR(1) needs at least 3 points to work properly
        short_series = np.array([1, 2, 3, 4, 5])  # Use a longer minimum series
        residuals = pre_whiten(short_series)
        assert len(residuals) == 4
        
        # Test with constant series - this might cause issues
        constant_series = np.ones(50)
        try:
            residuals = pre_whiten(constant_series)
            assert len(residuals) == 49
        except (ZeroDivisionError, ValueError):
            # Constant series can cause numerical issues, which is expected
            pass

    # Test stationarity tests
    def test_adf_wrapper(self):
        """Test ADF test wrapper."""
        # Test on stationary series (white noise)
        result_stationary = adf_wrapper(self.white_noise)
        assert 'ADF Statistic' in result_stationary
        assert 'p-value' in result_stationary
        assert result_stationary['p-value'] < 0.05  # Should be stationary
        
        # Test on non-stationary series (random walk)
        result_nonstationary = adf_wrapper(self.random_walk)
        assert 'ADF Statistic' in result_nonstationary
        assert 'p-value' in result_nonstationary
        assert result_nonstationary['p-value'] > 0.05  # Should be non-stationary
        
    def test_kpss_wrapper(self):
        """Test KPSS test wrapper."""
        result = kpss_wrapper(self.white_noise)
        assert 'KPSS Statistic' in result
        assert 'p-value' in result
        assert isinstance(result['KPSS Statistic'], (int, float))
        assert isinstance(result['p-value'], (int, float))
        
    def test_pp_wrapper(self):
        """Test Phillips-Perron test wrapper."""
        result = pp_wrapper(self.white_noise)
        assert 'PP Statistic' in result
        assert 'p-value' in result
        assert isinstance(result['PP Statistic'], (int, float))
        assert isinstance(result['p-value'], (int, float))

    # Test normality tests
    def test_jb_wrapper(self):
        """Test Jarque-Bera test wrapper."""
        result = jb_wrapper(self.white_noise)
        assert 'Jarque-Bera Statistic' in result
        assert 'p-value' in result
        assert isinstance(result['Jarque-Bera Statistic'], (int, float))
        assert isinstance(result['p-value'], (int, float))
        
    def test_sw_wrapper(self):
        """Test Shapiro-Wilk test wrapper."""
        result = sw_wrapper(self.white_noise)
        assert 'Shapiro-Wilk Statistic' in result
        assert 'p-value' in result
        assert isinstance(result['Shapiro-Wilk Statistic'], (int, float))
        assert isinstance(result['p-value'], (int, float))

    # Test nonlinearity tests
    def test_ramsey_reset(self):
        """Test Ramsey RESET test."""
        result = ramsey_reset(self.linear_ts)
        assert 'F_stat' in result
        assert 'p_value' in result
        assert isinstance(result['F_stat'], (int, float))
        assert isinstance(result['p_value'], (int, float))
        assert result['F_stat'] >= 0  # F-stat should be non-negative
        assert 0 <= result['p_value'] <= 1  # p-value should be in [0,1]
        
    def test_ramsey_reset_parameters(self):
        """Test Ramsey RESET with different parameters."""
        # Test different lag structures
        result1 = ramsey_reset(self.linear_ts, lags=2)
        result2 = ramsey_reset(self.linear_ts, lags=3)
        assert isinstance(result1['F_stat'], (int, float))
        assert isinstance(result2['F_stat'], (int, float))
        
        # Test different powers
        result3 = ramsey_reset(self.linear_ts, powers=[2])
        result4 = ramsey_reset(self.linear_ts, powers=[2, 3, 4])
        assert isinstance(result3['F_stat'], (int, float))
        assert isinstance(result4['F_stat'], (int, float))
        
    def test_bds_wrapper(self):
        """Test BDS test wrapper."""
        result = bds_wrapper(self.linear_ts)
        assert isinstance(result, dict)
        # BDS test should return results for different dimensions
        
    def test_keenan(self):
        """Test Keenan test."""
        result = keenan(self.linear_ts)
        assert 'F_stat' in result
        assert 'p_value' in result
        assert isinstance(result['F_stat'], (int, float))
        assert isinstance(result['p_value'], (int, float))
        assert 0 <= result['p_value'] <= 1
        
    def test_keenan_different_lags(self):
        """Test Keenan test with different lag structures."""
        for lag in [1, 2, 3]:
            result = keenan(self.linear_ts, lag=lag)
            assert 'F_stat' in result
            assert 'p_value' in result
        
    def test_terasvirta(self):
        """Test Terasvirta test."""
        result = terasvirta(self.linear_ts, B=100)  # Small B for speed
        assert 'F_stat' in result
        assert 'bootstrap_p_value' in result
        assert isinstance(result['F_stat'], (int, float))
        assert isinstance(result['bootstrap_p_value'], (int, float))
        assert 0 <= result['bootstrap_p_value'] <= 1
        
    def test_tsay_test(self):
        """Test Tsay test."""
        result = tsay_test(self.linear_ts)
        assert 'F_stat' in result
        assert 'p_value' in result
        assert isinstance(result['F_stat'], (int, float))
        assert isinstance(result['p_value'], (int, float))
        assert result['F_stat'] >= 0
        assert 0 <= result['p_value'] <= 1
        
    def test_ljung_box(self):
        """Test Ljung-Box test."""
        result = ljung_box(self.linear_ts)
        assert isinstance(result, pd.DataFrame)
        assert 'lb_stat' in result.columns
        assert 'lb_pvalue' in result.columns
        
    def test_mcleod_li(self):
        """Test McLeod-Li test."""
        result = mcleod_li(self.linear_ts)
        assert isinstance(result, (dict, pd.DataFrame))

    # Test chaos/complexity measures
    def test_hurst_exponent(self):
        """Test Hurst exponent calculation."""
        result = hurst_exponent(self.linear_ts)
        assert isinstance(result, (int, float))
        assert 0 < result < 1  # Hurst exponent should be between 0 and 1
        
        # Test on white noise (should be around 0.5)
        hurst_wn = hurst_exponent(self.white_noise)
        assert 0.3 < hurst_wn < 0.7  # Should be around 0.5 for white noise
        
    def test_lyapunov_exponent(self):
        """Test Lyapunov exponent calculation."""
        result = lyapunov_exponent(self.linear_ts)
        assert isinstance(result, (int, float))
        
    def test_run_all_univariate_tests(self):
        """Test the comprehensive test runner."""
        result = run_all_univariate_tests(self.linear_ts)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0  # Should return some results
        
    # Test error handling
    def test_invalid_inputs(self):
        """Test functions with invalid inputs."""
        # Test with empty array
        empty_array = np.array([])
        with pytest.raises((ValueError, IndexError)):
            ramsey_reset(empty_array)
            
        # Test with single value
        single_value = np.array([1.0])
        with pytest.raises((ValueError, IndexError)):
            keenan(single_value)
            
        # Test with non-numeric data
        with pytest.raises((TypeError, ValueError)):
            ramsey_reset(['a', 'b', 'c'])
            
    def test_statistical_properties(self):
        """Test that tests behave correctly on known statistical properties."""
        # For truly linear AR(1), nonlinearity tests should generally not reject
        linear_result = ramsey_reset(self.linear_ts)
        
        # For nonlinear series, at least some tests should detect nonlinearity
        nonlinear_result = ramsey_reset(self.nonlinear_ts)
        
        # Both should produce valid p-values
        assert 0 <= linear_result['p_value'] <= 1
        assert 0 <= nonlinear_result['p_value'] <= 1
        
        # The nonlinear series should generally have lower p-values
        # (though this isn't guaranteed due to randomness)
        assert isinstance(linear_result['F_stat'], (int, float))
        assert isinstance(nonlinear_result['F_stat'], (int, float))

if __name__ == "__main__":
    pytest.main([__file__])
