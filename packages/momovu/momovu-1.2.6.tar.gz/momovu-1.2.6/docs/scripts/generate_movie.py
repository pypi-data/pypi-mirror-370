#!/usr/bin/env python3
"""
Generate a movie from momovu screenshots.

This script automates the process of:
1. Launching momovu with various configurations
2. Taking screenshots of different states and features
3. Combining screenshots into a WebM video using ffmpeg

The script demonstrates momovu's features through an automated sequence:
- Document types: Dustjacket, Cover, and Interior
- Visual overlays: trim lines, safety margins, fold lines, barcode areas
- View modes: single page, side-by-side, presentation mode
- Navigation: page jumping, sequential navigation
- File operations: opening different PDFs, changing document types

Requirements:
- xdotool (for window management and keyboard automation)
- imagemagick (for window-specific screenshots)
- wmctrl (for window management)
- ffmpeg (for video generation)

Install on Debian/Ubuntu:
    sudo apt-get install xdotool imagemagick wmctrl ffmpeg

Usage:
    # Generate movie with default settings (2 seconds per frame)
    ./generate_movie.py

    # Specify output file and frame delay
    ./generate_movie.py -o demo.webm -d 3.0

    # Higher quality video (lower CRF = better quality)
    ./generate_movie.py --crf 20

    # Keep temporary screenshot files for inspection
    ./generate_movie.py --keep-temp

    # Dry run to see what would be done
    ./generate_movie.py --dry-run

The script will:
1. Create a temporary directory for screenshots
2. Execute 103 actions to capture 40 screenshots
3. Generate a WebM video using VP9 codec with 2-pass encoding
4. Clean up temporary files (unless --keep-temp is specified)

Video specifications:
- Codec: VP9 (libvpx-vp9)
- Container: WebM
- Frame rate: Determined by delay (default 0.5 fps for 2s delay)
- Quality: CRF 30 (adjustable with --crf)
- Encoding: 2-pass for optimal quality/size ratio
"""

import argparse
import atexit
import logging
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global list to track running processes for cleanup
running_processes: list[subprocess.Popen[bytes]] = []


# Action Types
class ActionType(Enum):
    """Types of actions that can be performed"""

    LAUNCH = "launch"
    SCREENSHOT = "screenshot"
    KEYBOARD = "keyboard"
    MENU_NAVIGATE = "menu_navigate"
    FILE_OPEN = "file_open"
    DOCUMENT_TYPE = "document_type"
    PAGE_GOTO = "page_goto"
    SET_PAGE_COUNT = "set_page_count"
    WAIT = "wait"
    MOUSE_CLICK = "mouse_click"


@dataclass
class ExecutionContext:
    """Shared context for all actions"""

    window_id: Optional[str] = None
    process: Optional[subprocess.Popen[bytes]] = None
    temp_dir: Optional[Path] = None
    frame_counter: int = 0
    screenshot_delay: float = 2.0  # Default 2 seconds between frames
    progress_tracker: Optional["ProgressTracker"] = None


@dataclass
class Action(ABC):
    """Base class for all actions in the sequence"""

    action_type: ActionType
    description: str

    @abstractmethod
    def execute(self, context: ExecutionContext) -> bool:
        """Execute the action. Returns True on success."""
        pass


@dataclass
class MovieConfig:
    """Configuration for movie generation"""

    output_path: Path = Path("momovu_demo.webm")
    temp_dir: Optional[Path] = None
    frame_delay: float = 2.0
    video_crf: int = 30
    video_preset: str = "medium"
    cleanup_on_exit: bool = True
    verbose: bool = False
    dry_run: bool = False
    keep_temp: bool = False


class ProgressTracker:
    """Track and display progress"""

    def __init__(self, total_actions: int):
        self.total = total_actions
        self.current = 0
        self.start_time = time.time()

    def update(self, description: str) -> None:
        """Update progress"""
        self.current += 1
        elapsed = time.time() - self.start_time

        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: calculating..."

        print(
            f"\r[{self.current}/{self.total}] {description:<50} ({eta_str})",
            end="",
            flush=True,
        )

    def complete(self) -> None:
        """Mark as complete"""
        total_time = time.time() - self.start_time
        print(f"\nCompleted {self.total} actions in {total_time:.1f} seconds")


