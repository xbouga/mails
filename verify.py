#!/usr/bin/env python3
"""
Email Verification Script
Validates email addresses by checking domain, MX records, and SMTP connectivity.
"""

import smtplib
import dns.resolver
import socket
import sys
import os
from datetime import datetime
from collections import defaultdict


class EmailVerificationStats:
    """Track statistics for email verification"""
    
    def __init__(self):
        self.total = 0
        self.valid = 0
        self.invalid_domain = 0
        self.invalid_mx = 0
        self.over_quota = 0
        self.insufficient_storage = 0
        self.other_errors = 0
        
    def print_dashboard(self):
        """Display verification dashboard"""
        print("\n" + "="*60)
        print("EMAIL VERIFICATION DASHBOARD")
        print("="*60)
        print(f"Total Emails Checked:      {self.total}")
        print(f"Valid Emails:              {self.valid}")
        print(f"Invalid Domain:            {self.invalid_domain}")
        print(f"Invalid MX Record:         {self.invalid_mx}")
        print(f"Over Quota:                {self.over_quota}")
        print(f"Insufficient Storage:      {self.insufficient_storage}")
        print(f"Other Errors:              {self.other_errors}")
        print("="*60)
        
        if self.total > 0:
            success_rate = (self.valid / self.total) * 100
            print(f"Success Rate:              {success_rate:.2f}%")
        print("="*60 + "\n")


