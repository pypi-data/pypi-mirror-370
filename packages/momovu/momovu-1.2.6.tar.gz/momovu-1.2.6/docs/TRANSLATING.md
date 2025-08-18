# Translation Guide for Momovu

This guide explains how to manage translations for the Momovu application.

## Overview

Momovu uses Qt's translation system with `.ts` (Translation Source) files that can be processed by automated translation tools like transpolibre.

## Supported Languages

The application currently supports 16 languages:

- Arabic (ar) - RTL support
- Bengali (bn)
- Chinese (zh)
- English (en) - Default
- French (fr)
- German (de)
- Hindi (hi)
- Indonesian (id)
- Italian (it)
- Japanese (ja)
- Korean (ko)
- Polish (pl)
- Portuguese (pt)
- Russian (ru)
- Spanish (es)
- Turkish (tr)

## Directory Structure

```
src/momovu/translations/
├── momovu_ar.ts    # Arabic translation source
├── momovu_bn.ts    # Bengali translation source
├── momovu_de.ts    # German translation source
├── momovu_en.ts    # English (source language)
├── momovu_es.ts    # Spanish translation source
├── momovu_fr.ts    # French translation source
├── momovu_hi.ts    # Hindi translation source
├── momovu_id.ts    # Indonesian translation source
├── momovu_it.ts    # Italian translation source
├── momovu_ja.ts    # Japanese translation source
├── momovu_ko.ts    # Korean translation source
├── momovu_pl.ts    # Polish translation source
├── momovu_pt.ts    # Portuguese translation source
├── momovu_ru.ts    # Russian translation source
├── momovu_tr.ts    # Turkish translation source
└── momovu_zh.ts    # Chinese translation source
```

## Translation Workflow

### 1. Extract Translatable Strings

When you add new translatable strings to the code, extract them to .ts files:

```bash
python scripts/manage_translations.py update
```

This scans all Python files and updates the .ts files with new strings.

### 2. Translate Strings

#### Option A: Using transpolibre (Automated)

The .ts files are in XML format and can be directly processed by transpolibre:

```bash
# Example command (adjust based on transpolibre's actual interface)
transpolibre translate src/momovu/translations/momovu_*.ts
```

#### Option B: Using Qt Linguist (Manual)

Install Qt Linguist and open the .ts files:

```bash
# Install Qt tools if needed
pip install PySide6

# Open a .ts file in Qt Linguist
pyside6-linguist src/momovu/translations/momovu_es.ts
```

#### Option C: Direct XML Editing

The .ts files are XML and can be edited directly. Look for `<translation>` tags:

```xml
<message>
    <source>Open a PDF file</source>
    <translation type="unfinished"></translation>
</message>
```

Change to:

```xml
<message>
    <source>Open a PDF file</source>
    <translation>Abrir un archivo PDF</translation>
</message>
```

### 3. Compile Translations

After translating, compile .ts files to binary .qm files:

```bash
python scripts/manage_translations.py compile
```

### 4. Test Translations

1. Change language in Preferences → Language tab
2. Restart the application
3. Verify all UI elements are translated

## Adding New Translatable Strings

When adding new UI strings in the code:

### For QObject-derived classes:
```python
# Use self.tr() for translatable strings
self.setWindowTitle(self.tr("My Window"))
button.setText(self.tr("Click Me"))
```

### For non-QObject classes:
```python
from PySide6.QtCore import QCoreApplication

# Use QCoreApplication.translate()
text = QCoreApplication.translate("ContextName", "Translatable text")
```

### For dynamic strings with variables:
```python
# Use format() for variable substitution
self.label.setText(self.tr("Page: {current}/{total}").format(
    current=current_page,
    total=total_pages
))
```

### For plural forms:
```python
# Use %n for plural-aware translations
self.label.setText(self.tr("%n page(s)", "", page_count))
```

## Translation Management Script

The `scripts/manage_translations.py` script provides several commands:

```bash
# Extract strings to .ts files
python scripts/manage_translations.py update

# Compile .ts to .qm files
python scripts/manage_translations.py compile

# Do both update and compile
python scripts/manage_translations.py all

# Show translation statistics
python scripts/manage_translations.py stats

# Add a new language (e.g., Swedish)
python scripts/manage_translations.py new --lang sv
```

## Special Considerations

### Right-to-Left Languages (Arabic)

Qt automatically handles RTL layout mirroring for Arabic. Test thoroughly:
- Menu and toolbar layouts
- Page navigation direction
- Text alignment

### CJK Languages (Chinese, Japanese, Korean)

- System fonts are used automatically
- Test for text overflow in UI elements
- Verify character rendering

### Keyboard Shortcuts

Menu accelerators (& markers) should be translated carefully to avoid conflicts:
- `&File` → `&Archivo` (Spanish)
- `&Edit` → `&Édition` (French)

Test that Alt+letter combinations don't conflict within the same menu.

## Testing Checklist

- [ ] All dialogs open without text cutoff
- [ ] Menu items and accelerators work correctly
- [ ] Toolbar tooltips display properly
- [ ] Status bar updates show correctly
- [ ] Number formatting follows locale conventions
- [ ] RTL languages display correctly (Arabic)
- [ ] CJK fonts render properly
- [ ] Preferences dialog saves language selection
- [ ] Application restarts with selected language

## Troubleshooting

### Missing Translations

If strings appear in English despite selecting another language:
1. Check if the string is marked with `tr()` in the code
2. Verify the .ts file contains the translation
3. Ensure .qm files are compiled
4. Check the console for translation loading errors

### Translation Not Loading

Check that:
1. .qm files exist in `src/momovu/translations/`
2. Language code in preferences matches .qm file name
3. Application was restarted after language change

### Adding Context for Translators

Add comments in the code to help translators:

```python
# Translators: This appears in the main window title bar
self.setWindowTitle(self.tr("Momovu"))

# Translators: Status bar text showing current and total pages
self.label.setText(self.tr("Page: {current}/{total}"))
```

## Contributing Translations

1. Fork the repository
2. Update the relevant .ts file
3. Test your translations
4. Submit a pull request

For questions about translations, please open an issue on the project repository.