class CleanupManager:
    """Handles cleanup of resources"""

    def __init__(self) -> None:
        self.temp_dirs: list[Path] = []
        self.processes: list[subprocess.Popen[bytes]] = []

    def register_temp_dir(self, path: Path) -> None:
        """Register a temporary directory for cleanup"""
        self.temp_dirs.append(path)

    def register_process(self, process: subprocess.Popen[bytes]) -> None:
        """Register a process for cleanup"""
        self.processes.append(process)

    def cleanup(self, keep_temp: bool = False) -> None:
        """Clean up all resources"""
        # Terminate processes
        for proc in self.processes:
            if proc.poll() is None:  # Still running
                logger.info(f"Terminating process {proc.pid}")
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing process {proc.pid}")
                    proc.kill()
                    proc.wait()

        # Remove temp directories
        if not keep_temp:
            for temp_dir in self.temp_dirs:
                if temp_dir.exists():
                    logger.info(f"Removing temporary directory: {temp_dir}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            logger.info(
                f"Keeping temporary files in: {', '.join(str(d) for d in self.temp_dirs)}"
            )


# Global cleanup manager
cleanup_manager = CleanupManager()


def cleanup_handler(keep_temp: bool = False) -> None:
    """Handler for cleanup on exit"""
    cleanup_manager.cleanup(keep_temp)


# Window Management Functions (adapted from generate_screenshots.py)
def find_window_id(window_title: str, max_attempts: int = 10) -> Optional[str]:
    """Find window ID by title using xdotool."""
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["xdotool", "search", "--name", window_title],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split("\n")
                # Return the most recent window (last in list)
                return window_ids[-1]

        except subprocess.SubprocessError as e:
            logger.error(f"Error finding window: {e}")

        if attempt < max_attempts - 1:
            time.sleep(0.5)

    return None


def activate_window(window_id: str) -> bool:
    """Activate (focus) a window by ID."""
    try:
        subprocess.run(
            ["xdotool", "windowactivate", window_id], check=True, capture_output=True
        )
        time.sleep(0.2)  # Give window time to activate
        return True
    except subprocess.CalledProcessError:
        return False


def send_keys(keys: list[str], delay: float = 0.5) -> None:
    """Send keyboard shortcuts using xdotool."""
    for key_combo in keys:
        try:
            # xdotool uses + for key combinations
            subprocess.run(
                ["xdotool", "key", key_combo], check=True, capture_output=True
            )
            time.sleep(delay)  # Wait between key combinations
        except subprocess.CalledProcessError as e:
            logger.error(f"Error sending keys '{key_combo}': {e}")


def take_window_screenshot(window_id: str, output_path: Path) -> bool:
    """Take screenshot of specific window using ImageMagick's import."""
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Take screenshot using import
        subprocess.run(
            ["import", "-window", window_id, str(output_path)],
            check=True,
            capture_output=True,
        )

        # Verify file was created
        if output_path.exists():
            logger.info(f"Screenshot saved: {output_path}")
            return True
        else:
            logger.error(f"Screenshot file not created: {output_path}")
            return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Error taking screenshot: {e}")
        return False


# Concrete Action Implementations
@dataclass
class LaunchAction(Action):
    """Launch momovu with specified arguments"""

    command: list[str]
    wait_time: float = 3.0

    def execute(self, context: ExecutionContext) -> bool:
        """Launch momovu and find its window"""
        logger.info(f"Launching: {' '.join(self.command)}")

        try:
            # Launch the process
            proc = subprocess.Popen(self.command)
            context.process = proc
            cleanup_manager.register_process(proc)

            # Wait for window to appear
            logger.info(f"Waiting {self.wait_time}s for window to appear...")
            time.sleep(self.wait_time)

            # Find the window
            window_id = find_window_id("Momovu")
            if not window_id:
                logger.error("Could not find Momovu window")
                return False

            context.window_id = window_id
            logger.info(f"Found Momovu window: {window_id}")

            # Activate the window
            if not activate_window(window_id):
                logger.warning("Could not activate window, continuing anyway")

            return True

        except Exception as e:
            logger.error(f"Error launching momovu: {e}")
            return False


@dataclass
class ScreenshotAction(Action):
    """Capture a screenshot"""

    label: Optional[str] = None

    def execute(self, context: ExecutionContext) -> bool:
        """Take a screenshot with sequential numbering"""
        if not context.window_id:
            logger.error("No window ID available for screenshot")
            return False

        if not context.temp_dir:
            logger.error("No temporary directory available for screenshot")
            return False

        # Generate filename
        context.frame_counter += 1
        if self.label:
            filename = f"frame_{context.frame_counter:04d}_{self.label}.png"
        else:
            filename = f"frame_{context.frame_counter:04d}.png"

        output_path = context.temp_dir / filename

        # Take the screenshot
        return take_window_screenshot(context.window_id, output_path)


