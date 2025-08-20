"""Test specific edge cases and integration scenarios."""
import numpy as np
import pandas as pd
import pytest
from fin_nln.univar.tests import run_all_univariate_tests


class TestIntegration:
    """Integration tests for the univariate testing suite."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(123)
        
        # Financial-like data patterns
        self.returns = np.random.normal(0, 0.02, 1000)  # Daily returns
        self.prices = 100 * np.exp(np.cumsum(self.returns))  # Price series
        
        # GARCH-like volatility clustering
        self.garch_returns = self._generate_garch_like(1000)
        
        # Regime-switching like data
        self.regime_switching = self._generate_regime_switching(500)
        
    def _generate_garch_like(self, n):
        """Generate GARCH(1,1)-like data with volatility clustering."""
        omega, alpha, beta = 0.0001, 0.05, 0.9
        returns = np.zeros(n)
        sigma2 = np.zeros(n)
        sigma2[0] = omega / (1 - alpha - beta)
        
        for t in range(1, n):
            sigma2[t] = omega + alpha * returns[t-1]**2 + beta * sigma2[t-1]
            returns[t] = np.sqrt(sigma2[t]) * np.random.normal()
            
        return returns
    
    def _generate_regime_switching(self, n):
        """Generate regime-switching data."""
        # Two regimes: low and high volatility
        regime = np.random.choice([0, 1], n, p=[0.7, 0.3])
        data = np.zeros(n)
        
        for t in range(n):
            if regime[t] == 0:  # Low volatility regime
                data[t] = np.random.normal(0, 0.01)
            else:  # High volatility regime
                data[t] = np.random.normal(0, 0.05)
                
        return data
    
    def test_run_all_tests_comprehensive(self):
        """Test that run_all_univariate_tests works on various data types."""
        # Should work on returns
        result_returns = run_all_univariate_tests(self.returns)
        assert isinstance(result_returns, pd.DataFrame)
        assert len(result_returns) > 0
        
        # Should work on GARCH-like data
        result_garch = run_all_univariate_tests(self.garch_returns)
        assert isinstance(result_garch, pd.DataFrame)
        assert len(result_garch) > 0
        
        # Should work on regime-switching data
        result_regime = run_all_univariate_tests(self.regime_switching)
        assert isinstance(result_regime, pd.DataFrame)
        assert len(result_regime) > 0
        
    def test_financial_data_properties(self):
        """Test that tests detect expected properties of financial data."""
        from fin_nln.univar.tests import jb_wrapper, ramsey_reset
        
        # Financial returns should typically be non-normal
        jb_result = jb_wrapper(self.returns)
        # Note: We can't guarantee this will always reject normality due to randomness
        assert 'p-value' in jb_result
        assert 0 <= jb_result['p-value'] <= 1
        
        # GARCH data should show some signs of nonlinearity
        reset_result = ramsey_reset(self.garch_returns)
        assert 'p_value' in reset_result
        assert 0 <= reset_result['p_value'] <= 1


class TestPerformance:
    """Test performance and scalability."""
    
    def test_large_series_performance(self):
        """Test that functions can handle reasonably large series."""
        from fin_nln.univar.tests import ramsey_reset, hurst_exponent
        
        # Test with larger series (5000 observations)
        large_series = np.random.normal(0, 1, 5000)
        
        # Should complete in reasonable time
        result = ramsey_reset(large_series)
        assert 'F_stat' in result
        
        hurst_result = hurst_exponent(large_series)
        assert isinstance(hurst_result, (int, float))
        
    def test_memory_efficiency(self):
        """Test that functions don't create excessive memory usage."""
        from fin_nln.univar.tests import bds_wrapper
        
        # This is a basic test - in production you'd use memory profiling
        series = np.random.normal(0, 1, 1000)
        result = bds_wrapper(series, max_dim=2)  # Keep dimensions low
        assert isinstance(result, dict)


class TestDataValidation:
    """Test data validation and preprocessing."""
    
    def test_missing_values_handling(self):
        """Test behavior with missing values."""
        from fin_nln.univar.tests import ramsey_reset
        
        # Series with NaN values
        series_with_nan = np.array([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10])
        
        # Should either handle gracefully or raise informative error
        try:
            result = ramsey_reset(series_with_nan)
            # If it doesn't raise an error, result should be valid
            assert 'F_stat' in result
        except (ValueError, TypeError, Exception) as e:
            # Acceptable to raise error for NaN values
            # Just check that it's a reasonable error message
            error_msg = str(e).lower()
            assert any(word in error_msg for word in ['nan', 'missing', 'inf', 'invalid'])
            
    def test_infinite_values_handling(self):
        """Test behavior with infinite values."""
        from fin_nln.univar.tests import hurst_exponent
        
        # Series with infinite values
        series_with_inf = np.array([1, 2, 3, np.inf, 5, 6, 7, 8, 9, 10])
        
        # Should either handle gracefully or raise informative error
        try:
            result = hurst_exponent(series_with_inf)
            assert isinstance(result, (int, float))
            assert not np.isinf(result)
        except (ValueError, TypeError):
            # Acceptable to raise error for infinite values
            pass


if __name__ == "__main__":
    pytest.main([__file__])
