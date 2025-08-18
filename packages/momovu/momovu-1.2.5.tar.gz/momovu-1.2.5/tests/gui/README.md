# GUI Tests for Momovu

This directory contains GUI tests that use `pytest-qt` to test the Momovu application with real Qt widgets and user interactions.

## Overview

These tests differ from the unit tests in that they:
- Use real Qt widgets instead of mocks
- Test actual user interactions (clicks, keyboard input, etc.)
- Load real PDF files from the `samples/` directory
- Verify visual rendering and UI state changes
- Run automatically without requiring user input

## Test Categories

### Phase 1: Critical Path Tests (Implemented)

1. **PDF Loading and Rendering** (`test_pdf_loading.py`)
   - Loading different PDF types (interior, cover, dustjacket)
   - Initial rendering verification
   - Sequential loading of multiple PDFs
   - Close and reload functionality
   - Rendering with overlays (margins, trim lines, etc.)

2. **Page Navigation** (`test_navigation.py`)
   - Navigation with toolbar buttons
   - Keyboard navigation (arrows, Page Up/Down, Home/End)
   - Mouse wheel navigation
   - Page number spinbox input
   - Side-by-side view navigation
   - Navigation boundaries testing

3. **Zoom Operations** (`test_zoom.py`)
   - Zoom with toolbar buttons
   - Keyboard shortcuts (Ctrl+Plus/Minus/0)
   - Mouse wheel zoom (Ctrl+wheel)
   - Zoom limits testing
   - Zoom preservation across page changes
   - Zoom interaction with navigation

4. **Document Type Switching** (`test_document_types.py`)
   - Switching between interior, cover, and dustjacket
   - Document-specific overlays (barcode, fold lines, etc.)
   - Num pages spinbox for cover/dustjacket
   - Keyboard shortcuts for document types
   - State preservation during type changes

## Running the Tests

The GUI tests integrate seamlessly with the main pytest setup. Simply run pytest as usual:

### Run all tests including GUI:
```bash
pytest
```

### Run only GUI tests:
```bash
pytest -m gui
```

### Run specific GUI test file:
```bash
pytest tests/gui/test_pdf_loading.py -v
```

### Run specific test:
```bash
pytest tests/gui/test_navigation.py::TestPageNavigation::test_navigate_with_toolbar_buttons -v
```

### Run GUI tests excluding slow ones:
```bash
pytest -m "gui and not slow"
```

### Run in headless mode (for CI):
```bash
# Linux/CI environments
QT_QPA_PLATFORM=offscreen pytest -m gui

# Or with xvfb
xvfb-run -a pytest -m gui
```

## Test Fixtures

The GUI tests use several custom fixtures defined in `conftest.py`:

- `main_window`: Creates a clean MainWindow instance
- `main_window_with_pdf`: MainWindow with an interior PDF loaded
- `main_window_with_cover`: MainWindow with a cover PDF loaded
- `main_window_with_dustjacket`: MainWindow with a dustjacket PDF loaded
- `sample_pdf_paths`: Dictionary of paths to sample PDFs
- `gui_helper`: Helper class with utility methods

## Best Practices

1. **No User Input Required**: All tests run automatically without blocking for user input
2. **Use qtbot.wait()**: Add appropriate waits after actions to allow rendering
3. **Verify State**: Always verify both the action succeeded and the UI updated
4. **Clean State**: Each test starts with a fresh MainWindow instance
5. **Real Files**: Tests use actual PDF files from the samples directory
6. **Timeout Protection**: Tests have a 30-second timeout to prevent hanging

## Writing New GUI Tests

When adding new GUI tests:

1. Use the appropriate fixture for your test scenario
2. Use `qtbot` methods for interactions:
   - `qtbot.mouseClick()` for button clicks
   - `qtbot.keyClick()` for keyboard input
   - `qtbot.waitUntil()` for waiting on conditions
   - `qtbot.wait()` for simple delays

3. Use the `gui_helper` for common operations:
   ```python
   def test_example(qtbot, main_window_with_pdf, gui_helper):
       # Get current state
       current_page = gui_helper.get_current_page(main_window_with_pdf)
       
       # Perform action
       main_window_with_pdf.next_page()
       
       # Wait for rendering
       gui_helper.wait_for_render(qtbot, main_window_with_pdf)
       
       # Verify result
       assert gui_helper.get_current_page(main_window_with_pdf) == current_page + 1
   ```

## Troubleshooting

### Tests fail with "could not connect to display"
- Set `QT_QPA_PLATFORM=offscreen` environment variable
- Or use `xvfb-run` on Linux

### Tests are slow
- GUI tests are inherently slower than unit tests
- Run in parallel: `pytest tests/gui/ -n auto`
- Skip slow tests: `pytest tests/gui/ -m "not gui_slow"`

### Tests hang
- Check for missing `qtbot.wait()` after actions
- Ensure no dialogs are blocking (all dialogs should be non-modal in tests)
- Verify the 30-second timeout is working

## CI Integration

For CI environments, ensure:
1. Qt dependencies are installed
2. Virtual display is available (xvfb on Linux)
3. `QT_QPA_PLATFORM=offscreen` is set
4. Sample PDF files are available in the repository

Example GitHub Actions setup:
```yaml
- name: Run GUI tests
  env:
    QT_QPA_PLATFORM: offscreen
  run: |
    pytest tests/gui/ -v --tb=short