@dataclass
class WaitAction(Action):
    """Wait for specified duration"""

    duration: float

    def execute(self, context: ExecutionContext) -> bool:
        """Simply wait for the specified duration"""
        logger.debug(f"Waiting for {self.duration}s")
        time.sleep(self.duration)
        return True


@dataclass
class KeyboardAction(Action):
    """Send keyboard shortcuts"""

    keys: list[str]
    wait_after: float = 0.5

    def execute(self, context: ExecutionContext) -> bool:
        """Send keyboard shortcuts"""
        if not context.window_id:
            logger.error("No window ID available for keyboard action")
            return False

        # Ensure window is active
        activate_window(context.window_id)

        # Send the keys
        send_keys(self.keys, delay=self.wait_after)
        return True


@dataclass
class PageGotoAction(Action):
    """Navigate to specific page"""

    page_number: int

    def execute(self, context: ExecutionContext) -> bool:
        """Navigate to a specific page using Ctrl+G dialog"""
        if not context.window_id:
            logger.error("No window ID available for page navigation")
            return False

        try:
            # Activate window
            activate_window(context.window_id)

            # Open goto page dialog
            subprocess.run(
                ["xdotool", "key", "ctrl+g"], check=True, capture_output=True
            )
            time.sleep(1.0)  # Wait for dialog to fully open

            # Clear existing text with triple-click to select all
            subprocess.run(
                ["xdotool", "click", "--repeat", "3", "1"],
                check=True,
                capture_output=True,
            )
            time.sleep(0.2)

            # Type the page number
            subprocess.run(
                ["xdotool", "type", str(self.page_number)],
                check=True,
                capture_output=True,
            )
            time.sleep(0.3)

            # Press Enter to navigate
            subprocess.run(
                ["xdotool", "key", "Return"], check=True, capture_output=True
            )
            time.sleep(1.5)  # Wait for page to load

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error navigating to page {self.page_number}: {e}")
            return False


# Placeholder action classes for future implementation
@dataclass
class MenuNavigateAction(Action):
    """Navigate through menus"""

    menu_path: list[str]

    def execute(self, context: ExecutionContext) -> bool:
        """Navigate through menu items"""
        if not context.window_id:
            logger.error("No window ID available for menu navigation")
            return False

        try:
            # Activate window
            activate_window(context.window_id)
            time.sleep(0.2)

            # For menu navigation, we use Alt+first letter of menu
            # Then navigate with arrow keys or letters
            if len(self.menu_path) >= 1:
                # Open first menu (e.g., "View" -> Alt+V)
                first_menu = self.menu_path[0].lower()
                first_letter = first_menu[0]

                # Special handling for common menus
                menu_keys = {
                    "file": "alt+f",
                    "view": "alt+v",
                    "document": "alt+d",
                    "help": "alt+h",
                }

                menu_key = menu_keys.get(first_menu, f"alt+{first_letter}")
                subprocess.run(
                    ["xdotool", "key", menu_key], check=True, capture_output=True
                )
                time.sleep(0.5)

                # Navigate to submenu items
                if len(self.menu_path) > 1:
                    # For "Presentation Mode", just press 'p'
                    if self.menu_path[1].lower() == "presentation mode":
                        subprocess.run(
                            ["xdotool", "key", "p"], check=True, capture_output=True
                        )
                    else:
                        # For other items, use first letter
                        item_letter = self.menu_path[1].lower()[0]
                        subprocess.run(
                            ["xdotool", "key", item_letter],
                            check=True,
                            capture_output=True,
                        )
                    time.sleep(0.5)

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error navigating menu {' -> '.join(self.menu_path)}: {e}")
            return False


