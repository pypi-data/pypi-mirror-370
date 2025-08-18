# TranspoLibre Testing Documentation

## Overview

This directory contains the comprehensive test suite for TranspoLibre, a PO file translation tool supporting LibreTranslate, Ollama, and local AI models. The test suite follows industry best practices with clear separation of concerns, comprehensive coverage, and performance benchmarking.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual modules
│   ├── test_parse_arguments.py
│   ├── test_get_lang_name.py
│   ├── test_trans_msg.py
│   ├── test_trans_list.py
│   ├── test_update_pofile.py
│   ├── test_trans_pofile.py
│   ├── test_trans_local.py
│   └── test_trans_ollama.py
├── integration/             # End-to-end workflow tests
│   ├── test_main.py
│   └── test_translation_flow.py
├── performance/             # Performance and benchmark tests
│   └── test_batch_processing.py
├── fixtures/                # Test data and sample files
│   └── sample_po_files/
├── e2e/                    # Optional end-to-end tests with real APIs
└── conftest.py             # Shared pytest fixtures

```

## Quick Start

### Installation

Install test dependencies:

```bash
pip install -e .[test]
```

Or install all development dependencies:

```bash
pip install -e .[dev,test]
```

### Running Tests

Run all tests:
```bash
make test
```

Run specific test categories:
```bash
make test-unit          # Unit tests only
make test-integration   # Integration tests
make test-performance   # Performance tests
make test-coverage      # With coverage report
```

Run tests in parallel for faster execution:
```bash
make test-parallel
```

## Test Categories

### Unit Tests

Unit tests verify individual components in isolation:

- **`test_parse_arguments.py`**: CLI argument parsing and validation
- **`test_get_lang_name.py`**: ISO 639 language code conversion
- **`test_trans_msg.py`**: Message translation with URL/email detection
- **`test_trans_list.py`**: Language listing functionality
- **`test_update_pofile.py`**: PO file entry updates
- **`test_trans_pofile.py`**: LibreTranslate engine workflow
- **`test_trans_local.py`**: Local model with PyTorch/CUDA
- **`test_trans_ollama.py`**: Ollama API integration

### Integration Tests

Integration tests verify complete workflows:

- **`test_main.py`**: Main entry point routing and error handling
- **`test_translation_flow.py`**: End-to-end translation scenarios

### Performance Tests

Performance tests ensure efficiency and scalability:

- **`test_batch_processing.py`**: 
  - Large file processing (1000+ entries)
  - Memory usage monitoring
  - Batch size optimization
  - Concurrent file processing
  - Error recovery performance

## Key Test Scenarios

### 1. Translation Engines

Each engine is tested for:
- Correct initialization
- API key handling
- Translation accuracy
- Error handling
- Batch processing (local model)

### 2. Special Content Handling

- **URLs**: Preserved in reStructuredText format (`` `text <url>`_ ``)
- **Emails**: Detection prevents translation
- **Unicode**: Full UTF-8 support
- **Multiline**: Preserved formatting

### 3. File Operations

- Missing files raise appropriate errors
- Partial translations can resume
- Overwrite mode retranslates existing entries
- File permissions and encoding preserved

### 4. Performance Benchmarks

- **Throughput**: >100 entries/second (mocked API)
- **Memory**: <100MB increase for 500 entries
- **Batch Size**: Optimal 16-item batches for local model
- **Concurrency**: Thread-safe file processing

## Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def temp_po_file()          # Basic PO file with test entries
def temp_po_file_with_urls() # PO file with URL entries
def temp_po_file_with_emails() # PO file with email entries
def empty_po_file()          # Empty PO file
def malformed_po_file()      # Invalid PO format

def mock_libretranslate_api() # Mock LibreTranslate API
def mock_ollama_client()      # Mock Ollama client
def mock_torch_cuda_available() # Mock CUDA availability
def mock_transformers()       # Mock transformer models

def sample_args()            # Default argument namespace
def sample_args_ollama()     # Ollama-specific args
def sample_args_local()      # Local model args
```

## Test Markers

Pytest markers for test categorization:

```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.performance    # Performance tests
@pytest.mark.e2e           # End-to-end tests
@pytest.mark.slow          # Slow running tests
@pytest.mark.requires_cuda  # Tests requiring CUDA/GPU
@pytest.mark.requires_network # Tests requiring network
```

## Coverage Requirements

- **Minimum Coverage**: 80% (enforced in pytest.ini)
- **Core Modules**: 90%+ coverage target
- **Error Paths**: 85%+ coverage target

View coverage report:
```bash
make test-coverage
# HTML report in htmlcov/index.html
```

## Continuous Testing

Watch mode for development:
```bash
make test-watch  # Requires pytest-watch
```

Re-run only failed tests:
```bash
make test-failed
```

## Best Practices

1. **Isolation**: Each test is independent with proper setup/teardown
2. **Mocking**: External dependencies are mocked to ensure fast, reliable tests
3. **Fixtures**: Reusable test data and mocks via pytest fixtures
4. **Clear Names**: Test names clearly describe what they test
5. **Assertions**: Specific assertions with helpful error messages
6. **Performance**: Tests run quickly (<10s for unit tests)
7. **Documentation**: Each test includes docstring explaining purpose

## Adding New Tests

1. Choose appropriate directory (unit/integration/performance)
2. Follow naming convention: `test_<module_name>.py`
3. Use existing fixtures from `conftest.py`
4. Add appropriate markers
5. Ensure tests are independent
6. Document complex test scenarios

Example test structure:

```python
import pytest
from unittest.mock import Mock, patch

class TestNewFeature:
    """Test new feature functionality."""
    
    @pytest.mark.unit
    def test_basic_functionality(self, sample_fixture):
        """Test basic feature behavior."""
        # Arrange
        input_data = "test"
        expected = "result"
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected
    
    @pytest.mark.unit
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            function_under_test(invalid_input)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `pip install -e .[test]` was run
2. **CUDA Tests**: Mark with `@pytest.mark.requires_cuda` if GPU needed
3. **Slow Tests**: Mark with `@pytest.mark.slow` for optional execution
4. **Flaky Tests**: Use `pytest-timeout` to prevent hanging

### Debug Options

Verbose output:
```bash
pytest -vv tests/unit/test_specific.py
```

Show print statements:
```bash
pytest -s tests/
```

Drop into debugger on failure:
```bash
pytest --pdb tests/
```

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example for CI configuration
test:
  script:
    - pip install -e .[test]
    - make test-coverage
    - make lint-tests
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Contributing

When contributing tests:

1. Ensure all new code has tests
2. Maintain or improve coverage
3. Follow existing patterns and conventions
4. Update this documentation if adding new test categories
5. Run full test suite before submitting

## License

Tests are part of the TranspoLibre project and follow the same Apache-2.0 license.