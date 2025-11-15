# Tests Directory

This folder contains unit tests for the Fake News Detection System.

## Running Tests

### Install test dependencies
```bash
pip install pytest pytest-asyncio httpx
```

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_api.py -v
```

### Run with coverage
```bash
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html
```

## Test Structure

- `test_api.py` - API endpoint tests (FastAPI routes)
- `test_utils.py` - Utility function tests
- `test_claims.py` - Claim extraction tests (TODO)
- `test_vectorstore.py` - Vector store tests (TODO)

## Writing Tests

Follow pytest conventions:
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*()`

Example:
```python
def test_example():
    assert True
```

## CI/CD Integration

These tests can be integrated with GitHub Actions for continuous testing.