@dataclass
class FileOpenAction(Action):
    """Open a file through File dialog"""

    file_path: str

    def execute(self, context: ExecutionContext) -> bool:
        """Open a file via File menu"""
        if not context.window_id:
            logger.error("No window ID available for file open")
            return False

        try:
            # Activate window
            activate_window(context.window_id)

            # Open File menu
            subprocess.run(["xdotool", "key", "alt+f"], check=True, capture_output=True)
            time.sleep(0.5)

            # Select Open (usually 'o')
            subprocess.run(["xdotool", "key", "o"], check=True, capture_output=True)
            time.sleep(1.0)  # Wait for dialog

            # Clear any existing text and type the file path
            subprocess.run(
                ["xdotool", "key", "ctrl+a"], check=True, capture_output=True
            )
            time.sleep(0.2)

            # Type the full path
            full_path = Path(self.file_path).absolute()
            subprocess.run(
                ["xdotool", "type", str(full_path)], check=True, capture_output=True
            )
            time.sleep(0.5)

            # Press Enter to open
            subprocess.run(
                ["xdotool", "key", "Return"], check=True, capture_output=True
            )
            time.sleep(2.0)  # Wait for file to load

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error opening file {self.file_path}: {e}")
            return False


@dataclass
class DocumentTypeAction(Action):
    """Change document type via menu"""

    document_type: str  # "Cover", "Interior", "Dustjacket"

    def execute(self, context: ExecutionContext) -> bool:
        """Change document type"""
        if not context.window_id:
            logger.error("No window ID available for document type change")
            return False

        try:
            # Activate window
            activate_window(context.window_id)

            # Open Document menu
            subprocess.run(["xdotool", "key", "alt+d"], check=True, capture_output=True)
            time.sleep(0.5)

            # Select document type by first letter
            type_keys = {"cover": "c", "interior": "i", "dustjacket": "d"}

            key = type_keys.get(
                self.document_type.lower(), self.document_type.lower()[0]
            )
            subprocess.run(["xdotool", "key", key], check=True, capture_output=True)
            time.sleep(1.0)  # Wait for change to apply

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error changing document type to {self.document_type}: {e}")
            return False


@dataclass
class SetPageCountAction(Action):
    """Set the page count in the toolbar"""

    page_count: int

    def execute(self, context: ExecutionContext) -> bool:
        """Set page count in the Pages field"""
        if not context.window_id:
            logger.error("No window ID available for page count setting")
            return False

        try:
            # Activate window
            activate_window(context.window_id)

            # Click on the page count field (this would need coordinates)
            # For now, we'll use Tab navigation to reach it
            # This is application-specific and may need adjustment

            # Try using keyboard shortcut if available
            # Otherwise, would need to click on specific coordinates
            logger.warning(
                f"Page count setting to {self.page_count} - implementation needs UI coordinates"
            )

            # Placeholder implementation
            # In a real implementation, we'd either:
            # 1. Click on the page count field at known coordinates
            # 2. Use Tab navigation to reach the field
            # 3. Use a keyboard shortcut if available

            return True

        except Exception as e:
            logger.error(f"Error setting page count to {self.page_count}: {e}")
            return False


def create_test_sequence() -> list[Action]:
    """Create a minimal test sequence for debugging"""
    return [
        LaunchAction(
            action_type=ActionType.LAUNCH,
            description="Launch momovu with Vatican dustjacket",
            command=[
                "momovu",
                "-n",
                "442",
                "--document",
                "dustjacket",
                "samples/vatican-dustjacket.pdf",
            ],
            wait_time=3.0,
        ),
        ScreenshotAction(
            action_type=ActionType.SCREENSHOT,
            description="Initial screenshot",
            label="test_initial",
        ),
        KeyboardAction(
            action_type=ActionType.KEYBOARD,
            description="Fit page",
            keys=["ctrl+0"],
            wait_after=1.0,
        ),
        ScreenshotAction(
            action_type=ActionType.SCREENSHOT,
            description="After fit page",
            label="test_fitted",
        ),
        WaitAction(action_type=ActionType.WAIT, description="Final wait", duration=1.0),
    ]


