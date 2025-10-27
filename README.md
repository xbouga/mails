# ADAC Newsletter Generator

A Python script that generates variations of ADAC-style member newsletter emails with multiple spam filter bypass techniques and randomization features.

## Features

- **ADAC Brand Styling**: Authentic yellow/black color scheme
- **Dynamic Content**: Random user data, invoice references, and timestamps
- **Domain Integration**: Uses email domains from `mails.txt`
- **Spam Filter Bypass**: Multiple evasion techniques including:
  - Randomized HTML attributes
  - Invisible honeypot content
  - Whitespace pattern variations
  - Fake email headers as HTML comments
  - Base64 encoded warning text
  - Multiple header layout variations
  - Variable bullet point styles
  - Different logo rendering styles

## Usage

### Basic Usage
```bash
python3 newsletter_generator.py
```

### Make Executable (Optional)
```bash
chmod +x newsletter_generator.py
./newsletter_generator.py
```

## Output

The script generates:
- HTML newsletter file named: `adac_newsletter_{user}_{timestamp}.html`
- Detailed console output with generation status
- Summary report with user details and file information

## Example Output

```
============================================================
ADAC-Style Newsletter Generator
============================================================
[INFO] Newsletter Generator initialized
[INFO] Loaded 100 email domains
[INFO] User login: petra.meyer55
[INFO] Invoice reference: ADAC-20250910-468146
[INFO] Generating ADAC-style newsletter...
[SUCCESS] Newsletter saved as: adac_newsletter_petra.meyer55_20250910_204947.html
============================================================
```

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Files

- `newsletter_generator.py` - Main script
- `mails.txt` - Email domains source file
- Generated HTML files are excluded from git via `.gitignore`

## Note

This tool is intended for testing and educational purposes only. Generated content is clearly marked as test material.