# Momovu Test Suite

This directory contains the comprehensive test suite for the Momovu PDF viewer application, following industry best practices for Python testing.

## Overview

The test suite is designed with the following principles:
- **Comprehensive Coverage**: Tests cover unit, integration, and performance scenarios
- **Maintainable**: Clear organization, reusable fixtures, and minimal duplication
- **Reliable**: Deterministic tests with proper mocking and isolation
- **Fast**: Efficient test execution with parallel capabilities
- **Documented**: Clear test names and comprehensive documentation

## Test Structure

```
tests/
├── conftest.py                     # Shared fixtures and configuration
├── pytest.ini                     # Pytest configuration
├── test_utils.py                   # Test utilities and helpers
├── README.md                       # This documentation
├── test_*_improved.py              # Improved test files following best practices
└── test_*.py                       # Original test files (for comparison)
```

## Test Categories

Tests are organized using pytest markers:

### Core Test Types
- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for component interactions
- `@pytest.mark.slow` - Tests that take longer than 1 second
- `@pytest.mark.gui` - Tests requiring Qt GUI components

### Specialized Test Types
- `@pytest.mark.edge_case` - Edge cases and boundary conditions
- `@pytest.mark.performance` - Performance and benchmark tests
- `@pytest.mark.smoke` - Critical functionality smoke tests
- `@pytest.mark.regression` - Tests for previously fixed bugs

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_viewer_improved.py

# Run specific test class
pytest tests/test_viewer_improved.py::TestPDFViewerInitialization

# Run specific test method
pytest tests/test_viewer_improved.py::TestPDFViewerInitialization::test_viewer_initializes_with_valid_pdf
```

### Filtered Test Execution
```bash
# Run only unit tests
pytest -m unit

# Run only fast tests (exclude slow tests)
pytest -m "not slow"

# Run integration tests but skip GUI tests
pytest -m "integration and not gui"

# Run edge case tests
pytest -m edge_case

# Run performance tests
pytest -m performance
```

### Coverage Reports
```bash
# Run tests with coverage
pytest --cov=src/momovu

# Generate HTML coverage report
pytest --cov=src/momovu --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=src/momovu --cov-report=xml
```

### Parallel Execution
```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run tests on 4 cores
pytest -n 4
```

## Test Fixtures

The test suite provides comprehensive fixtures in [`conftest.py`](conftest.py):

### Application Fixtures
- `qapp` - QApplication instance for GUI tests
- `temp_pdf_file` - Temporary PDF file for testing
- `mock_document` - Mock QPdfDocument with realistic behavior
- `mock_scene` - Mock QGraphicsScene
- `mock_viewer` - Comprehensive mock PDFViewer

### Data Fixtures
- `sample_page_sizes` - Common page size configurations
- `margin_test_data` - Test data for margin calculations
- `test_factory` - Factory for creating test objects
- `margin_conversion_data` - Parametrized margin conversion data
- `page_size_data` - Parametrized page size data

## Test Utilities

The [`test_utils.py`](test_utils.py) module provides:

### Builders and Factories
- `TestDataBuilder` - Fluent interface for building test data
- `MockFactory` - Factory for creating sophisticated mock objects
- `PropertyBasedTestHelper` - Helpers for property-based testing

### Custom Assertions
- `CustomAssertions.assert_rectangles_equal()` - Compare QRectF objects
- `CustomAssertions.assert_margin_conversion_accurate()` - Verify mm to points conversion
- `CustomAssertions.assert_all_items_hidden()` - Verify all items are hidden
- `CustomAssertions.assert_items_positioned_correctly()` - Verify item positioning

### Performance Testing
- `PerformanceTestHelper.measure_time()` - Context manager for timing
- `PerformanceTestHelper.assert_performance_within_limit()` - Performance assertions
- `PerformanceTestHelper.benchmark_operation()` - Benchmarking utilities

### Scenario Generation
- `TestScenarioGenerator.generate_margin_test_scenarios()` - Margin test scenarios
- `TestScenarioGenerator.generate_presentation_test_scenarios()` - Presentation scenarios

## Writing New Tests

### Test Naming Conventions
- Test files: `test_<component>_improved.py`
- Test classes: `Test<Component><Functionality>`
- Test methods: `test_<behavior>_<condition>`

Example:
```python
class TestPDFViewerInitialization:
    def test_viewer_initializes_with_valid_pdf(self):
        """Test that PDFViewer initializes successfully with a valid PDF file."""
        # Test implementation
```

### Test Organization
Organize tests by functionality, not by implementation:

```python
class TestMarginManagerInitialization:
    """Test MarginManager initialization and basic properties."""

class TestMarginManagerProperties:
    """Test margin property management."""

