# Bulk Email Sender

A user-friendly, multi-threaded bulk email sending script with progress tracking, validation, and colored output.

## Features

- 🚀 **Multi-threaded sending** - Send emails concurrently with configurable thread count
- 📊 **Progress bar** - Real-time progress tracking with tqdm
- 🎨 **Colored output** - Easy-to-read colored terminal output
- ✅ **Email validation** - Automatic validation of email addresses
- 🔒 **Confirmation prompt** - Interactive confirmation before sending
- 🛠️ **Flexible configuration** - Command-line arguments for all options
- 📝 **Verbose mode** - Detailed logging for debugging
- ⚡ **Batch processing** - Configurable batch sizes for optimal performance

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python send.py
```

This will use the default configuration:
- Email recipients from `mails.txt`
- HTML template from `message.html`
- 150 concurrent threads
- 200 emails per batch

### Custom Configuration

```bash
python send.py --threads 50 --emails recipients.txt --template email.html
```

### Advanced Usage

```bash
python send.py \
  --sender myemail@example.com \
  --sender-name "My Name" \
  --subject "Important Update" \
  --threads 100 \
  --batch-size 50 \
  --verbose
```

## Command-Line Options

### Required Files (with defaults)

- `--emails, -e` - Path to recipient emails file (default: `mails.txt`)
- `--template, -t` - Path to HTML template file (default: `message.html`)

### Email Configuration

- `--sender, -s` - Sender email address
- `--sender-name` - Sender display name
- `--subject` - Email subject line
- `--to-email` - To email address in header (defaults to sender)

### Performance Tuning

- `--threads` - Number of concurrent threads (default: 150)
- `--batch-size` - Emails per batch (default: 200)

### SMTP Configuration

- `--smtp-server` - SMTP server address (default: auto-detect from MX records)
- `--smtp-port` - SMTP server port (default: 25)

### Behavior

- `--verbose, -v` - Enable verbose output for debugging
- `--no-confirm` - Skip confirmation prompt before sending

### Help

- `--help, -h` - Show help message and exit

## Examples

### Send with custom thread count

```bash
python send.py --threads 50
```

### Send to specific recipients with custom sender

```bash
python send.py --emails clients.txt --sender sales@company.com --sender-name "Sales Team"
```

### Debug mode with verbose output

```bash
python send.py --verbose --threads 10 --batch-size 5
```

### Automated sending (no confirmation)

```bash
python send.py --no-confirm --threads 100
```

## File Formats

### Email Recipients File (`mails.txt`)

One email address per line:

```
user1@example.com
user2@example.com
user3@example.com
```

### HTML Template File (`message.html`)

Standard HTML email template:

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Hello!</h1>
  <p>Your message here...</p>
</body>
</html>
```

## Features in Detail

### Email Validation

The script automatically validates all email addresses and:
- Filters out invalid email addresses
- Shows warnings for invalid entries
- Continues with valid emails only

### Progress Tracking

Real-time progress bar showing:
- Number of emails sent
- Percentage complete
- Estimated time remaining
- Elapsed time

### Colored Output

- 🟢 Green - Success messages
- 🔴 Red - Error messages
- 🟡 Yellow - Warnings
- 🔵 Cyan - Information

### Error Handling

The script handles various error conditions:
- Missing files
- Invalid email addresses
- SMTP connection errors
- Invalid sender addresses
- MX record resolution failures

### Confirmation Prompt

Before sending, you'll see:
```
============================================================
Email Sending Confirmation
============================================================
  Sender: user@example.com
  Recipients: 100 email(s)
============================================================

Do you want to proceed? (yes/no):
```

Type `yes` or `y` to proceed, or `no` to cancel.

## Output Summary

After sending, you'll see a summary:

```
============================================================
Email Sending Summary
============================================================
  Total attempted: 100
  Successfully sent: 95
  Failed: 5
============================================================
```

## Security Notes

- The script uses SMTP without authentication by default
- Ensure you have permission to send emails from the sender address
- Be aware of rate limits and anti-spam policies
- Test with small batches first

## Troubleshooting

### "Module not found" errors

Install dependencies:
```bash
pip install -r requirements.txt
```

### "File does not exist" error

Check file paths are correct and files exist:
```bash
ls -la mails.txt message.html
```

### SMTP connection errors

- Verify SMTP server is reachable
- Check firewall/network settings
- Try specifying `--smtp-server` manually
- Use `--verbose` flag for detailed error messages

## License

This project is for educational purposes. Ensure compliance with anti-spam laws and email sending regulations in your jurisdiction.