def create_complete_demo_sequence() -> list[Action]:
    """
    Create the complete demo sequence as specified by the user.

    Sequence:
    1. Launch with vatican dustjacket
    2. Fit page and presentation view
    3. Cycle through overlays (ctrl-m, ctrl-l, ctrl-b, ctrl-t)
    4. Open bovary cover
    5. Change to Cover document type
    6. Cycle through overlays
    7. Set page count to 688
    8. Open pingouins interior
    9. Change to Interior document type
    10. Navigate pages 1-10
    11. Enable side-by-side view
    12. Navigate 10 more pages
    13. Enter presentation mode
    14. Final overlay toggles
    """

    actions = []

    # ===== PART 1: Pingouins Dustjacket =====
    actions.extend(
        [
            LaunchAction(
                action_type=ActionType.LAUNCH,
                description="Launch momovu with Pingouins dustjacket",
                command=[
                    "momovu",
                    "-n",
                    "574",
                    "--document",
                    "dustjacket",
                    "samples/pingouins-dustjacket.pdf",
                ],
                wait_time=3.0,
            ),
            # Fit page first before taking screenshot
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Fit page to window",
                keys=["ctrl+0"],
                wait_after=1.0,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins dustjacket - initial view fitted",
                label="01_pingouins_dustjacket_initial",
            ),
            # Enter presentation view
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Enter presentation mode",
                keys=["f5"],
                wait_after=1.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins dustjacket - presentation mode",
                label="02_pingouins_dustjacket_presentation",
            ),
            # Cycle through overlays
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle safety margins",
                keys=["ctrl+m"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins dustjacket - margins toggled",
                label="03_pingouins_dustjacket_margins",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle trim lines",
                keys=["ctrl+l"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins dustjacket - trim lines toggled",
                label="04_pingouins_dustjacket_trim",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle barcode area",
                keys=["ctrl+b"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins dustjacket - barcode toggled",
                label="05_pingouins_dustjacket_barcode",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle fold lines",
                keys=["ctrl+t"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins dustjacket - fold lines toggled",
                label="06_pingouins_dustjacket_fold",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle bleed lines",
                keys=["ctrl+r"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins dustjacket - bleed lines toggled",
                label="07_pingouins_dustjacket_bleed",
            ),
            # Exit presentation mode
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Exit presentation mode",
                keys=["Escape"],
                wait_after=1.0,
            ),
            # Close momovu to prepare for next document
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Close momovu",
                keys=["ctrl+q"],
                wait_after=2.0,
            ),
        ]
    )

    # ===== PART 2: Bovary Cover =====
    actions.extend(
        [
            # Launch momovu with cover document
            LaunchAction(
                action_type=ActionType.LAUNCH,
                description="Launch momovu with Bovary cover",
                command=[
                    "momovu",
                    "-n",
                    "688",
                    "--document",
                    "cover",
                    "samples/bovary-cover.pdf",
                ],
                wait_time=3.0,
            ),
            # Fit page first
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Fit page",
                keys=["ctrl+0"],
                wait_after=1.0,
            ),
            # Take initial screenshot with margins shown by default
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Bovary cover - initial with margins",
                label="08_bovary_cover_initial",
            ),
            # Enter presentation mode
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Enter presentation mode",
                keys=["f5"],
                wait_after=1.5,
            ),
            # Toggle margins off (they start on by default)
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle margins off on cover",
                keys=["ctrl+m"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Bovary cover - margins off",
                label="09_bovary_cover_margins_off",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle trim lines on cover",
                keys=["ctrl+l"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Bovary cover - trim lines",
                label="10_bovary_cover_trim",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle barcode on cover",
                keys=["ctrl+b"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Bovary cover - barcode",
                label="11_bovary_cover_barcode",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle spine lines on cover",
                keys=["ctrl+t"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Bovary cover - spine lines",
                label="12_bovary_cover_spine",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle bleed lines on cover",
                keys=["ctrl+r"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Bovary cover - bleed lines",
                label="13_bovary_cover_bleed",
            ),
            # Exit presentation mode
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Exit presentation mode",
                keys=["Escape"],
                wait_after=1.0,
            ),
            # Close momovu to prepare for next document
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Close momovu",
                keys=["ctrl+q"],
                wait_after=2.0,
            ),
        ]
    )

    # ===== PART 3: Pingouins Interior =====
    actions.extend(
        [
            # Launch momovu with interior document
            LaunchAction(
                action_type=ActionType.LAUNCH,
                description="Launch momovu with Pingouins interior",
                command=[
                    "momovu",
                    "--document",
                    "interior",
                    "samples/pingouins-interior.pdf",
                ],
                wait_time=3.0,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins interior - initial",
                label="14_pingouins_interior_initial",
            ),
            # Fit page
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Fit page",
                keys=["ctrl+0"],
                wait_after=1.0,
            ),
        ]
    )

    # Navigate through pages 3-12 with 1 second intervals
    for page in range(3, 13):
        actions.extend(
            [
                PageGotoAction(
                    action_type=ActionType.PAGE_GOTO,
                    description=f"Go to page {page}",
                    page_number=page,
                ),
                WaitAction(
                    action_type=ActionType.WAIT,
                    description=f"Wait on page {page}",
                    duration=1.0,
                ),
                ScreenshotAction(
                    action_type=ActionType.SCREENSHOT,
                    description=f"Pingouins interior - page {page}",
                    label=f"{12+page}_pingouins_page_{page:02d}",
                ),
            ]
        )

    actions.extend(
        [
            # Enable side-by-side view
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Enable side-by-side view",
                keys=["ctrl+d"],
                wait_after=1.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins interior - side by side",
                label="25_pingouins_side_by_side",
            ),
        ]
    )

    # Advance 10 more pages
    for i in range(10):
        actions.extend(
            [
                KeyboardAction(
                    action_type=ActionType.KEYBOARD,
                    description=f"Next page ({i+1}/10)",
                    keys=["Page_Down"],
                    wait_after=0.5,
                ),
                ScreenshotAction(
                    action_type=ActionType.SCREENSHOT,
                    description=f"Pingouins interior - advancing {i+1}",
                    label=f"{26+i}_pingouins_advancing_{i+1:02d}",
                ),
            ]
        )

    actions.extend(
        [
            # Enter presentation mode via menu
            MenuNavigateAction(
                action_type=ActionType.MENU_NAVIGATE,
                description="Enter presentation mode via menu",
                menu_path=["View", "Presentation Mode"],
            ),
            WaitAction(
                action_type=ActionType.WAIT,
                description="Wait for presentation mode",
                duration=1.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins interior - presentation mode",
                label="36_pingouins_presentation",
            ),
            # Final overlay toggles in presentation mode
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle margins in presentation",
                keys=["ctrl+m"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins interior - presentation margins",
                label="37_pingouins_presentation_margins",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle fold lines in presentation",
                keys=["ctrl+t"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins interior - presentation fold",
                label="38_pingouins_presentation_fold",
            ),
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Toggle trim lines in presentation",
                keys=["ctrl+l"],
                wait_after=0.5,
            ),
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins interior - presentation trim",
                label="39_pingouins_presentation_trim",
            ),
            # Advance one more page
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Advance to next page",
                keys=["Page_Down"],
                wait_after=0.5,
            ),
            # Exit presentation mode
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Exit presentation mode",
                keys=["Escape"],
                wait_after=1.0,
            ),
            # Fit page
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Fit page",
                keys=["ctrl+0"],
                wait_after=0.5,
            ),
            # Enable all overlays for final frame
            KeyboardAction(
                action_type=ActionType.KEYBOARD,
                description="Enable all overlays",
                keys=["ctrl+m", "ctrl+t", "ctrl+l"],
                wait_after=0.2,  # Quick succession
            ),
            # Final screenshot with everything enabled
            ScreenshotAction(
                action_type=ActionType.SCREENSHOT,
                description="Pingouins interior - final with all overlays",
                label="40_pingouins_final_all_overlays",
            ),
            # Final wait
            WaitAction(
                action_type=ActionType.WAIT,
                description="Final wait before closing",
                duration=1.0,
            ),
        ]
    )

    return actions


