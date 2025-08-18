# Momovu Movie Generation Script

## Overview

The `generate_movie.py` script creates an automated demonstration video of momovu's features by:
- Launching momovu with different document types
- Capturing screenshots of various states and features
- Combining screenshots into a WebM video using ffmpeg

## Prerequisites

### Required Software

Install the following tools on Debian/Ubuntu:

```bash
sudo apt-get install xdotool imagemagick wmctrl ffmpeg
```

- **xdotool**: Window management and keyboard automation
- **imagemagick**: Window-specific screenshot capture
- **wmctrl**: Additional window management
- **ffmpeg**: Video generation with VP9 codec

### Required Files

Ensure these sample PDF files exist in the `samples/` directory:
- `vatican-dustjacket.pdf`
- `bovary-cover.pdf`
- `pingouins-interior.pdf`

## Usage

### Basic Usage

Generate a movie with default settings:
```bash
./generate_movie.py
```

This creates `momovu_demo.webm` with 2 seconds per screenshot.

### Command-Line Options

```
-o, --output PATH       Output video file (default: momovu_demo.webm)
-t, --temp-dir PATH     Temporary directory for screenshots (default: auto-generated)
-d, --delay SECONDS     Delay between frames in seconds (default: 2.0)
--crf VALUE            Video quality CRF 0-63, lower is better (default: 30)
--preset PRESET        FFmpeg encoding preset (default: medium)
--keep-temp            Keep temporary screenshot files after completion
--dry-run              Show what would be done without executing
-v, --verbose          Enable verbose logging
```

### Examples

```bash
# Custom output file and 3 seconds per frame
./generate_movie.py -o demo.webm -d 3.0

# Higher quality video (CRF 20)
./generate_movie.py --crf 20

# Keep screenshots for inspection
./generate_movie.py --keep-temp

# See what would be done
./generate_movie.py --dry-run

# Verbose output for debugging
./generate_movie.py -v
```

## Demo Sequence

The script executes 103 actions to capture 40 screenshots:

### Part 1: Vatican Dustjacket (7 screenshots)
1. Launch with dustjacket document
2. Fit page to window
3. Enter presentation mode
4. Toggle overlays: margins, trim lines, barcode, fold lines

### Part 2: Bovary Cover (7 screenshots)
1. Open cover PDF
2. Change document type to Cover
3. Fit page and enter presentation mode
4. Toggle overlays
5. Set page count to 688

### Part 3: Pingouins Interior (26 screenshots)
1. Open interior PDF
2. Change document type to Interior
3. Navigate pages 1-10 (10 screenshots)
4. Enable side-by-side view
5. Advance 10 more pages (10 screenshots)
6. Enter presentation mode via menu
7. Toggle final overlays

## Video Output

The generated WebM video features:
- **Codec**: VP9 (libvpx-vp9)
- **Container**: WebM
- **Frame rate**: 0.5 fps (2 seconds per frame by default)
- **Quality**: CRF 30 (adjustable)
- **Encoding**: 2-pass for optimal quality/size ratio
- **Duration**: ~80 seconds with default settings

## Troubleshooting

### Window Not Found
- Ensure momovu is installed and accessible in PATH
- Check that X11 display is available
- Verify xdotool can find windows: `xdotool search --name Momovu`

### Screenshot Failures
- Verify ImageMagick is installed: `which import`
- Check window permissions and compositor settings
- Try running with `-v` for detailed error messages

### Video Generation Issues
- Ensure ffmpeg supports VP9: `ffmpeg -codecs | grep vp9`
- Check disk space for temporary files
- Verify write permissions for output directory

### Automation Issues
- Some window managers may interfere with xdotool
- Disable compositor effects if experiencing issues
- Increase wait times if actions execute too quickly

## Technical Details

### Action Types
- **Launch**: Start momovu with specific arguments
- **Screenshot**: Capture window screenshot
- **Keyboard**: Send keyboard shortcuts
- **Menu Navigation**: Navigate menus via Alt+key
- **File Open**: Open files through File dialog
- **Document Type**: Change document type
- **Page Navigation**: Jump to specific pages
- **Wait**: Pause between actions

### File Naming
Screenshots are saved as:
- `frame_0001_label.png` (with label)
- `frame_0001.png` (without label)

Numbers are zero-padded to 4 digits for proper sorting.

### Cleanup
The script automatically:
- Terminates momovu processes on exit
- Removes temporary directories (unless --keep-temp)
- Cleans up ffmpeg log files

## Development

### Adding New Actions
1. Create a new Action subclass
2. Implement the `execute()` method
3. Add to the sequence in `create_complete_demo_sequence()`

### Modifying the Sequence
Edit `create_complete_demo_sequence()` to:
- Change the order of actions
- Add/remove screenshots
- Adjust timing between actions
- Include different PDF files

### Debugging
- Use `--dry-run` to preview actions
- Enable `-v` for verbose logging
- Keep temp files with `--keep-temp`
- Check individual screenshots before video generation