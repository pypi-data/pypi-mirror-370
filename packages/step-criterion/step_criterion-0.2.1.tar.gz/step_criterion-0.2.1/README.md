# step-criterion

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Educational and diagnostic stepwise model selection for statsmodels with multiple criteria: AIC, BIC, Adjusted R², and p-values.**

This package provides a unified, flexible interface for **exploratory stepwise regression** with various selection criteria, supporting both OLS and GLM models with advanced features like interaction terms, transformations, and different statistical tests. **Designed for educational purposes and model exploration, not production model selection.**

## ✨ Key Features

- **🎯 Main Function**: `step_criterion()` - unified interface for all selection methods
- **📊 Multiple Criteria**: AIC, BIC, Adjusted R², and p-value based selection
- **🔧 Convenience Wrappers**: Specialized functions for each criterion
- **📈 Model Support**: OLS and GLM (including logistic, Poisson, etc.)
- **🧮 Advanced Formulas**: Interaction terms, transformations, categorical variables
- **⚡ GLM Flexibility**: Multiple test types (likelihood ratio, Wald)
- **🔇 Clean Output**: Automatic suppression of technical warnings
- **📋 R-like Results**: Familiar ANOVA-style step tables

## ⚠️ Important Statistical Considerations

**This package is designed for educational and exploratory purposes.** Stepwise selection has well-documented statistical limitations that users should understand:

### 🚨 Key Limitations

- **P-value Inflation**: Multiple testing inflates Type I error rates. P-values from stepwise procedures are biased and **should not be used for inference**
- **Overfitting**: Selected models are optimistic and may not generalize well to new data
- **Selection Bias**: Standard confidence intervals and hypothesis tests are invalid after model selection
- **Multiple Comparisons**: The more variables considered, the higher the chance of spurious associations

### 🎯 Recommended Uses

- **✅ Educational**: Learning about model selection and variable importance
- **✅ Exploratory Data Analysis**: Initial investigation of relationships  
- **✅ Diagnostic**: Understanding which variables might be relevant
- **✅ Hypothesis Generation**: Developing ideas for future confirmatory studies

### ❌ Not Recommended For

- **❌ Confirmatory Analysis**: Final statistical inference or hypothesis testing
- **❌ Production Models**: Automated model selection in production systems
- **❌ P-value Reporting**: Publishing p-values from stepwise-selected models
- **❌ Causal Inference**: Establishing causal relationships

### 📚 Better Alternatives for Production

For reliable inference and model selection, consider:
- **Cross-validation** with penalized regression (LASSO, Ridge, Elastic Net)
- **Information criteria** with proper model averaging
- **Bootstrap procedures** for selection uncertainty
- **Post-selection inference** methods when stepwise is unavoidable
- **Domain knowledge** guided model specification

## 🚀 Installation

```bash
pip install step-criterion
```

## 📖 Quick Start

### Basic Usage

```python
import pandas as pd
import statsmodels.api as sm
from step_criterion import step_criterion

# Load your data
df = pd.read_csv("your_data.csv")

# Perform stepwise selection with BIC
result = step_criterion(
    data=df,
    initial="y ~ 1",  # Start with intercept only
    scope={"upper": "y ~ x1 + x2 + x3 + x1:x2 + I(x1**2)"},
    direction="both",  # Forward and backward steps
    criterion="bic",   # Selection criterion
    trace=1            # Show step-by-step progress
)

# View results
print(result.model.summary())
print("\nStep-by-step path:")
print(result.anova)
```

## 📚 Comprehensive Documentation

### Main Function: `step_criterion()`

**This is the recommended entry point** - a unified interface supporting all selection criteria and model types.

```python
step_criterion(
    data,                    # pandas DataFrame
    initial,                 # Initial formula string
    scope=None,             # Upper/lower bounds for model terms
    direction="both",       # "both", "forward", or "backward"
    criterion="aic",        # "aic", "bic", "adjr2", or "p-value"
    trace=1,                # Verbosity level (0=silent, 1=progress)
    family=None,            # statsmodels family (None=OLS, or sm.families.*)
    glm_test="lr",          # For GLM p-value: "lr", "wald", "score", "gradient"
    alpha_enter=0.05,       # p-value threshold for entering (p-value criterion)
    alpha_exit=0.10,        # p-value threshold for removal (p-value criterion)
    steps=1000,             # Maximum number of steps
    keep=None,              # Optional function to track custom metrics
    fit_kwargs=None         # Additional arguments passed to model.fit()
)
```

