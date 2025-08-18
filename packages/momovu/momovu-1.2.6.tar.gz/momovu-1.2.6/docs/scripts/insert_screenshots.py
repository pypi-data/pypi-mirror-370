#!/usr/bin/env python3
"""
Insert screenshot image directives into RST documentation files.

This script reads the screenshot_insertion_report.txt and automatically
inserts the image directives at the specified locations.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_insertion_report(report_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Parse the insertion report to extract insertion instructions."""
    insertions: dict[str, list[dict[str, Any]]] = {}
    current_file = None

    with open(report_path) as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for file header (e.g., "usage.rst:")
        if line.endswith(".rst:"):
            current_file = line[:-1]  # Remove the colon
            insertions[current_file] = []
            i += 2  # Skip the underline
            continue

        # Check for insertion location (e.g., "After line 17 (in section 'Quick Start'):")
        match = re.match(r"After line (\d+) \(in section \'(.+)\'\):", line)
        if match:
            line_number = int(match.group(1))
            section = match.group(2)

            # Collect the RST directive lines
            i += 2  # Skip blank line
            directive_lines = []
            while i < len(lines) and lines[i].strip():
                directive_lines.append(lines[i].rstrip())
                i += 1

            if current_file is not None:
                insertions[current_file].append(
                    {
                        "line": line_number,
                        "section": section,
                        "content": "\n".join(directive_lines),
                    }
                )

        i += 1

    return insertions


def insert_images_in_rst(rst_path: Path, insertions: list[dict[str, Any]]) -> bool:
    """Insert image directives into an RST file at specified locations."""
    # Read the original file
    with open(rst_path) as f:
        lines = f.readlines()

    # Sort insertions by line number in reverse order
    # This ensures we insert from bottom to top, preserving line numbers
    sorted_insertions = sorted(insertions, key=lambda x: x["line"], reverse=True)

    # Insert each image directive
    for insertion in sorted_insertions:
        line_num = insertion["line"]
        content = insertion["content"]

        # Ensure we don't exceed file bounds
        if line_num > len(lines):
            print(f"Warning: Line {line_num} exceeds file length ({len(lines)} lines)")
            continue

        # Insert after the specified line
        # Add blank lines for better formatting
        insert_content = f"\n{content}\n\n"
        lines.insert(line_num, insert_content)

    # Write the modified content back
    with open(rst_path, "w") as f:
        f.writelines(lines)

    return True


def main() -> int:
    """Main entry point."""
    # Paths
    docs_source = Path("docs/_source")
    screenshots_dir = docs_source / "_static" / "screenshots"
    report_path = screenshots_dir / "screenshot_insertion_report.txt"

    if not report_path.exists():
        print(f"Error: Report file not found: {report_path}")
        return 1

    # Parse the insertion report
    print("Parsing insertion report...")
    insertions = parse_insertion_report(report_path)

    # Create backups and insert images
    for rst_file, insertion_list in insertions.items():
        rst_path = docs_source / rst_file

        if not rst_path.exists():
            print(f"Warning: RST file not found: {rst_path}")
            continue

        # Create backup
        backup_path = rst_path.with_suffix(
            f'.rst.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )
        shutil.copy2(rst_path, backup_path)
        print(f"Created backup: {backup_path}")

        # Insert images
        print(f"Inserting {len(insertion_list)} images into {rst_file}...")
        if insert_images_in_rst(rst_path, insertion_list):
            print(f"✓ Successfully updated {rst_file}")
        else:
            print(f"✗ Failed to update {rst_file}")

    print("\nDone! Image directives have been inserted into the documentation.")
    print("Backups of original files have been created with timestamp suffixes.")
    return 0


if __name__ == "__main__":
    exit(main())
