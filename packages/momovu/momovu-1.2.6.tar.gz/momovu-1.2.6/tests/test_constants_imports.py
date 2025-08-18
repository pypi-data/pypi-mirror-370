"""Test that all constants are properly imported from constants.py.

This test ensures that no hardcoded values are used in the codebase
and that all constants are centralized in the constants module.
"""

import ast
import unittest
from pathlib import Path


class TestConstantsImports(unittest.TestCase):
    """Test suite for verifying constants are imported from constants.py."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.src_dir = Path(__file__).parent.parent / "src" / "momovu"
        self.constants_file = self.src_dir / "lib" / "constants.py"

    def test_margin_presenter_imports_constants(self) -> None:
        """Test that MarginPresenter imports all required constants."""
        margin_file = self.src_dir / "presenters" / "margin.py"
        self.assertTrue(margin_file.exists(), f"File not found: {margin_file}")

        with open(margin_file) as f:
            content = f.read()

        # Check that constants are imported
        expected_imports = [
            "DEFAULT_SAFETY_MARGIN_MM",
            "FLAP_HEIGHT_RATIO",
            "FLAP_WIDTH_RATIO",
            "MM_TO_POINTS",
            "SPINE_WIDTH_DIVISOR",
            "SPINE_WIDTH_OFFSET",
        ]

        for constant in expected_imports:
            self.assertIn(
                constant,
                content,
                f"Constant {constant} not imported in margin.py",
            )

        # Check that no hardcoded values exist for these concepts
        hardcoded_patterns = [
            "= 100  # Standard barcode",
            "= 60  # Standard barcode",
            "= 20  # Distance from edges",
            "= 12.7  # 0.5 inches",
            "= 36.0  # 12.7mm in points",
            "= 2.83465  # Conversion factor",
        ]

        for pattern in hardcoded_patterns:
            self.assertNotIn(
                pattern,
                content,
                f"Hardcoded value found in margin.py: {pattern}",
            )

    def test_zoom_controller_imports_viewport_margin(self) -> None:
        """Test that ZoomController imports VIEWPORT_FIT_MARGIN."""
        zoom_controller_file = (
            self.src_dir / "views" / "components" / "zoom_controller.py"
        )
        self.assertTrue(
            zoom_controller_file.exists(), f"File not found: {zoom_controller_file}"
        )

        with open(zoom_controller_file) as f:
            content = f.read()

        # Check that VIEWPORT_FIT_MARGIN is imported
        self.assertIn(
            "VIEWPORT_FIT_MARGIN",
            content,
            "VIEWPORT_FIT_MARGIN not imported in zoom_controller.py",
        )

        # Check that no hardcoded margin = 10 exists in fit_to_page context
        # We'll check for the specific pattern that was replaced
        self.assertNotIn(
            "margin = 10\n",
            content,
            "Hardcoded margin = 10 found in zoom_controller.py",
        )

    def test_constants_file_has_all_required_constants(self) -> None:
        """Test that constants.py contains all required constants."""
        self.assertTrue(
            self.constants_file.exists(), f"File not found: {self.constants_file}"
        )

        with open(self.constants_file) as f:
            content = f.read()

        # Parse the AST to get all constant names
        tree = ast.parse(content)
        constants: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                constants.add(node.target.id)

        # Check that all new constants exist
        required_constants = [
            "VIEWPORT_FIT_MARGIN",
            "MM_TO_POINTS",
            "FLAP_WIDTH_RATIO",
            "FLAP_HEIGHT_RATIO",
        ]

        for constant in required_constants:
            self.assertIn(
                constant,
                constants,
                f"Constant {constant} not found in constants.py",
            )

    def test_no_duplicate_margin_constants_in_presenters(self) -> None:
        """Test that presenters don't define their own margin constants."""
        presenter_dir = self.src_dir / "presenters"

        for presenter_file in presenter_dir.glob("*.py"):
            if presenter_file.name == "__init__.py":
                continue

            with open(presenter_file) as f:
                content = f.read()

            # Parse the AST to check for class-level constants
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    # Check if it's a margin-related constant
                                    name = target.id
                                    if any(
                                        keyword in name.upper()
                                        for keyword in [
                                            "MARGIN",
                                            "SAFETY",
                                            "MM_TO_POINTS",
                                            "BARCODE",
                                        ]
                                    ):
                                        self.fail(
                                            f"Found class-level constant {name} in "
                                            f"{presenter_file.name}. Should be imported "
                                            f"from constants.py instead."
                                        )

    def test_constants_documentation_updated(self) -> None:
        """Test that constants.py documentation mentions new constants."""
        with open(self.constants_file) as f:
            content = f.read()

        # Extract the module docstring
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)

        self.assertIsNotNone(docstring, "No docstring found in constants.py")

        # Check that documentation mentions key concepts
        doc_keywords = [
            "Barcode dimensions",
            "Spine",
            "flap",
            "Measurement conversions",
            "margins",
        ]

        for keyword in doc_keywords:
            self.assertIn(
                keyword.lower(),
                docstring.lower(),
                f"Documentation doesn't mention '{keyword}'",
            )


if __name__ == "__main__":
    unittest.main()
