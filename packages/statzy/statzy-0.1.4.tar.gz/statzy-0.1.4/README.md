# statzy

A simple Python library for:
- get quick data overview 
- detecting and visualizing outliers in datasets
- etc.

## How to Upload this module to PyPI?
1. Update the `version` field in your `setup.py` before each release, e.g., `0.1.0`, `0.1.1`, `0.2.0` etc.
2. Push your changes to git
```bash
commit -m '...'
git push
```
3. Create a new **git tag** and push it to git
```bash
git tag v0.1.0 # Create a Git tag matching the pattern in the workflow
git push origin v0.1.0 # Without this, the tag would only exist locally
```

This will trigger the GitHub Action, which builds and uploads your package automatically to PyPI.

## Installation

```bash
pip install statzy
```

## Usage
```python
import statzy as st
import pandas as pd

data = pd.DataFrame({'value': [10, 12, 14, 110, 15]})
outliers, low, high = st.detect_outliers_iqr(data, 'value')
print(outliers)
```
