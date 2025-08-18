"""Page position calculator for determining page locations in the view."""

from typing import Any

from momovu.lib.constants import Y_OFFSET_SPACING
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class PagePositions:
    """Calculates page positions for scrolling and navigation."""

    def __init__(self, document_presenter: Any, navigation_presenter: Any) -> None:
        """Initialize the calculator.

        Args:
            document_presenter: Presenter for document operations
            navigation_presenter: Presenter for navigation operations
        """
        self.document_presenter = document_presenter
        self.navigation_presenter = navigation_presenter
        self.Y_OFFSET_SPACING = Y_OFFSET_SPACING  # Points between pages/pairs

    def calculate_single_page_position(self, page_index: int) -> tuple[float, float]:
        """Find center point of page in vertically stacked layout.

        Args:
            page_index: Zero-based page index

        Returns:
            (x, y) scene coordinates of page center
        """
        y_offset = 0.0

        # Calculate y position by summing heights of previous pages
        for i in range(page_index):
            page_size = self.document_presenter.get_page_size(i)
            if page_size:
                _, page_height = page_size
                y_offset += page_height + self.Y_OFFSET_SPACING

        # Get current page dimensions
        page_size = self.document_presenter.get_page_size(page_index)
        if page_size:
            page_width, page_height = page_size
            center_x = page_width / 2
            center_y = y_offset + page_height / 2
            return center_x, center_y

        return 0.0, 0.0

    def calculate_page_pair_position(self, page_index: int) -> tuple[float, float]:
        """Find center point of page pair containing the given page.

        Book layout: page 1 alone, then pairs (2-3), (4-5), etc.

        Args:
            page_index: Zero-based page index

        Returns:
            (x, y) scene coordinates of pair center
        """
        if page_index == 0:
            # Page 1 is alone at the top on the right
            return self._calculate_first_page_position()
        else:
            # For pages 2+, find which pair contains the current page
            return self._calculate_pair_position(page_index)

    def _calculate_first_page_position(self) -> tuple[float, float]:
        """Get center of page 1 positioned on right side.

        Returns:
            (x, y) coordinates for right-aligned first page
        """
        page_size = self.document_presenter.get_page_size(0)
        if page_size:
            page_width, page_height = page_size
            # Center on page 1 (which is on the right side)
            center_x = page_width + page_width / 2  # Center of right page
            center_y = page_height / 2
            return center_x, center_y

        return 0.0, 0.0

    def _calculate_pair_position(self, page_index: int) -> tuple[float, float]:
        """Find center of the pair containing the given page.

        Args:
            page_index: Page index > 0 (not the first page)

        Returns:
            (x, y) coordinates of the containing pair's center
        """
        y_offset = 0.0

        # Page 1 (index 0) takes first row
        first_size = self.document_presenter.get_page_size(0)
        if first_size:
            _, first_height = first_size
            y_offset = first_height + self.Y_OFFSET_SPACING

        # Determine which pair the current page belongs to
        if page_index % 2 == 1:
            # Odd index (even page number) - this is a left page
            pair_left = page_index
            pair_right = page_index + 1
        else:
            # Even index (odd page number) - this is a right page
            pair_left = page_index - 1
            pair_right = page_index

        # Calculate y position by counting pairs before this one
        y_offset = self._calculate_y_offset_for_pair(pair_left, y_offset)

        # Get dimensions of current pair for centering
        return self._calculate_pair_center(pair_left, pair_right, y_offset)

    def _calculate_y_offset_for_pair(
        self, pair_left: int, initial_offset: float
    ) -> float:
        """Sum heights of all pairs above the target pair.

        Args:
            pair_left: Left page index of target pair
            initial_offset: Y position after page 1

        Returns:
            Total Y offset to reach target pair
        """
        y_offset = initial_offset

        # Pairs start at index 1: (1,2), (3,4), (5,6), etc.
        for i in range(1, pair_left, 2):
            left_size = self.document_presenter.get_page_size(i)
            right_size = (
                self.document_presenter.get_page_size(i + 1)
                if i + 1 < self.navigation_presenter.get_total_pages()
                else None
            )

            if left_size:
                _, left_height = left_size
                pair_height = left_height
                if right_size:
                    _, right_height = right_size
                    pair_height = max(left_height, right_height)
                y_offset += pair_height + self.Y_OFFSET_SPACING

        return y_offset

    def _calculate_pair_center(
        self, pair_left: int, pair_right: int, y_offset: float
    ) -> tuple[float, float]:
        """Find geometric center of two side-by-side pages.

        Args:
            pair_left: Left page index
            pair_right: Right page index (may be beyond document end)
            y_offset: Vertical position of pair top

        Returns:
            (x, y) coordinates at center of combined pages
        """
        left_size = self.document_presenter.get_page_size(pair_left)
        right_size = (
            self.document_presenter.get_page_size(pair_right)
            if pair_right < self.navigation_presenter.get_total_pages()
            else None
        )

        if left_size:
            left_width, left_height = left_size
            total_width = left_width
            pair_height = left_height

            if right_size:
                right_width, right_height = right_size
                total_width += right_width
                pair_height = max(left_height, right_height)

            # Center on the pair (both pages together)
            center_x = total_width / 2
            center_y = y_offset + pair_height / 2
            return center_x, center_y

        return 0.0, 0.0
