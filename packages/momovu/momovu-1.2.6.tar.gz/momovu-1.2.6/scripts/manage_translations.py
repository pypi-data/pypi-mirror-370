#!/usr/bin/env python3
"""
Translation management script for Momovu application.

This script handles:
- Extracting translatable strings to .ts files (lupdate)
- Compiling .ts files to .qm files (lrelease)
- Creating new language files
"""

import subprocess
import sys
from pathlib import Path
from typing import List

# Supported languages
LANGUAGES = [
    "ar",  # Arabic
    "bn",  # Bengali
    "de",  # German
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "hi",  # Hindi
    "id",  # Indonesian
    "it",  # Italian
    "ja",  # Japanese
    "ko",  # Korean
    "pl",  # Polish
    "pt",  # Portuguese
    "ru",  # Russian
    "tr",  # Turkish
    "zh",  # Chinese
]

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "momovu"
TRANSLATIONS_DIR = SRC_DIR / "translations"


def get_python_files() -> List[Path]:
    """Get all Python files in the source directory."""
    return list(SRC_DIR.rglob("*.py"))


def update_ts_files():
    """Extract translatable strings from Python files to .ts files."""
    print("Extracting translatable strings...")

    # Ensure translations directory exists
    TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Get all Python source files
    python_files = get_python_files()

    if not python_files:
        print("No Python files found!")
        return

    print(f"Found {len(python_files)} Python files")

    # Update .ts file for each language
    for lang in LANGUAGES:
        ts_file = TRANSLATIONS_DIR / f"momovu_{lang}.ts"
        print(f"Updating {ts_file.name}...")

        # Build lupdate command
        cmd = ["pyside6-lupdate", *[str(f) for f in python_files], "-ts", str(ts_file)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  Warning: lupdate failed for {lang}")
                print(f"  Error: {result.stderr}")
            else:
                print(f"  ✓ Updated {ts_file.name}")
        except FileNotFoundError:
            print("Error: pyside6-lupdate not found. Please install PySide6-tools:")
            print("  pip install PySide6")
            sys.exit(1)


def compile_translations():
    """Compile .ts files to .qm files."""
    print("\nCompiling translations...")

    # Check if any .ts files exist
    ts_files = list(TRANSLATIONS_DIR.glob("momovu_*.ts"))

    if not ts_files:
        print("No .ts files found to compile!")
        return

    # Compile each .ts file
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        print(f"Compiling {ts_file.name} -> {qm_file.name}...")

        cmd = ["pyside6-lrelease", str(ts_file), "-qm", str(qm_file)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  Warning: lrelease failed for {ts_file.name}")
                print(f"  Error: {result.stderr}")
            else:
                print(f"  ✓ Compiled {qm_file.name}")
        except FileNotFoundError:
            print("Error: pyside6-lrelease not found. Please install PySide6-tools:")
            print("  pip install PySide6")
            sys.exit(1)


def create_new_language(lang_code: str):
    """Create a new language .ts file."""
    if lang_code in LANGUAGES:
        print(f"Language {lang_code} already exists")
        return

    ts_file = TRANSLATIONS_DIR / f"momovu_{lang_code}.ts"
    print(f"Creating new language file: {ts_file.name}")

    # Get all Python source files
    python_files = get_python_files()

    # Create new .ts file
    cmd = ["pyside6-lupdate", *[str(f) for f in python_files], "-ts", str(ts_file)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error creating {lang_code}: {result.stderr}")
        else:
            print(f"✓ Created {ts_file.name}")
            print(
                f"Don't forget to add '{lang_code}' to the LANGUAGES list in this script"
            )
    except FileNotFoundError:
        print("Error: pyside6-lupdate not found. Please install PySide6-tools")
        sys.exit(1)


def show_statistics():
    """Show translation statistics for each language."""
    print("\nTranslation Statistics:")
    print("-" * 50)

    for lang in LANGUAGES:
        ts_file = TRANSLATIONS_DIR / f"momovu_{lang}.ts"
        if ts_file.exists():
            # Parse the .ts file to get statistics (simplified)
            content = ts_file.read_text()
            total = content.count("<source>")
            unfinished = content.count('type="unfinished"')
            translated = total - unfinished

            if total > 0:
                percentage = (translated / total) * 100
                print(
                    f"{lang:3} : {translated:4}/{total:4} ({percentage:5.1f}%) translated"
                )
            else:
                print(f"{lang:3} : No strings found")
        else:
            print(f"{lang:3} : File not found")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage translations for Momovu application"
    )
    parser.add_argument(
        "action",
        choices=["update", "compile", "all", "stats", "new"],
        help="Action to perform",
    )
    parser.add_argument(
        "--lang", help="Language code for 'new' action (e.g., 'es' for Spanish)"
    )

    args = parser.parse_args()

    if args.action == "update":
        update_ts_files()
    elif args.action == "compile":
        compile_translations()
    elif args.action == "all":
        update_ts_files()
        compile_translations()
        show_statistics()
    elif args.action == "stats":
        show_statistics()
    elif args.action == "new":
        if not args.lang:
            print("Error: --lang required for 'new' action")
            sys.exit(1)
        create_new_language(args.lang)

    print("\nDone!")


if __name__ == "__main__":
    main()