class TestMarginManagerPaintTracking:
    """Test paint tracking functionality."""
```

### Using Fixtures
Leverage fixtures for setup and data:

```python
def test_viewer_loads_pages_correctly(self, mock_viewer, sample_page_sizes):
    """Test that viewer loads pages correctly."""
    # Use fixtures instead of manual setup
```

### Parametrized Tests
Use parametrization for testing multiple scenarios:

```python
@pytest.mark.parametrize("margin_mm,expected_points", [
    (12.7, 36.0),
    (25.4, 72.0),
    (50.8, 144.0),
])
def test_mm_to_points_conversion(self, margin_mm, expected_points):
    """Test millimeter to points conversion accuracy."""
```

### Mocking Best Practices
1. Use `spec` parameter to ensure mock interface compliance
2. Mock at the boundary of your system under test
3. Use realistic return values
4. Verify interactions, not just return values

```python
def test_viewer_delegates_to_managers(self, mock_viewer):
    """Test that viewer properly delegates to its managers."""
    mock_viewer.next_page()
    
    # Verify delegation occurred
    mock_viewer.presentation_manager.next_page.assert_called_once_with(
        mock_viewer.page_manager, mock_viewer.margin_manager
    )
```

## Test Data Management

### Using Test Data Builder
```python
def test_with_complex_data(self):
    """Test using the test data builder."""
    data = (TestDataBuilder()
            .with_page_size(612.0, 792.0)
            .with_margin(12.7)
            .with_spine_dimensions(10.0, 20.0, 30.0)
            .build())
    
    # Use data in test
```

### Property-Based Testing
```python
def test_margin_calculations_with_random_data(self):
    """Test margin calculations with property-based testing."""
    page_sizes = PropertyBasedTestHelper.generate_page_sizes(10)
    margins = PropertyBasedTestHelper.generate_margin_values(10)
    
    for page_size, margin in zip(page_sizes, margins):
        # Test with generated data
```

## Performance Testing

### Basic Performance Assertions
```python
def test_operation_performance(self):
    """Test that operation completes within time limit."""
    def expensive_operation():
        # Some operation
        pass
    
    PerformanceTestHelper.assert_performance_within_limit(
        expensive_operation, max_time=0.1
    )
```

### Benchmarking
```python
@pytest.mark.performance
def test_benchmark_margin_loading(self):
    """Benchmark margin loading performance."""
    def load_margins():
        # Load margins operation
        pass
    
    stats = PerformanceTestHelper.benchmark_operation(
        load_margins, iterations=100
    )
    
    assert stats['avg_time'] < 0.01  # Average should be < 10ms
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
    - name: Run tests
      run: |
        pytest --cov=src/momovu --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Test Dependencies

Required packages for running tests:
```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-qt>=4.2.0
pytest-xdist>=3.0.0  # For parallel execution
pytest-randomly>=3.12.0  # For test order randomization
pytest-timeout>=2.1.0  # For test timeouts
```

## Best Practices Summary

1. **Test Behavior, Not Implementation** - Focus on what the code does, not how
2. **Use Descriptive Names** - Test names should describe the scenario and expected outcome
3. **Keep Tests Independent** - Each test should be able to run in isolation
4. **Use Fixtures for Setup** - Avoid repetitive setup code
5. **Mock External Dependencies** - Keep tests fast and reliable
6. **Test Edge Cases** - Include boundary conditions and error scenarios
7. **Maintain Test Code Quality** - Apply the same standards as production code
8. **Use Appropriate Assertions** - Choose the most specific assertion available
9. **Group Related Tests** - Organize tests by functionality
10. **Document Complex Tests** - Add docstrings for non-obvious test scenarios

## Troubleshooting

### Common Issues

#### Qt Application Errors
If you see Qt-related errors, ensure tests use the `qapp` fixture:
```python
def test_qt_component(self, qapp):
    # Test Qt components here
```

#### Mock Assertion Errors
When mock assertions fail, check:
1. Mock was called with expected arguments
2. Mock was called the expected number of times
3. Mock method names are spelled correctly

#### Performance Test Failures
Performance tests may fail on slower systems. Consider:
1. Adjusting time limits for CI environments
2. Using relative performance comparisons
3. Skipping performance tests in certain environments

### Debugging Tests
```bash
# Run with debugging output
pytest -s -vv

# Run single test with debugging
pytest -s -vv tests/test_viewer_improved.py::test_specific_test

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

## Contributing

When adding new tests:
1. Follow the established patterns and conventions
2. Add appropriate markers for test categorization
3. Include docstrings for complex test scenarios
4. Update this documentation if adding new utilities or patterns
5. Ensure tests pass in isolation and as part of the full suite

For questions or suggestions about the test suite, please open an issue or discussion.