### Selection Criteria

#### 1. **AIC (Akaike Information Criterion)**
```python
# Using main function
result = step_criterion(data=df, initial="y ~ 1", 
                       scope={"upper": "y ~ x1 + x2 + x3"}, 
                       criterion="aic")

# Using convenience wrapper (allows custom k penalty)
from step_criterion import step_aic
result = step_aic(data=df, initial="y ~ 1", 
                  scope={"upper": "y ~ x1 + x2 + x3"}, 
                  k=2.0)  # Standard AIC penalty
```

#### 2. **BIC (Bayesian Information Criterion)**
```python
# BIC automatically uses log(n) penalty
result = step_criterion(data=df, initial="y ~ 1", 
                       scope={"upper": "y ~ x1 + x2 + x3"}, 
                       criterion="bic")

# Convenience wrapper
from step_criterion import step_bic
result = step_bic(data=df, initial="y ~ 1", 
                  scope={"upper": "y ~ x1 + x2 + x3"})
```

#### 3. **Adjusted R² (OLS only)**
```python
# Maximizes adjusted R-squared
result = step_criterion(data=df, initial="y ~ 1", 
                       scope={"upper": "y ~ x1 + x2 + x3"}, 
                       criterion="adjr2")

# Convenience wrapper
from step_criterion import step_adjr2
result = step_adjr2(data=df, initial="y ~ 1", 
                    scope={"upper": "y ~ x1 + x2 + x3"})
```

#### 4. **P-value Based Selection**
```python
# OLS with F-tests
result = step_criterion(data=df, initial="y ~ 1", 
                       scope={"upper": "y ~ x1 + x2 + x3"}, 
                       criterion="p-value",
                       alpha_enter=0.05, alpha_exit=0.10)

# GLM with likelihood ratio tests
result = step_criterion(data=df, initial="y ~ 1", 
                       scope={"upper": "y ~ x1 + x2 + x3"}, 
                       criterion="p-value",
                       family=sm.families.Binomial(),
                       glm_test="lr")

# Convenience wrapper with GLM Wald tests
from step_criterion import step_pvalue
result = step_pvalue(data=df, initial="y ~ 1", 
                     scope={"upper": "y ~ x1 + x2 + x3"},
                     family=sm.families.Binomial(),
                     glm_test="wald")
```

### Model Types

#### Ordinary Least Squares (OLS)
```python
# family=None (default) uses OLS
result = step_criterion(
    data=df,
    initial="y ~ 1",
    scope={"upper": "y ~ x1 + x2 + x3"},
    criterion="bic"
)
```

#### Generalized Linear Models (GLM)
```python
import statsmodels.api as sm

# Logistic regression
result = step_criterion(
    data=df,
    initial="binary_outcome ~ 1",
    scope={"upper": "binary_outcome ~ x1 + x2 + x3"},
    criterion="aic",
    family=sm.families.Binomial()
)

# Poisson regression
result = step_criterion(
    data=df,
    initial="count_outcome ~ 1",
    scope={"upper": "count_outcome ~ x1 + x2 + x3"},
    criterion="bic",
    family=sm.families.Poisson()
)

# Gamma regression
result = step_criterion(
    data=df,
    initial="positive_outcome ~ 1",
    scope={"upper": "positive_outcome ~ x1 + x2 + x3"},
    criterion="aic",
    family=sm.families.Gamma()
)
```

### Advanced Formula Syntax

