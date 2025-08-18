# Momovu Screenshot Generation Script

This script automates the generation of screenshots for the momovu documentation.

## Prerequisites

The script requires Debian/Ubuntu with X11 and the following tools installed:

```bash
sudo apt-get install xdotool imagemagick wmctrl
```

- `xdotool` - For window management and keyboard automation
- `imagemagick` - For taking window-specific screenshots
- `wmctrl` - For window control

## Usage

### Basic Usage

Generate all screenshots:

```bash
./generate_screenshots.py
```

### Options

- `--output-dir PATH` - Specify output directory (default: `docs/_source/_static/screenshots`)
- `--scenarios ID1 ID2 ...` - Capture only specific scenarios
- `--dry-run` - Show what would be done without taking screenshots
- `--verbose` or `-v` - Enable verbose logging

### Examples

```bash
# Dry run to see what will be captured
./generate_screenshots.py --dry-run

# Capture only specific scenarios
./generate_screenshots.py --scenarios basic-usage cover-with-spine

# Verbose output
./generate_screenshots.py --verbose

# Custom output directory
./generate_screenshots.py --output-dir /tmp/screenshots
```

## Available Scenarios

The script captures the following scenarios:

### Basic Usage
- `basic-usage` - Basic momovu window with interior PDF
- `cover-with-spine` - Cover document showing spine width
- `side-by-side` - Interior pages in side-by-side view

### Document Types
- `interior-single` - Interior document in single page view
- `dustjacket` - Dustjacket with flaps and fold lines

### Visual Overlays
- `trim-lines` - Trim lines overlay enabled
- `safety-margins` - Safety margins overlay enabled
- `spine-lines` - Spine/fold lines overlay enabled
- `barcode-area` - Barcode area overlay enabled
- `all-overlays` - All overlays enabled simultaneously

### View Modes
- `presentation-mode` - Presentation mode (fullscreen, no UI)
- `fullscreen-mode` - Fullscreen mode (maximized window)
- `zoomed-in` - Zoomed in view

### Dialogs
- `goto-page-dialog` - Go to Page dialog

## Output

The script generates:
1. PNG screenshots in the output directory
2. A report file (`screenshot_insertion_report.txt`) showing where to insert images in RST files

## RST Integration

After running the script, check `screenshot_insertion_report.txt` for the exact RST directives to add to your documentation. Example:

```rst
.. figure:: _static/screenshots/basic-usage.png
   :align: center
   :alt: Basic momovu window with interior PDF
   :width: 80%

   Basic momovu window with interior PDF
```

## Troubleshooting

1. **"Missing required tools"** - Install the prerequisites listed above
2. **"Could not find Momovu window"** - Ensure momovu is installed and the samples directory exists
3. **Screenshots are black** - Make sure you're running in an X11 session (not Wayland)

## Notes

- The script automatically terminates momovu processes after taking screenshots
- A 3-second delay is used by default to allow windows to fully render
- Keyboard shortcuts are sent with 0.5s delays between them
- All processes are cleaned up on exit (including Ctrl+C)