class MovieGenerator:
    """Main orchestrator class for movie generation"""

    def __init__(self, config: MovieConfig):
        self.config = config
        self.context = ExecutionContext()
        self.actions: list[Action] = []

    def add_action(self, action: Action) -> None:
        """Add action to sequence"""
        self.actions.append(action)

    def execute_sequence(self) -> bool:
        """Execute all actions in sequence"""
        if not self.actions:
            logger.error("No actions to execute")
            return False

        # Set up context
        self.context.temp_dir = self.config.temp_dir
        self.context.screenshot_delay = self.config.frame_delay
        self.context.progress_tracker = ProgressTracker(len(self.actions))

        logger.info(f"Executing {len(self.actions)} actions...")

        success = True
        for _i, action in enumerate(self.actions):
            if self.context.progress_tracker:
                self.context.progress_tracker.update(action.description)

            if not action.execute(self.context):
                logger.error(f"Action failed: {action.description}")
                success = False
                break

        if self.context.progress_tracker:
            self.context.progress_tracker.complete()

        return success

    def generate_video(self) -> bool:
        """Generate video from screenshots"""
        if not self.context.temp_dir or not self.context.temp_dir.exists():
            logger.error("No temporary directory available for video generation")
            return False

        # Get list of screenshots
        screenshots = sorted(self.context.temp_dir.glob("frame_*.png"))
        if not screenshots:
            logger.error("No screenshots found for video generation")
            return False

        logger.info(f"Found {len(screenshots)} screenshots for video generation")

        # Create video generator
        video_gen = VideoGenerator(
            screenshot_dir=self.context.temp_dir,
            output_path=self.config.output_path,
            frame_delay=self.config.frame_delay,
            crf=self.config.video_crf,
            preset=self.config.video_preset,
        )

        return video_gen.encode_video()


