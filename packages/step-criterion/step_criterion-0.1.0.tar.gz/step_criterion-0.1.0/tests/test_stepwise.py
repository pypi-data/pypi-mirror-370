"""
Basic tests for step-criterion package functionality.
"""

import pytest
import pandas as pd
import numpy as np
import statsmodels.api as sm
from step_criterion import step_criterion, step_aic, step_bic, step_adjr2, step_pvalue, StepwiseResult


class TestBasicFunctionality:
    """Test basic stepwise selection functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing."""
        np.random.seed(42)
        n = 50
        data = pd.DataFrame({
            'y': np.random.normal(0, 1, n),
            'x1': np.random.normal(0, 1, n),
            'x2': np.random.normal(0, 1, n),
            'x3': np.random.normal(0, 1, n)
        })
        # Add some relationship
        data['y'] = 2 + 1.5 * data['x1'] + 0.8 * data['x2'] + np.random.normal(0, 0.5, n)
        return data
    
    def test_step_criterion_basic(self, sample_data):
        """Test basic step_criterion functionality."""
        result = step_criterion(
            data=sample_data,
            initial="y ~ 1",
            scope={"upper": "y ~ x1 + x2 + x3"},
            criterion="aic",
            trace=0
        )
        
        assert isinstance(result, StepwiseResult)
        assert hasattr(result, 'model')
        assert hasattr(result, 'anova')
        assert result.anova is not None
        assert len(result.anova) > 0
    
    def test_all_criteria(self, sample_data):
        """Test all selection criteria work."""
        criteria = ['aic', 'bic', 'adjr2', 'p-value']
        
        for criterion in criteria:
            result = step_criterion(
                data=sample_data,
                initial="y ~ 1",
                scope={"upper": "y ~ x1 + x2 + x3"},
                criterion=criterion,
                trace=0
            )
            assert isinstance(result, StepwiseResult)
            assert result.model is not None
    
    def test_convenience_functions(self, sample_data):
        """Test convenience wrapper functions."""
        # Test step_aic
        result_aic = step_aic(
            data=sample_data,
            initial="y ~ 1",
            scope={"upper": "y ~ x1 + x2"},
            trace=0
        )
        assert isinstance(result_aic, StepwiseResult)
        
        # Test step_bic
        result_bic = step_bic(
            data=sample_data,
            initial="y ~ 1",
            scope={"upper": "y ~ x1 + x2"},
            trace=0
        )
        assert isinstance(result_bic, StepwiseResult)
        
        # Test step_adjr2
        result_adjr2 = step_adjr2(
            data=sample_data,
            initial="y ~ 1",
            scope={"upper": "y ~ x1 + x2"},
            trace=0
        )
        assert isinstance(result_adjr2, StepwiseResult)
        
        # Test step_pvalue
        result_pvalue = step_pvalue(
            data=sample_data,
            initial="y ~ 1",
            scope={"upper": "y ~ x1 + x2"},
            trace=0
        )
        assert isinstance(result_pvalue, StepwiseResult)
    
    def test_glm_functionality(self, sample_data):
        """Test GLM functionality with binary outcome."""
        # Create binary outcome
        data = sample_data.copy()
        logit = -1 + data['x1'] + 0.5 * data['x2']
        data['binary_y'] = (np.random.random(len(data)) < 1/(1+np.exp(-logit))).astype(int)
        
        result = step_criterion(
            data=data,
            initial="binary_y ~ 1",
            scope={"upper": "binary_y ~ x1 + x2 + x3"},
            criterion="aic",
            family=sm.families.Binomial(),
            trace=0
        )
        
        assert isinstance(result, StepwiseResult)
        assert result.model is not None
    
    def test_directions(self, sample_data):
        """Test different directions work."""
        directions = ['both', 'forward', 'backward']
        
        for direction in directions:
            if direction == 'backward':
                initial = "y ~ x1 + x2 + x3"
                scope = {"lower": "y ~ 1"}
            else:
                initial = "y ~ 1"
                scope = {"upper": "y ~ x1 + x2 + x3"}
            
            result = step_criterion(
                data=sample_data,
                initial=initial,
                scope=scope,
                direction=direction,
                criterion="aic",
                trace=0
            )
            assert isinstance(result, StepwiseResult)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_criterion(self):
        """Test that invalid criterion raises error."""
        data = pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]})
        
        with pytest.raises(ValueError, match="criterion must be one of"):
            step_criterion(
                data=data,
                initial="y ~ 1",
                criterion="invalid",
                trace=0
            )
    
    def test_invalid_direction(self):
        """Test that invalid direction raises error."""
        data = pd.DataFrame({'y': [1, 2, 3], 'x': [1, 2, 3]})
        
        with pytest.raises(ValueError, match="direction must be"):
            step_criterion(
                data=data,
                initial="y ~ 1",
                direction="invalid",
                trace=0
            )
    
    def test_adjr2_with_glm(self):
        """Test that adjr2 with GLM raises error."""
        data = pd.DataFrame({'y': [0, 1, 1], 'x': [1, 2, 3]})
        
        with pytest.raises(ValueError, match="criterion='adjr2' is only supported for OLS"):
            step_criterion(
                data=data,
                initial="y ~ 1",
                criterion="adjr2",
                family=sm.families.Binomial(),
                trace=0
            )


if __name__ == "__main__":
    pytest.main([__file__])
