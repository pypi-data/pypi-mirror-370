# Hypothesis Quick Start Guide for Momovu Team

## Overview

This guide provides practical instructions for writing and running property-based tests using Hypothesis in the Momovu project. Property-based testing helps us find edge cases and ensure our code works correctly for all valid inputs.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Writing Your First Property Test](#first-test)
3. [Running Hypothesis Tests](#running-tests)
4. [Common Patterns](#common-patterns)
5. [Debugging Failed Tests](#debugging)
6. [Best Practices](#best-practices)
7. [Cheat Sheet](#cheat-sheet)

## Getting Started {#getting-started}

### Installation

Hypothesis is already included in our dev dependencies. To install:

```bash
# Install all dev dependencies
pip install -e ".[dev]"

# Or just Hypothesis
pip install hypothesis[pytest]
```

### Import What You Need

```python
# Basic imports
from hypothesis import given, strategies as st, assume, settings

# For stateful testing
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

# Import our custom strategies
from tests.hypothesis_strategies import (
    document_types, margin_settings, page_dimensions,
    pdf_file_paths, zoom_levels
)
```

## Writing Your First Property Test {#first-test}

### Basic Structure

```python
import hypothesis.strategies as st
from hypothesis import given

class TestMyComponent:
    @given(
        # Define your inputs using strategies
        number=st.integers(min_value=1, max_value=100),
        text=st.text(min_size=1, max_size=50)
    )
    def test_my_property(self, number, text):
        """Test description."""
        # Your test code here
        result = my_function(number, text)
        
        # Assert properties that should always be true
        assert len(result) > 0
        assert result.count(text) <= number
```

### Real Example from Our Codebase

```python
from hypothesis import given
import hypothesis.strategies as st
from momovu.models.margin_settings import MarginSettingsModel

class TestMarginSettings:
    @given(
        margin_mm=st.floats(min_value=0.0, max_value=100.0),
        num_pages=st.integers(min_value=1, max_value=5000)
    )
    def test_valid_margins_accepted(self, margin_mm, num_pages):
        """Valid margins and page counts are always accepted."""
        model = MarginSettingsModel()
        
        # These should always succeed
        assert model.set_property("safety_margin_mm", margin_mm)
        assert model.set_property("num_pages", num_pages)
        
        # Values should be stored correctly
        assert model.safety_margin_mm == margin_mm
        assert model.num_pages == num_pages
```

## Running Hypothesis Tests {#running-tests}

### Command Line

```bash
# Run all Hypothesis tests
pytest -m hypothesis

# Run with verbose output
HYPOTHESIS_PROFILE=dev pytest -v -m hypothesis

# Run a specific test file
pytest tests/test_models_hypothesis.py -v

# Run with statistics
pytest -m hypothesis --hypothesis-show-statistics

# Quick check (fewer examples)
HYPOTHESIS_PROFILE=quick pytest -m hypothesis

# Debug mode (very verbose, few examples)
HYPOTHESIS_PROFILE=debug pytest -k test_name -s
```

### In Your IDE

Most IDEs support running pytest tests directly. Just click the run button next to your test!

### Continuous Integration

Our CI runs with the `ci` profile automatically:

```yaml
env:
  HYPOTHESIS_PROFILE: ci
```

## Common Patterns {#common-patterns}

### 1. Testing Boundaries

```python
@given(page=st.integers())
def test_page_bounds(self, page):
    """Pages are always clamped to valid range."""
    presenter = NavigationPresenter(model)
    presenter.set_total_pages(100)
    
    presenter.go_to_page(page)
    
    # Should always be in bounds
    current = presenter.get_current_page()
    assert 0 <= current < 100
```

### 2. Testing Invariants

```python
@given(operations=st.lists(
    st.sampled_from(["add", "remove", "clear"]),
    min_size=1
))
def test_count_invariant(self, operations):
    """Item count is never negative."""
    collection = MyCollection()
    
    for op in operations:
        if op == "add":
            collection.add_item()
        elif op == "remove":
            collection.remove_item()
        elif op == "clear":
            collection.clear()
    
    # Invariant: count is never negative
    assert collection.count >= 0
```

### 3. Round-Trip Properties

```python
@given(data=margin_settings())
def test_serialization_round_trip(self, data):
    """Data survives serialization/deserialization."""
    original = MarginSettingsModel(**data)
    
    # Serialize and deserialize
    serialized = original.to_dict()
    restored = MarginSettingsModel.from_dict(serialized)
    
    # Should be equivalent
    assert restored.to_dict() == serialized
```

### 4. Using Our Custom Strategies

```python
from tests.hypothesis_strategies import (
    document_types,    # "interior", "cover", "dustjacket"
    page_dimensions,   # (width, height) tuples
    zoom_levels,       # 0.1 to 10.0
    margin_settings,   # Complete margin configurations
)

@given(
    doc_type=document_types,
    pages=page_dimensions
)
def test_with_custom_strategies(self, doc_type, pages):
    """Test using project-specific strategies."""
    # Your test here
```

### 5. Stateful Testing

```python
from hypothesis.stateful import RuleBasedStateMachine, rule

class DocumentStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.doc = Document()
    
    @rule(pages=st.integers(min_value=1, max_value=1000))
    def set_pages(self, pages):
        self.doc.page_count = pages
    
    @rule()
    def clear(self):
        self.doc.clear()
    
    @invariant()
    def pages_non_negative(self):
        assert self.doc.page_count >= 0

# Create the test
TestDocumentStates = DocumentStateMachine.TestCase
```

## Debugging Failed Tests {#debugging}

### 1. Understanding Failures

When a test fails, Hypothesis shows you:
- The minimal failing example
- How to reproduce it

```
Falsifying example: test_my_property(
    self=<test_models_hypothesis.TestMyClass object at 0x...>,
    number=0,  # <-- Minimal failing input
    text='',   # <-- Minimal failing input
)
```

### 2. Reproducing Failures

Failed examples are saved. To reproduce:

```python
# Hypothesis will automatically reproduce the failure
pytest tests/test_models_hypothesis.py::test_my_property
```

### 3. Adding Explicit Examples

```python
from hypothesis import given, example

@given(number=st.integers())
@example(number=0)  # Always test this case
@example(number=-1)  # And this one
def test_with_examples(self, number):
    # Your test
```

### 4. Debugging Strategies

```python
# Print generated values
@given(value=my_strategy)
def test_debug(self, value):
    print(f"Testing with: {value}")
    # Your test

# Use assume() to filter inputs
@given(value=st.floats())
def test_positive_only(self, value):
    assume(value > 0)  # Skip non-positive values
    # Your test
```

## Best Practices {#best-practices}

### DO ✅

1. **Test Properties, Not Examples**
   ```python
   # Good: Tests a property
   @given(items=st.lists(st.integers()))
   def test_sort_property(self, items):
       sorted_items = sorted(items)
       assert all(a <= b for a, b in zip(sorted_items, sorted_items[1:]))
   ```

2. **Use Meaningful Strategies**
   ```python
   # Good: Constrained to valid values
   @given(doc_type=st.sampled_from(["interior", "cover", "dustjacket"]))
   ```

3. **Let Hypothesis Find Edge Cases**
   ```python
   # Good: Allows all valid floats
   @given(zoom=st.floats(min_value=0.1, max_value=10.0))
   ```

4. **Write Clear Assertions**
   ```python
   # Good: Clear what property we're testing
   assert result.page_count >= 0, "Page count must be non-negative"
   ```

### DON'T ❌

1. **Don't Test Implementation Details**
   ```python
   # Bad: Tests internal state
   assert model._internal_counter == 5
   ```

2. **Don't Over-Constrain**
   ```python
   # Bad: Too restrictive
   @given(number=st.integers(min_value=10, max_value=20))
   ```

3. **Don't Ignore Failures**
   ```python
   # Bad: Silencing failures
   try:
       assert something
   except:
       pass  # Don't do this!
   ```

## Cheat Sheet {#cheat-sheet}

### Common Strategies

```python
# Numbers
st.integers(min_value=0, max_value=100)
st.floats(min_value=0.0, max_value=1.0)
st.decimals(min_value=0, max_value=100, places=2)

# Text
st.text(min_size=1, max_size=50)
st.text(alphabet=st.characters(whitelist_categories=["Lu", "Ll"]))
st.from_regex(r"[A-Z][a-z]+")

# Collections
st.lists(st.integers(), min_size=0, max_size=10)
st.sets(st.text(), min_size=1)
st.dictionaries(st.text(), st.integers())

# Choices
st.sampled_from(["option1", "option2", "option3"])
st.one_of(st.none(), st.integers())
st.booleans()

# Composite
@st.composite
def my_composite_strategy(draw):
    size = draw(st.integers(min_value=1, max_value=10))
    elements = draw(st.lists(st.integers(), min_size=size, max_size=size))
    return {"size": size, "elements": elements}
```

### Useful Decorators

```python
# Set deadline (timeout)
@settings(deadline=1000)  # 1 second

# Set number of examples
@settings(max_examples=1000)

# Disable health checks
@settings(suppress_health_check=[HealthCheck.too_slow])

# Combine settings
@settings(max_examples=50, deadline=None)
```

### Project-Specific Strategies

```python
from tests.hypothesis_strategies import (
    # Documents
    document_types,        # "interior", "cover", "dustjacket"
    pdf_file_paths(),      # Valid PDF paths
    page_dimensions,       # (width, height) tuples
    page_ranges(),         # (current, total) tuples
    
    # Margins
    margin_settings(),     # Complete margin configurations
    margin_sizes_mm,       # 0.0 to 100.0 mm
    spine_widths,          # None or 0.0 to 200.0
    
    # View
    view_modes,            # "single", "side_by_side"
    zoom_levels,           # 0.1 to 10.0
    view_states(),         # Complete view state
    
    # Qt
    qrect_like(),          # (x, y, width, height)
    qpoint_like(),         # (x, y)
)
```

## Getting Help

1. **Hypothesis Documentation**: https://hypothesis.readthedocs.io/
2. **Our Examples**: See `tests/test_*_hypothesis.py` files
3. **Team Chat**: Ask in #testing channel
4. **Property-Based Testing Guide**: See `docs/hypothesis_testing_plan.md`

## Quick Wins

Start with these easy property tests:

1. **Validation Tests**: Properties that should always be accepted/rejected
2. **Boundary Tests**: Values at the edges of valid ranges
3. **Invariant Tests**: Things that should never change
4. **Round-Trip Tests**: Serialize/deserialize, encode/decode

Remember: Property-based tests complement regular tests - use both!