class VideoGenerator:
    """Handles ffmpeg video generation"""

    def __init__(
        self,
        screenshot_dir: Path,
        output_path: Path,
        frame_delay: float = 2.0,
        crf: int = 30,
        preset: str = "medium",
    ):
        self.screenshot_dir = screenshot_dir
        self.output_path = output_path
        self.frame_delay = frame_delay
        self.crf = crf
        self.preset = preset
        self.frame_rate = 1.0 / frame_delay  # Convert delay to fps

    def generate_file_list(self) -> Path:
        """Generate ffmpeg concat file listing all screenshots"""
        concat_file = self.screenshot_dir / "concat.txt"

        # Get sorted list of screenshots
        screenshots = sorted(self.screenshot_dir.glob("frame_*.png"))

        with open(concat_file, "w") as f:
            for screenshot in screenshots:
                # Each image is shown for frame_delay seconds
                f.write(f"file '{screenshot.absolute()}'\n")
                f.write(f"duration {self.frame_delay}\n")

            # Add the last image again without duration (ffmpeg requirement)
            if screenshots:
                f.write(f"file '{screenshots[-1].absolute()}'\n")

        return concat_file

    def encode_video(self) -> bool:
        """Two-pass VP9 encoding as specified by user"""
        try:
            # Generate concat file
            concat_file = self.generate_file_list()
            logger.info(f"Generated concat file: {concat_file}")

            # Create temporary output file in /tmp
            temp_output = Path(tempfile.mktemp(suffix=".webm", dir="/tmp"))

            # First pass
            logger.info("Running ffmpeg first pass...")
            cmd_pass1 = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c:v",
                "libvpx-vp9",
                "-crf",
                str(self.crf),
                "-b:v",
                "0",
                "-pass",
                "1",
                "-an",  # No audio
                "-f",
                "null",
                "/dev/null",
            ]

            result = subprocess.run(cmd_pass1, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg first pass failed: {result.stderr}")
                return False

            # Second pass - output to temp file
            logger.info("Running ffmpeg second pass...")
            cmd_pass2 = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c:v",
                "libvpx-vp9",
                "-crf",
                str(self.crf),
                "-b:v",
                "0",
                "-speed",
                "0",
                "-pass",
                "2",
                "-tile-columns",
                "2",
                "-row-mt",
                "1",
                "-threads",
                str(os.cpu_count() or 4),
                "-an",  # No audio
                "-vf",
                "format=yuv420p,hqdn3d=luma_spatial=4.0:chroma_spatial=3.0",
                str(temp_output),
            ]

            result = subprocess.run(cmd_pass2, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg second pass failed: {result.stderr}")
                if temp_output.exists():
                    temp_output.unlink()
                return False

            # Clean up ffmpeg log files
            for log_file in Path(".").glob("ffmpeg2pass-*.log"):
                log_file.unlink()

            # Ensure output directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy from temp to final location
            import shutil

            shutil.copy2(temp_output, self.output_path)
            temp_output.unlink()

            logger.info(f"Video successfully created: {self.output_path}")
            return True

        except Exception as e:
            logger.error(f"Error during video encoding: {e}")
            return False


def setup_cleanup_handlers(keep_temp: bool = False) -> None:
    """Register cleanup handlers for graceful exit"""
    atexit.register(lambda: cleanup_handler(keep_temp))

    def signal_handler(_sig: Any, _frame: Any) -> None:
        cleanup_handler(keep_temp)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def check_dependencies() -> bool:
    """Check if required system tools are available"""
    required_tools = ["xdotool", "import", "wmctrl", "ffmpeg"]
    missing_tools = []

    for tool in required_tools:
        if not shutil.which(tool):
            missing_tools.append(tool)

    if missing_tools:
        logger.error(f"Missing required tools: {', '.join(missing_tools)}")
        logger.error(
            "Install with: sudo apt-get install xdotool imagemagick wmctrl ffmpeg"
        )
        return False

    return True


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Generate a movie from momovu screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Generate movie with default settings
  %(prog)s -o demo.webm       # Specify output file
  %(prog)s -d 3.0             # 3 seconds per frame
  %(prog)s --crf 20           # Higher quality video
  %(prog)s --keep-temp        # Keep screenshot files
  %(prog)s --dry-run          # Show what would be done
        """,
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("momovu_demo.webm"),
        help="Output video file (default: momovu_demo.webm)",
    )

    parser.add_argument(
        "-t",
        "--temp-dir",
        type=Path,
        help="Temporary directory for screenshots (default: auto-generated)",
    )

    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=2.0,
        help="Delay between frames in seconds (default: 2.0)",
    )

    parser.add_argument(
        "--crf",
        type=int,
        default=30,
        help="Video quality CRF value 0-63, lower is better (default: 30)",
    )

    parser.add_argument(
        "--preset",
        choices=[
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ],
        default="medium",
        help="FFmpeg encoding preset (default: medium)",
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary screenshot files after completion",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a minimal test sequence (5 actions, 2 screenshots)",
    )

    return parser


def main() -> int:
    """Main entry point"""
    # Parse command-line arguments
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create configuration
    config = MovieConfig(
        output_path=args.output,
        temp_dir=args.temp_dir,
        frame_delay=args.delay,
        video_crf=args.crf,
        video_preset=args.preset,
        cleanup_on_exit=not args.keep_temp,
        verbose=args.verbose,
        dry_run=args.dry_run,
        keep_temp=args.keep_temp,
    )

    # Setup cleanup handlers
    setup_cleanup_handlers(keep_temp=config.keep_temp)

    # Check dependencies
    if not check_dependencies():
        return 1

    # Show configuration
    logger.info("Movie Generation Configuration:")
    logger.info(f"  Output file: {config.output_path}")
    logger.info(f"  Frame delay: {config.frame_delay}s")
    logger.info(f"  Video quality (CRF): {config.video_crf}")
    logger.info(f"  Encoding preset: {config.video_preset}")
    logger.info(f"  Keep temp files: {config.keep_temp}")

    # Create movie generator
    generator = MovieGenerator(config)

    # Load the action sequence
    logger.info("\nLoading action sequence...")
    if args.test:
        logger.info("Using test sequence (minimal)")
        actions = create_test_sequence()
    else:
        actions = create_complete_demo_sequence()

    for action in actions:
        generator.add_action(action)

    logger.info(f"Loaded {len(actions)} actions")

    if config.dry_run:
        logger.info("\nDRY RUN MODE - No actions will be performed")
        logger.info(
            f"Would create temporary directory: {config.temp_dir or 'auto-generated'}"
        )
        logger.info(f"\nWould execute {len(actions)} actions:")
        for i, action in enumerate(actions, 1):
            logger.info(f"  {i}. {action.description} ({action.action_type.value})")

        # Count screenshots in sequence
        screenshot_count = sum(1 for a in actions if isinstance(a, ScreenshotAction))
        logger.info(f"\nWould capture {screenshot_count} screenshots")
        logger.info("Would generate WebM video using ffmpeg 2-pass encoding")
        return 0

    # Create temporary directory if not specified
    if config.temp_dir is None:
        temp_dir = Path(tempfile.mkdtemp(prefix="momovu_movie_"))
        config.temp_dir = temp_dir
        cleanup_manager.register_temp_dir(temp_dir)
    else:
        config.temp_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"  Temp directory: {config.temp_dir}")

    # Execute the sequence
    logger.info("\nExecuting action sequence...")
    if not generator.execute_sequence():
        logger.error("Failed to execute action sequence")
        return 1

    # Count screenshots
    screenshot_count = len(list(config.temp_dir.glob("frame_*.png")))
    logger.info(f"\nCaptured {screenshot_count} screenshots")

    # Generate video
    if screenshot_count > 0:
        logger.info("\nGenerating video...")
        if not generator.generate_video():
            logger.error("Failed to generate video")
            return 1

        logger.info(f"Video saved to: {config.output_path}")

        # Move video to documentation directory
        docs_video_path = Path("docs/_source/_static") / config.output_path.name
        if docs_video_path.parent.exists():
            logger.info("Moving video to documentation directory...")
            import shutil

            shutil.move(str(config.output_path), str(docs_video_path))
            logger.info(f"Video moved to: {docs_video_path}")
        else:
            logger.warning(
                f"Documentation directory not found: {docs_video_path.parent}"
            )
    else:
        logger.warning("No screenshots captured, skipping video generation")

    return 0


if __name__ == "__main__":
    sys.exit(main())