Using [Patsy](https://patsy.readthedocs.io/) formula syntax for complex model specifications:

```python
# Interaction terms
scope = {"upper": "y ~ x1 + x2 + x1:x2"}           # Specific interaction
scope = {"upper": "y ~ x1 * x2"}                   # Main effects + interaction
scope = {"upper": "y ~ (x1 + x2 + x3)**2"}         # All pairwise interactions

# Transformations
scope = {"upper": "y ~ x1 + I(x1**2) + I(x1**3)"}  # Polynomial terms
scope = {"upper": "y ~ x1 + np.log(x2) + np.sqrt(x3)"}  # Math functions

# Categorical variables
scope = {"upper": "y ~ x1 + C(category)"}          # Categorical encoding
scope = {"upper": "y ~ x1 + C(category, Treatment(reference='A'))"}  # Custom reference

# Mixed interactions
scope = {"upper": "y ~ x1 + x2 + C(group) + x1:C(group) + I(x2**2)"}
```

### GLM Test Options

For GLM models with p-value criterion, choose the appropriate test:

```python
# Likelihood Ratio Test (recommended for most cases)
result = step_criterion(data=df, initial="y ~ 1", criterion="p-value",
                       family=sm.families.Binomial(), glm_test="lr")

# Wald Test (faster, asymptotically equivalent)
result = step_criterion(data=df, initial="y ~ 1", criterion="p-value",
                       family=sm.families.Binomial(), glm_test="wald")

# Score and Gradient tests (currently mapped to LR with warning)
result = step_criterion(data=df, initial="y ~ 1", criterion="p-value",
                       family=sm.families.Binomial(), glm_test="score")
```

### Direction Options

```python
# Both directions (recommended) - can add and remove terms
result = step_criterion(data=df, initial="y ~ x1", direction="both",
                       scope={"upper": "y ~ x1 + x2 + x3"})

# Forward only - only adds terms
result = step_criterion(data=df, initial="y ~ 1", direction="forward",
                       scope={"upper": "y ~ x1 + x2 + x3"})

# Backward only - only removes terms  
result = step_criterion(data=df, initial="y ~ x1 + x2 + x3", direction="backward",
                       scope={"lower": "y ~ 1"})
```

## 🎯 Convenience Functions

While `step_criterion()` is the main interface, specialized convenience functions are available:

```python
from step_criterion import step_aic, step_bic, step_adjr2, step_pvalue

# AIC with custom penalty
result = step_aic(data=df, initial="y ~ 1", scope={"upper": "y ~ x1 + x2"}, k=2.5)

# BIC (automatic log(n) penalty)
result = step_bic(data=df, initial="y ~ 1", scope={"upper": "y ~ x1 + x2"})

# Adjusted R² (OLS only)
result = step_adjr2(data=df, initial="y ~ 1", scope={"upper": "y ~ x1 + x2"})

# P-value with custom thresholds
result = step_pvalue(data=df, initial="y ~ 1", scope={"upper": "y ~ x1 + x2"},
                     alpha_enter=0.01, alpha_exit=0.05)
```

## 📊 Results and Output

### StepwiseResult Object

All functions return a `StepwiseResult` object with:

```python
result.model     # Final statsmodels Results object
result.anova     # Step-by-step path DataFrame  
result.keep      # Optional custom metrics (if keep function provided)

# Access final model
print(result.model.summary())
print(f"Final AIC: {result.model.aic:.3f}")
print(f"R-squared: {result.model.rsquared:.3f}")

# View selection path
print(result.anova)
```

### Step Path Table (result.anova)

```
     Step     Df   Deviance  Resid. Df  Resid. Dev      AIC
0              NaN       NaN        15   305.619    308.392
1     + GNP    1.0    54.762        14   250.857    256.402
2   + UNEMP    1.0     8.363        13   242.494    250.812
3   + ARMED    1.0     4.177        12   238.317    249.408
4    + YEAR    1.0    18.662        11   219.655    233.518
```

## 🔍 Examples

**Note**: The following examples demonstrate the package's capabilities for **exploratory analysis**. Remember that p-values and model selection results should not be used for confirmatory inference.

### Example 1: Economic Data with Interactions

```python
import pandas as pd
import statsmodels.api as sm
from step_criterion import step_criterion

# Load Longley economic dataset
longley = sm.datasets.longley.load_pandas().data
longley.rename(columns={'TOTEMP': 'employment'}, inplace=True)

# Stepwise with BIC including interactions and polynomials
result = step_criterion(
    data=longley,
    initial="employment ~ 1",
    scope={"upper": "employment ~ GNP + UNEMP + ARMED + POP + YEAR + GNPDEFL + GNP:YEAR + I(GNP**2)"},
    direction="both",
    criterion="bic",
    trace=1
)

print("Final model:")
print(result.model.summary())
```

### Example 2: Logistic Regression for Binary Classification

```python
# Simulated medical data
np.random.seed(42)
n = 1000
data = pd.DataFrame({
    'age': np.random.normal(50, 15, n),
    'bmi': np.random.normal(25, 5, n),
    'cholesterol': np.random.normal(200, 40, n),
    'smoking': np.random.choice([0, 1], n, p=[0.7, 0.3]),
    'exercise': np.random.normal(3, 2, n)  # hours per week
})

# Create outcome with realistic relationships
logit = (-5 + 0.05*data['age'] + 0.1*data['bmi'] + 
         0.01*data['cholesterol'] + 2*data['smoking'] - 0.2*data['exercise'])
data['disease'] = (np.random.random(n) < 1/(1+np.exp(-logit))).astype(int)

# Stepwise logistic regression
result = step_criterion(
    data=data,
    initial="disease ~ 1",
    scope={"upper": "disease ~ age + bmi + cholesterol + smoking + exercise + age:smoking + I(bmi**2)"},
    direction="both",
    criterion="p-value",
    family=sm.families.Binomial(),
    glm_test="lr",
    alpha_enter=0.05,
    alpha_exit=0.10,
    trace=1
)

print("Logistic regression results:")
print(result.model.summary())
```

### Example 3: Comparing Multiple Criteria

```python
from step_criterion import step_criterion, step_aic, step_bic, step_adjr2

# Compare different selection criteria
criteria_results = {}

for criterion in ['aic', 'bic', 'adjr2']:
    result = step_criterion(
        data=df,
        initial="y ~ 1",
        scope={"upper": "y ~ x1 + x2 + x3 + x1:x2 + I(x1**2)"},
        criterion=criterion,
        trace=0  # Silent for comparison
    )
    criteria_results[criterion] = {
        'formula': result.model.model.formula,
        'aic': result.model.aic,
        'bic': result.model.bic,
        'rsquared_adj': getattr(result.model, 'rsquared_adj', None),
        'n_params': len(result.model.params)
    }

# Display comparison
comparison_df = pd.DataFrame(criteria_results).T
print("Comparison of selection criteria:")
print(comparison_df)
```

## ⚙️ Advanced Usage

### Custom Metrics Tracking

```python
def track_metrics(model, score):
    """Custom function to track additional metrics during selection"""
    return {
        'aic': model.aic,
        'bic': model.bic,
        'rsquared': getattr(model, 'rsquared', None),
        'condition_number': np.linalg.cond(model.model.exog)
    }

result = step_criterion(
    data=df,
    initial="y ~ 1",
    scope={"upper": "y ~ x1 + x2 + x3"},
    criterion="bic",
    keep=track_metrics  # Track custom metrics at each step
)

# View tracked metrics
print(result.keep)
```

### Handling Missing Data

```python
# The package works with statsmodels' missing data handling
result = step_criterion(
    data=df_with_missing,
    initial="y ~ 1",
    scope={"upper": "y ~ x1 + x2 + x3"},
    criterion="aic",
    fit_kwargs={'missing': 'drop'}  # or 'raise', 'skip'
)
```

## 🛠️ API Reference

### ⚠️ Interpretation Warning

**Results from this package should be interpreted carefully:**
- Use selected models for **exploration and hypothesis generation only**
- **Do not report p-values** from stepwise-selected models as if they were from pre-specified models
- **Confidence intervals and standard errors** are not valid after selection
- **Effect sizes may be inflated** due to selection bias
- Always validate findings with **independent data** or **proper post-selection methods**

### Main Function

- **`step_criterion()`**: Unified stepwise selection interface

### Convenience Functions

- **`step_aic()`**: AIC-based selection with custom penalty parameter
- **`step_bic()`**: BIC-based selection  
- **`step_adjr2()`**: Adjusted R²-based selection (OLS only)
- **`step_pvalue()`**: P-value based selection with test options

### Return Object

- **`StepwiseResult`**: Container with `model`, `anova`, and optional `keep` attributes

## 🔧 Dependencies

- Python ≥ 3.9
- pandas ≥ 1.5
- numpy ≥ 1.23  
- statsmodels ≥ 0.13

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MrRolie/step-criterion/issues)
- **Documentation**: This README and inline docstrings
- **Examples**: See `examples_usage.ipynb` in the repository

## 🔄 Version History

- **0.1.0**: Initial release with comprehensive stepwise selection support
