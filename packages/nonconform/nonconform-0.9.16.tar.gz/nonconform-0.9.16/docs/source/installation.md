# Installation

Here you will learn how to install the `nonconform` package.

## Prerequisites

- Python 3.12 or higher is recommended

## Installation Methods

### Recommended: Using UV (Fast Package Manager)

[UV](https://github.com/astral-sh/uv) is a fast Python package manager that provides 10-100x faster dependency resolution than pip.

**Install UV first:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install nonconform:**
```bash
uv add nonconform
```

### Alternative: Using pip

For traditional installation, you can still use pip:

```bash
pip install nonconform
```

## Optional Dependencies

Existing optional dependencies are grouped into `[data]`, `[dev]`, `[docs]`, `[deep]`, `[fdr]` and `[all]`:
- `[data]`: Dataset loading functionality (includes `pyarrow`)
- `[dev]`: Development dependencies
- `[docs]`: Documentation dependencies
- `[deep]`: Deep Learning dependencies (`pytorch`)
- `[fdr]`: Online False Discovery Rate control (`online-fdr`)
- `[all]`: All optional dependencies

### Installing with Specific Dependencies

**Using UV (recommended):**
```bash
# With datasets support
uv add nonconform --extra data

# With online FDR control for streaming scenarios
uv add nonconform --extra fdr

# With all optional dependencies
uv add nonconform --all-extras
```

**Using pip (alternative):**
```bash
# With datasets support
pip install nonconform[data]

# With online FDR control for streaming scenarios
pip install nonconform[fdr]

# With all optional dependencies
pip install nonconform[all]
```

**Note**: The datasets are downloaded automatically when first used and cached both in memory and on disk (in `~/.cache/nonconform/`) for faster subsequent access.

## Get started

You are all set to find your first anomalies!

```bash
import nonconform
```