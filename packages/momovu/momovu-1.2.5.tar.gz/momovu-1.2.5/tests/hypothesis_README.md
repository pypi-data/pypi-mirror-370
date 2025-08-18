# Hypothesis Property-Based Testing in Momovu

This directory contains property-based tests using Hypothesis for the Momovu PDF viewer application.

## Overview

Property-based testing complements our traditional example-based tests by automatically generating test cases to find edge cases and ensure our code works correctly for all valid inputs.

## Structure

```
tests/
├── hypothesis_settings.py          # Hypothesis configuration and profiles
├── hypothesis_strategies.py        # Custom strategies for Momovu types
├── test_models_hypothesis.py       # Property tests for models
├── test_presenters_hypothesis.py   # Property tests for presenters
├── test_views_hypothesis.py        # Property tests for views/components
└── hypothesis_README.md           # This file
```

## Quick Start

### Running Tests

```bash
# Run all property-based tests
make test-hypothesis

# Quick tests (fewer examples)
make test-hypothesis-quick

# Debug mode (verbose output)
make test-hypothesis-debug

# CI mode (thorough testing)
make test-hypothesis-ci

# With statistics
make test-hypothesis-stats
```

### Writing New Tests

1. Import what you need:
```python
from hypothesis import given, strategies as st
from tests.hypothesis_strategies import document_types, margin_settings
```

2. Write your test:
```python
@given(margin=st.floats(min_value=0.0, max_value=100.0))
def test_margin_property(self, margin):
    model = MarginSettingsModel()
    model.safety_margin_mm = margin
    assert model.safety_margin_mm == margin
```

## Available Custom Strategies

Our `hypothesis_strategies.py` provides domain-specific strategies:

- **Document Types**: `document_types` - "interior", "cover", "dustjacket"
- **Page Dimensions**: `page_dimensions` - (width, height) tuples
- **Margin Settings**: `margin_settings()` - Complete margin configurations
- **View States**: `view_states()` - Complete view state configurations
- **PDF Paths**: `pdf_file_paths()` - Valid PDF file paths
- **Zoom Levels**: `zoom_levels` - Valid zoom range (0.1 to 10.0)

## Test Categories

### Model Tests (`test_models_hypothesis.py`)
- Property validation
- State consistency
- Boundary conditions
- State machines for complex workflows

### Presenter Tests (`test_presenters_hypothesis.py`)
- Business logic invariants
- Navigation boundaries
- State synchronization
- Error handling

### View Tests (`test_views_hypothesis.py`)
- UI component behavior
- Rendering consistency
- Performance characteristics
- Component integration

## Profiles

We have different profiles for different scenarios:

- **dev** (default): Balanced for development
- **quick**: Fast feedback, fewer examples
- **debug**: Very verbose, minimal examples
- **ci**: Thorough testing for CI
- **performance**: Strict timing requirements

Set profile with: `HYPOTHESIS_PROFILE=profile_name pytest ...`

## Best Practices

1. **Test Properties, Not Examples**: Focus on what should always be true
2. **Use Custom Strategies**: Leverage our domain-specific strategies
3. **Let Hypothesis Explore**: Don't over-constrain inputs
4. **Combine with Fixtures**: Property tests work with pytest fixtures
5. **Document Invariants**: Use property tests to document system invariants

## Documentation

- **Quick Start Guide**: `docs/hypothesis_quick_start_guide.md`
- **Comprehensive Plan**: `docs/hypothesis_testing_plan.md`
- **Official Docs**: https://hypothesis.readthedocs.io/

## Common Commands

```bash
# Run a specific test file
pytest tests/test_models_hypothesis.py -v

# Run a specific test
pytest tests/test_models_hypothesis.py::TestDocumentModelProperties::test_document_consistency -v

# See what Hypothesis is generating
HYPOTHESIS_PROFILE=debug pytest -k test_name -s

# Reproduce a failure
pytest tests/test_models_hypothesis.py::test_that_failed
```

## Tips

1. **Start Simple**: Begin with basic properties and add complexity
2. **Use Examples**: Add `@example()` decorators for specific cases
3. **Check Performance**: Use `@settings(deadline=ms)` for performance tests
4. **Stateful Testing**: Use `RuleBasedStateMachine` for complex workflows
5. **Debug Failures**: Hypothesis provides minimal failing examples

## Integration with CI

Our CI automatically runs property-based tests with the `ci` profile, which uses more examples and stricter settings.

## Contributing

When adding new property-based tests:

1. Add custom strategies to `hypothesis_strategies.py` if needed
2. Group related tests in appropriate test files
3. Use meaningful test names that describe the property
4. Add `@pytest.mark.hypothesis` to new property tests
5. Document complex properties with comments

## Troubleshooting

**Test is too slow**: 
- Use `@settings(deadline=None)` during development
- Reduce `max_examples` in settings
- Simplify strategies

**Too many invalid inputs**:
- Use `assume()` to filter inputs
- Refine your strategies
- Create custom composite strategies

**Can't reproduce failure**:
- Check `.hypothesis/examples/` directory
- Use `@example()` to add the failing case
- Run with `--hypothesis-seed=<seed>` to reproduce

Remember: Property-based tests find bugs that example-based tests miss!