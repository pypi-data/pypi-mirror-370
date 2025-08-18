# Documentation Generation Scripts

This directory contains scripts used to generate screenshots and videos for the Momovu documentation.

## Scripts

### generate_screenshots.py
Generates individual screenshots of Momovu in various states for use in documentation.

### insert_screenshots.py
Inserts generated screenshots into the Sphinx documentation with proper captions and references.

### generate_movie.py
Creates an automated demo video showcasing all of Momovu's features across different document types.

## Usage

These scripts are intended for documentation maintainers only. They require:
- xdotool, wmctrl, and imagemagick for window automation
- ffmpeg for video generation
- A running X11 display

See individual script documentation for detailed usage instructions.

## Note

These scripts are not part of the Momovu application itself - they are development tools used to maintain the project documentation.