class EmailVerifier:
    """Email verification with domain, MX, and SMTP checks"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.stats = EmailVerificationStats()
        self.results = {
            'valid': [],
            'invalid_domain': [],
            'invalid_mx': [],
            'over_quota': [],
            'insufficient_storage': [],
            'other_errors': []
        }
        
    def check_domain_exists(self, domain):
        """
        Check if a domain exists by attempting to resolve it
        Returns: (exists: bool, error_message: str)
        """
        try:
            # Try to resolve the domain - checking for any DNS records
            dns.resolver.resolve(domain, 'A')
            return True, None
        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist (NXDOMAIN)"
        except dns.resolver.NoAnswer:
            # Domain exists but no A record, try MX directly
            try:
                dns.resolver.resolve(domain, 'MX')
                return True, None
            except Exception:
                return False, "Domain exists but has no records"
        except dns.resolver.Timeout:
            return False, "DNS query timeout"
        except Exception as e:
            return False, f"DNS resolution error: {str(e)}"
    
    def check_mx_record(self, domain):
        """
        Check if domain has exactly one MX record matching "smtpin.rzone.de"
        Returns: (valid: bool, mx_server: str, error_message: str)
        """
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_list = sorted(mx_records, key=lambda rec: rec.preference)
            
            # Check if there's exactly one MX record
            if len(mx_list) != 1:
                return False, None, f"Domain has {len(mx_list)} MX records, expected exactly 1"
            
            # Get the MX server name
            mx_server = str(mx_list[0].exchange).strip('.').lower()
            
            # Check if it matches the expected server
            if mx_server == "smtpin.rzone.de":
                return True, mx_server, None
            else:
                return False, mx_server, f"MX record '{mx_server}' does not match expected 'smtpin.rzone.de'"
                
        except dns.resolver.NoAnswer:
            return False, None, "No MX records found for domain"
        except dns.resolver.NXDOMAIN:
            return False, None, "Domain does not exist"
        except Exception as e:
            return False, None, f"MX record lookup error: {str(e)}"
    
    def verify_smtp(self, email, mx_server):
        """
        Verify email via SMTP with detection for quota and storage issues
        Returns: (valid: bool, status: str, error_message: str)
        """
        try:
            # Connect to MX server
            server = smtplib.SMTP(timeout=self.timeout)
            server.connect(mx_server)
            server.ehlo("verify.example.com")
            
            # Try MAIL FROM
            code, message = server.mail("verify@example.com")
            if code != 250:
                server.quit()
                return False, "error", f"MAIL FROM rejected: {code} {message.decode()}"
            
            # Try RCPT TO - this is where we get detailed status
            code, message = server.rcpt(email)
            message_str = message.decode().lower()
            
            # Check for over quota conditions
            if code == 552 or 'quota' in message_str or 'over quota' in message_str:
                server.quit()
                return False, "over_quota", f"Mailbox over quota: {code} {message.decode()}"
            
            # Check for insufficient storage conditions
            if code == 452 or 'insufficient' in message_str or 'storage' in message_str or 'disk' in message_str:
                server.quit()
                return False, "insufficient_storage", f"Insufficient storage: {code} {message.decode()}"
            
            # Check if accepted
            if code == 250:
                server.quit()
                return True, "valid", None
            
            # Other rejection
            server.quit()
            return False, "error", f"RCPT TO rejected: {code} {message.decode()}"
            
        except smtplib.SMTPServerDisconnected:
            return False, "error", "Server disconnected"
        except smtplib.SMTPConnectError as e:
            return False, "error", f"Connection error: {str(e)}"
        except socket.timeout:
            return False, "error", "Connection timeout"
        except Exception as e:
            return False, "error", f"SMTP verification error: {str(e)}"
    
    def verify_email(self, email):
        """
        Complete email verification process
        Returns: (valid: bool, status: str, details: str)
        """
        email = email.strip()
        if not email or '@' not in email:
            return False, "error", "Invalid email format"
        
        try:
            local_part, domain = email.split('@', 1)
        except ValueError:
            return False, "error", "Invalid email format"
        
        print(f"\nVerifying: {email}")
        
        # Step 1: Check if domain exists
        print(f"  [1/3] Checking domain existence...")
        domain_exists, error_msg = self.check_domain_exists(domain)
        
        if not domain_exists:
            print(f"  ✗ Domain check failed: {error_msg}")
            self.stats.invalid_domain += 1
            self.results['invalid_domain'].append(email)
            return False, "invalid_domain", error_msg
        
        print(f"  ✓ Domain exists")
        
        # Step 2: Check MX record
        print(f"  [2/3] Checking MX record...")
        mx_valid, mx_server, error_msg = self.check_mx_record(domain)
        
        if not mx_valid:
            print(f"  ✗ MX check failed: {error_msg}")
            self.stats.invalid_mx += 1
            self.results['invalid_mx'].append(email)
            return False, "invalid_mx", error_msg
        
        print(f"  ✓ MX record valid: {mx_server}")
        
        # Step 3: SMTP verification
        print(f"  [3/3] Performing SMTP verification...")
        smtp_valid, status, error_msg = self.verify_smtp(email, mx_server)
        
        if status == "over_quota":
            print(f"  ⚠ Over quota: {error_msg}")
            self.stats.over_quota += 1
            self.results['over_quota'].append(email)
            return False, "over_quota", error_msg
        
        if status == "insufficient_storage":
            print(f"  ⚠ Insufficient storage: {error_msg}")
            self.stats.insufficient_storage += 1
            self.results['insufficient_storage'].append(email)
            return False, "insufficient_storage", error_msg
        
        if not smtp_valid:
            print(f"  ✗ SMTP check failed: {error_msg}")
            self.stats.other_errors += 1
            self.results['other_errors'].append(email)
            return False, "error", error_msg
        
        print(f"  ✓ Email is valid")
        self.stats.valid += 1
        self.results['valid'].append(email)
        return True, "valid", None
    
    def verify_emails_from_file(self, input_file):
        """Verify all emails from a file"""
        print(f"\nReading emails from: {input_file}")
        
        try:
            with open(input_file, 'r') as f:
                emails = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found")
            return
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return
        
        print(f"Found {len(emails)} email(s) to verify\n")
        print("="*60)
        
        self.stats.total = len(emails)
        
        for email in emails:
            self.verify_email(email)
        
        # Display dashboard
        self.stats.print_dashboard()
        
        # Save results to files
        self.save_results()
    
    def save_results(self):
        """Save categorized results to output files"""
        output_dir = "verification_results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_created = []
        
        for category, emails in self.results.items():
            if emails:
                filename = os.path.join(output_dir, f"{category}_{timestamp}.txt")
                with open(filename, 'w') as f:
                    f.write(f"# {category.replace('_', ' ').title()}\n")
                    f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Count: {len(emails)}\n\n")
                    for email in emails:
                        f.write(f"{email}\n")
                files_created.append(filename)
        
        if files_created:
            print("\nResults saved to:")
            for filename in files_created:
                print(f"  - {filename}")
        
        # Also create a summary file
        summary_file = os.path.join(output_dir, f"summary_{timestamp}.txt")
        with open(summary_file, 'w') as f:
            f.write(f"Email Verification Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Total Emails Checked:      {self.stats.total}\n")
            f.write(f"Valid Emails:              {self.stats.valid}\n")
            f.write(f"Invalid Domain:            {self.stats.invalid_domain}\n")
            f.write(f"Invalid MX Record:         {self.stats.invalid_mx}\n")
            f.write(f"Over Quota:                {self.stats.over_quota}\n")
            f.write(f"Insufficient Storage:      {self.stats.insufficient_storage}\n")
            f.write(f"Other Errors:              {self.stats.other_errors}\n\n")
            
            if self.stats.total > 0:
                success_rate = (self.stats.valid / self.stats.total) * 100
                f.write(f"Success Rate:              {success_rate:.2f}%\n")
        
        print(f"  - {summary_file}\n")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python verify.py <email_file>")
        print("\nExample: python verify.py mails.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    verifier = EmailVerifier(timeout=10)
    verifier.verify_emails_from_file(input_file)


if __name__ == "__main__":
    main()
