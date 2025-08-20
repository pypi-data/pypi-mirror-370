# Raindrop Python SDK

## Installation dependencies


```bash
pip install poetry
```

```bash
poetry install
```


## Run tests

### Using pytest (recommended)
```bash
# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_trace_attributes.py

# Run specific test
poetry run pytest tests/test_trace_attributes.py::TestTraceAttributes::test_user_id_attribute_direct

# Run tests with coverage
poetry run pytest --cov=raindrop
```

### Using green (legacy)
```bash
poetry run green -vv
```





