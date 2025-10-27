# Email Verification and Sending Tools

This repository contains tools for email verification and bulk email sending.

## Files

- **verify.py** - Email verification script with comprehensive checks
- **send.py** - Bulk email sending script
- **mails.txt** - Input file containing email addresses (one per line)
- **message.html** - HTML template for email messages

## Email Verification Script (verify.py)

The verification script performs comprehensive validation of email addresses with the following checks:

### Features

1. **Domain Existence Check**: Verifies that the email domain exists via DNS lookup
2. **MX Record Validation**: Checks that the domain has exactly one MX record matching "smtpin.rzone.de"
3. **SMTP Verification**: Performs actual SMTP connection to verify mailbox existence
4. **Quota Detection**: Identifies mailboxes that are over quota
5. **Storage Detection**: Detects insufficient storage conditions on mail servers

### Usage

```bash
python3 verify.py <email_file>
```

Example:
```bash
python3 verify.py mails.txt
```

### Verification Process

The script processes emails in the following order:

1. **Domain Check**: First checks if the domain exists
   - If domain doesn't exist, email is categorized as `invalid_domain`
   - Logs: "Domain check failed"

2. **MX Record Check**: Verifies exactly one MX record matches "smtpin.rzone.de"
   - If MX record doesn't match or multiple records exist, email is categorized as `invalid_mx`
   - Logs: "MX check failed"

3. **SMTP Verification**: Connects to mail server to verify mailbox
   - Detects over-quota conditions (SMTP code 552)
   - Detects insufficient storage (SMTP code 452)
   - Valid emails are categorized as `valid`
   - Other errors are categorized as `other_errors`

### Output

The script provides:

1. **Real-time Console Output**: Shows progress for each email being verified
2. **Dashboard**: Displays statistics summary at the end
3. **Categorized Results**: Saves emails to separate files based on verification status:
   - `valid_TIMESTAMP.txt` - Successfully verified emails
   - `invalid_domain_TIMESTAMP.txt` - Emails with non-existent domains
   - `invalid_mx_TIMESTAMP.txt` - Emails with incorrect MX records
   - `over_quota_TIMESTAMP.txt` - Emails with mailboxes over quota
   - `insufficient_storage_TIMESTAMP.txt` - Emails with storage issues
   - `other_errors_TIMESTAMP.txt` - Emails with other verification errors
   - `summary_TIMESTAMP.txt` - Overall statistics summary

All results are saved in the `verification_results/` directory.

### Example Output

```
EMAIL VERIFICATION DASHBOARD
============================================================
Total Emails Checked:      100
Valid Emails:              85
Invalid Domain:            5
Invalid MX Record:         3
Over Quota:                4
Insufficient Storage:      2
Other Errors:              1
============================================================
Success Rate:              85.00%
============================================================
```

## Email Sending Script (send.py)

Bulk email sending script with multi-threading support.

### Usage

Edit the script to configure:
- Sender email and name
- Subject and message
- Input file with recipient emails

Then run:
```bash
python3 send.py
```

## Installation

Install required dependencies:

```bash
pip3 install dnspython
```

## Requirements

- Python 3.6+
- dnspython library

## Notes

- The verification script uses a 10-second timeout for SMTP connections
- Results are timestamped to prevent overwriting previous runs
- The `verification_results/` directory is automatically created if it doesn't exist
- Empty lines and comments in email files are automatically skipped
