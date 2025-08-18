# Hypothesis Property-Based Testing Integration Plan for Momovu

## Overview

This document outlines a comprehensive plan for integrating Hypothesis, a powerful property-based testing framework, with the existing pytest test suite in the Momovu project. Property-based testing complements traditional example-based testing by automatically generating test cases based on specified properties.

## Table of Contents

1. [Introduction to Property-Based Testing](#introduction)
2. [Benefits for Momovu](#benefits)
3. [Installation and Setup](#installation)
4. [Configuration](#configuration)
5. [Testing Strategy](#strategy)
6. [Best Practices](#best-practices)
7. [Examples by Component](#examples)
8. [Custom Strategies](#custom-strategies)
9. [Integration with CI/CD](#ci-cd)
10. [Team Guidelines](#guidelines)

## 1. Introduction to Property-Based Testing {#introduction}

Property-based testing differs from traditional example-based testing:

- **Example-based**: Test specific inputs and expected outputs
- **Property-based**: Test properties that should hold for all valid inputs

Hypothesis automatically generates test cases, including edge cases you might not think of.

## 2. Benefits for Momovu {#benefits}

### Specific Benefits for PDF Viewer Application

1. **Boundary Testing**: Automatically test edge cases for page navigation, zoom levels, and margin calculations
2. **State Machine Testing**: Verify UI state transitions (fullscreen, presentation mode, view modes)
3. **Data Validation**: Ensure models properly validate all inputs
4. **Rendering Consistency**: Verify rendering calculations remain consistent across different inputs
5. **Memory Safety**: Test with large numbers of pages, extreme zoom levels

### General Benefits

- Finds bugs traditional tests miss
- Reduces test maintenance
- Documents invariants and contracts
- Provides better test coverage with less code

## 3. Installation and Setup {#installation}

### Add to Dependencies

Update `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    # ... existing dependencies ...
    "hypothesis>=6.100.0",
    "hypothesis[pytest]>=6.100.0",
]

test = [
    # ... existing dependencies ...
    "hypothesis>=6.100.0",
    "hypothesis[pytest]>=6.100.0",
]
```

### Install

```bash
pip install -e ".[dev]"
# or
pip install hypothesis[pytest]
```

## 4. Configuration {#configuration}

### Create Hypothesis Settings

Create `tests/hypothesis_settings.py`:

```python
"""Hypothesis settings and profiles for the test suite."""

from hypothesis import settings, Verbosity
from hypothesis import strategies as st

# Define test profiles
settings.register_profile(
    "dev",
    max_examples=100,
    verbosity=Verbosity.verbose,
    deadline=None,  # Disable for development
)

settings.register_profile(
    "ci",
    max_examples=1000,
    verbosity=Verbosity.normal,
    deadline=5000,  # 5 seconds
    suppress_health_check=[],
)

settings.register_profile(
    "debug",
    max_examples=10,
    verbosity=Verbosity.debug,
    deadline=None,
    print_blob=True,
)

# Load profile from environment
import os
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
```

### Update pytest Configuration

Add to `pytest.ini`:

```ini
[pytest]
# ... existing configuration ...

# Hypothesis settings
hypothesis_show_statistics = true

markers =
    # ... existing markers ...
    hypothesis: Property-based tests using Hypothesis
    hypothesis_slow: Slow property-based tests
```

### Add to conftest.py

```python
# In tests/conftest.py
from tests.hypothesis_settings import *  # noqa: F403
```

## 5. Testing Strategy {#strategy}

### Component Testing Priority

1. **Models** (High Priority)
   - Property validation
   - State transitions
   - Data consistency

2. **Presenters** (High Priority)
   - Business logic invariants
   - State management
   - Event handling

3. **Calculations** (High Priority)
   - Margin calculations
   - Page positioning
   - Zoom calculations

4. **Views** (Medium Priority)
   - UI state consistency
   - Event propagation
   - Resource management

### Property Categories

1. **Invariants**: Properties that always hold
2. **Roundtrip**: Encode/decode, serialize/deserialize
3. **Idempotence**: f(f(x)) = f(x)
4. **Commutativity**: Order doesn't matter
5. **Metamorphic**: Relations between different inputs

## 6. Best Practices {#best-practices}

### Do's

1. **Start Simple**: Begin with simple properties, add complexity gradually
2. **Use Composite Strategies**: Build complex inputs from simple ones
3. **Test Invariants**: Focus on properties that should always be true
4. **Shrinking**: Let Hypothesis find minimal failing examples
5. **Stateful Testing**: Use for complex workflows
6. **Profile-Based Testing**: Different settings for dev/CI

### Don'ts

1. **Don't Over-Constrain**: Allow Hypothesis to explore edge cases
2. **Don't Test Implementation**: Test behavior, not how it's done
3. **Don't Ignore Failures**: Hypothesis finds real bugs
4. **Don't Skip Shrinking**: Minimal examples are valuable

### Integration with Existing Tests

```python
# Combine with pytest fixtures
@given(page_count=st.integers(min_value=1, max_value=1000))
def test_document_with_hypothesis(document_model, page_count):
    """Property: Document page count is always non-negative."""
    document_model.page_count = page_count
    assert document_model.page_count > 0
```

## 7. Examples by Component {#examples}

### Model Testing Example

```python
# tests/test_models_hypothesis.py
import hypothesis.strategies as st
from hypothesis import given, assume, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel


class TestDocumentProperties:
    """Property-based tests for Document model."""
    
    @given(
        page_count=st.integers(min_value=0, max_value=10000),
        page_sizes=st.lists(
            st.tuples(
                st.floats(min_value=1.0, max_value=5000.0),
                st.floats(min_value=1.0, max_value=5000.0)
            ),
            min_size=0,
            max_size=100
        )
    )
    def test_document_consistency(self, page_count, page_sizes):
        """Property: Document state remains consistent."""
        doc = Document()
        doc.page_count = page_count
        doc.page_sizes = page_sizes
        
        # Property: page_sizes length should match page_count if provided
        if page_sizes:
            assert len(doc.page_sizes) == len(page_sizes)
        
        # Property: get_page_size returns None for invalid indices
        assert doc.get_page_size(-1) is None
        assert doc.get_page_size(len(page_sizes)) is None


class TestMarginSettingsProperties:
    """Property-based tests for MarginSettingsModel."""
    
    @given(
        margin_mm=st.floats(min_value=0.0, max_value=100.0),
        num_pages=st.integers(min_value=1, max_value=5000)
    )
    def test_margin_validation(self, margin_mm, num_pages):
        """Property: Valid margins are always accepted."""
        model = MarginSettingsModel()
        
        # These should always succeed for valid inputs
        assert model.set_property("safety_margin_mm", margin_mm)
        assert model.set_property("num_pages", num_pages)
        
        # Values should be stored correctly
        assert model.safety_margin_mm == margin_mm
        assert model.num_pages == num_pages
    
    @given(doc_type=st.sampled_from(["interior", "cover", "dustjacket"]))
    def test_document_type_validation(self, doc_type):
        """Property: Valid document types are always accepted."""
        model = MarginSettingsModel()
        assert model.set_property("document_type", doc_type)
        assert model.document_type == doc_type
```

### Presenter Testing Example

```python
# tests/test_presenters_hypothesis.py
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

from momovu.presenters.navigation import NavigationPresenter
from momovu.models.view_state import ViewStateModel


class NavigationStateMachine(RuleBasedStateMachine):
    """Stateful testing for navigation presenter."""
    
    def __init__(self):
        super().__init__()
        self.model = ViewStateModel()
        self.presenter = NavigationPresenter(self.model)
        self.presenter.set_total_pages(100)  # Fixed total for testing
    
    @rule(page=st.integers(min_value=0, max_value=99))
    def navigate_to_page(self, page):
        """Rule: Can navigate to any valid page."""
        self.presenter.go_to_page(page)
    
    @rule()
    def navigate_next(self):
        """Rule: Can navigate to next page."""
        self.presenter.next_page()
    
    @rule()
    def navigate_previous(self):
        """Rule: Can navigate to previous page."""
        self.presenter.previous_page()
    
    @invariant()
    def page_in_bounds(self):
        """Invariant: Current page is always within bounds."""
        current = self.presenter.get_current_page()
        total = self.presenter.get_total_pages()
        assert 0 <= current < total
    
    @invariant()
    def model_sync(self):
        """Invariant: Model and presenter are synchronized."""
        assert self.model.current_page == self.presenter.get_current_page()


# Run the state machine test
TestNavigation = NavigationStateMachine.TestCase
```

### View Component Testing Example

```python
# tests/test_views_hypothesis.py
import hypothesis.strategies as st
from hypothesis import given, assume
from PySide6.QtCore import QRectF

from momovu.views.components.zoom_controller import ZoomController


class TestZoomProperties:
    """Property-based tests for zoom functionality."""
    
    @given(
        zoom_level=st.floats(min_value=0.1, max_value=10.0),
        steps=st.integers(min_value=1, max_value=20)
    )
    def test_zoom_in_out_inverse(self, mock_graphics_view, zoom_level, steps):
        """Property: Zoom in and out are inverse operations."""
        controller = ZoomController(mock_graphics_view, None, None)
        controller.zoom_level = zoom_level
        
        original_zoom = controller.zoom_level
        
        # Zoom in n steps
        for _ in range(steps):
            controller.zoom_in()
        
        # Zoom out n steps
        for _ in range(steps):
            controller.zoom_out()
        
        # Should be back to original (within floating point tolerance)
        assert abs(controller.zoom_level - original_zoom) < 0.01
    
    @given(
        scene_rect=st.builds(
            QRectF,
            st.floats(min_value=-1000, max_value=1000),
            st.floats(min_value=-1000, max_value=1000),
            st.floats(min_value=1, max_value=5000),
            st.floats(min_value=1, max_value=5000)
        )
    )
    def test_fit_to_page_bounds(self, mock_graphics_view, scene_rect):
        """Property: Fit to page keeps content visible."""
        controller = ZoomController(mock_graphics_view, None, None)
        
        # Mock scene bounds
        mock_graphics_view.scene().itemsBoundingRect.return_value = scene_rect
        
        controller.fit_to_page()
        
        # Property: Zoom level should be positive
        assert controller.zoom_level > 0
        
        # Property: Should fit within reasonable bounds
        assert 0.01 <= controller.zoom_level <= 100
```

## 8. Custom Strategies {#custom-strategies}

Create `tests/hypothesis_strategies.py`:

```python
"""Custom Hypothesis strategies for Momovu types."""

import hypothesis.strategies as st
from hypothesis import assume

# Page dimensions strategy (in points)
page_dimensions = st.tuples(
    st.floats(min_value=72.0, max_value=7200.0),  # 1 inch to 100 inches
    st.floats(min_value=72.0, max_value=7200.0)
)

# Document type strategy
document_types = st.sampled_from(["interior", "cover", "dustjacket"])

# Valid file paths
@st.composite
def pdf_file_paths(draw):
    """Generate valid PDF file paths."""
    name = draw(st.text(
        alphabet=st.characters(blacklist_categories=["Cc", "Cs"]),
        min_size=1,
        max_size=50
    ))
    return f"/test/path/{name}.pdf"

# Page ranges
@st.composite
def page_ranges(draw, max_pages=1000):
    """Generate valid page ranges."""
    total = draw(st.integers(min_value=1, max_value=max_pages))
    current = draw(st.integers(min_value=0, max_value=total-1))
    return current, total

# Margin settings
@st.composite
def margin_settings(draw):
    """Generate valid margin settings."""
    return {
        "document_type": draw(document_types),
        "num_pages": draw(st.integers(min_value=1, max_value=5000)),
        "safety_margin_mm": draw(st.floats(min_value=0.0, max_value=50.0)),
        "spine_width": draw(st.one_of(st.none(), st.floats(min_value=0.0, max_value=100.0))),
        "show_margins": draw(st.booleans()),
        "show_trim_lines": draw(st.booleans()),
    }

# View states
@st.composite
def view_states(draw):
    """Generate valid view states."""
    return {
        "current_page": draw(st.integers(min_value=0)),
        "view_mode": draw(st.sampled_from(["single", "side_by_side"])),
        "zoom_level": draw(st.floats(min_value=0.1, max_value=10.0)),
        "is_fullscreen": draw(st.booleans()),
        "is_presentation": draw(st.booleans()),
    }
```

## 9. Integration with CI/CD {#ci-cd}

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -e ".[test]"
    
    - name: Run property-based tests
      env:
        HYPOTHESIS_PROFILE: ci
      run: |
        pytest -v -m hypothesis --hypothesis-show-statistics
    
    - name: Run all tests with coverage
      run: |
        pytest --cov=src/momovu --cov-report=xml
```

### Makefile Integration

```makefile
# Add to Makefile
.PHONY: test-hypothesis
test-hypothesis:
	HYPOTHESIS_PROFILE=dev pytest -v -m hypothesis

.PHONY: test-hypothesis-debug
test-hypothesis-debug:
	HYPOTHESIS_PROFILE=debug pytest -v -m hypothesis -s

.PHONY: test-hypothesis-ci
test-hypothesis-ci:
	HYPOTHESIS_PROFILE=ci pytest -v -m hypothesis --hypothesis-show-statistics
```

## 10. Team Guidelines {#guidelines}

### When to Use Property-Based Testing

**Use for:**
- Mathematical properties (calculations, transformations)
- Data validation and parsing
- State machine behavior
- Invariants that should always hold
- Round-trip operations (serialize/deserialize)

**Don't use for:**
- UI layout specifics
- External API calls
- Performance requirements
- Specific business rules with many exceptions

### Writing Good Properties

1. **Think in Properties, Not Examples**
   ```python
   # Bad: Testing specific example
   def test_margin_calculation():
       assert calculate_margin(100) == 36.0
   
   # Good: Testing property
   @given(pages=st.integers(min_value=1))
   def test_margin_positive(pages):
       assert calculate_margin(pages) >= 0
   ```

2. **Use Meaningful Strategies**
   ```python
   # Bad: Too broad
   @given(st.text())
   def test_document_type(doc_type):
       # Will fail on invalid types
   
   # Good: Constrained to valid values
   @given(st.sampled_from(["interior", "cover", "dustjacket"]))
   def test_document_type(doc_type):
       # Only tests valid types
   ```

3. **Let Hypothesis Find Edge Cases**
   ```python
   # Don't over-constrain
   @given(st.floats(min_value=0.0))  # Let it find infinity, NaN
   def test_zoom_level(zoom):
       # Handle edge cases properly
       assume(not math.isnan(zoom) and not math.isinf(zoom))
   ```

### Debugging Failed Properties

1. **Use the Hypothesis Database**
   - Failed examples are saved in `.hypothesis/examples/`
   - Re-run to reproduce failures

2. **Examine Shrunken Examples**
   - Hypothesis finds minimal failing cases
   - These often reveal the core issue

3. **Use Debug Profile**
   ```bash
   HYPOTHESIS_PROFILE=debug pytest -k test_name -s
   ```

4. **Add More Logging**
   ```python
   @given(...)
   def test_property(value):
       print(f"Testing with: {value}")  # Hypothesis will show minimal case
   ```

### Performance Considerations

1. **Adjust max_examples for Development**
   - Use fewer examples during development
   - Increase for CI/CD

2. **Use assume() Wisely**
   - Filter out invalid inputs early
   - But don't over-filter

3. **Profile Slow Tests**
   ```python
   @settings(deadline=None)  # Disable deadline for slow tests
   @given(...)
   def test_slow_property():
       pass
   ```

### Common Patterns

1. **Stateful Testing for Workflows**
   ```python
   class DocumentWorkflow(RuleBasedStateMachine):
       """Test document lifecycle."""
       
       @rule()
       def load_document(self):
           # Test loading
       
       @rule()
       def modify_document(self):
           # Test modifications
       
       @invariant()
       def document_valid(self):
           # Check validity
   ```

2. **Roundtrip Properties**
   ```python
   @given(margin_settings())
   def test_settings_roundtrip(settings):
       model = MarginSettingsModel()
       # Set all properties
       for key, value in settings.items():
           setattr(model, key, value)
       
       # Export and import
       exported = model.to_dict()
       new_model = MarginSettingsModel.from_dict(exported)
       
       # Should be equivalent
       assert new_model.to_dict() == exported
   ```

3. **Metamorphic Relations**
   ```python
   @given(st.integers(min_value=1, max_value=100))
   def test_page_navigation_metamorphic(pages):
       presenter = NavigationPresenter(ViewStateModel())
       presenter.set_total_pages(pages)
       
       # Property: going to last then previous = pages - 2
       presenter.go_to_last_page()
       presenter.previous_page()
       
       expected = pages - 2 if pages > 1 else 0
       assert presenter.get_current_page() == expected
   ```

## Conclusion

Property-based testing with Hypothesis will significantly improve the robustness of the Momovu application by:

1. Finding edge cases automatically
2. Documenting system invariants
3. Reducing test maintenance
4. Improving confidence in code correctness

Start with simple properties and gradually add more complex stateful tests. Focus on core business logic and calculations first, then expand to other components.

Remember: Property-based tests complement, not replace, example-based tests. Use both for comprehensive coverage.