#!/usr/bin/env python3
"""
Advanced Newsletter Generator with Anti-Spam Techniques
======================================================

This script generates newsletters with multiple anti-spam techniques to improve
deliverability and bypass spam filters.

Features:
1. Dynamic content generation with randomization
2. Improved email structure and headers
3. HTML encoding and spam trigger avoidance
4. Invisible honeypot fields for bots
5. Content obfuscation techniques
6. Email authentication setup suggestions
7. Image handling improvements
8. Text-to-image ratio optimization
9. Randomized newsletter ID and timestamps
10. IP rotation suggestions
"""

import random
import uuid
import time
import datetime
import re
import html
import base64
import hashlib
import string
from typing import List, Dict, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr, formatdate
import smtplib
import os


class NewsletterGenerator:
    """Advanced newsletter generator with anti-spam techniques."""
    
    def __init__(self, email_list_file: str = "mails.txt"):
        self.email_list_file = email_list_file
        self.spam_trigger_words = [
            "free", "urgent", "act now", "limited time", "guarantee", 
            "money back", "no obligation", "risk free", "call now",
            "click here", "amazing", "incredible", "unbelievable"
        ]
        
        # Content templates with variations
        self.subject_templates = [
            "Updates from {company} - {month} {year}",
            "{company} Newsletter - {season} Edition",
            "What's New at {company}",
            "Your {company} Update",
            "Latest from {company}",
            "{company} Insights - {month}",
            "Monthly Digest from {company}",
            "{company} News & Updates"
        ]
        
        self.content_blocks = [
            {
                "title": "Company Updates",
                "variations": [
                    "We're excited to share some recent developments",
                    "Here are the latest updates from our team",
                    "We wanted to keep you informed about our progress",
                    "Some exciting news to share with you"
                ]
            },
            {
                "title": "Product Features",
                "variations": [
                    "Our latest improvements focus on user experience",
                    "New features designed with your feedback in mind",
                    "Enhanced functionality now available",
                    "Updates that make your workflow smoother"
                ]
            },
            {
                "title": "Community News",
                "variations": [
                    "See what's happening in our community",
                    "Community highlights from this month",
                    "Stories from our valued customers",
                    "Community spotlights and achievements"
                ]
            }
        ]
        
    def load_email_list(self) -> List[str]:
        """Load email addresses from the mails.txt file."""
        try:
            with open(self.email_list_file, 'r', encoding='utf-8') as f:
                emails = []
                for line in f:
                    line = line.strip()
                    if line and '@' in line:
                        # Extract email from format "123.email@domain.com"
                        email_part = line.split('.', 1)
                        if len(email_part) > 1:
                            emails.append(email_part[1])
                        else:
                            emails.append(line)
                return emails
        except FileNotFoundError:
            print(f"Email list file {self.email_list_file} not found.")
            return []
    
    def generate_unique_id(self) -> str:
        """Generate a randomized newsletter ID."""
        timestamp = str(int(time.time()))
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return f"nl-{timestamp}-{random_str}"
    
    def randomize_timestamp(self) -> str:
        """Generate a randomized but realistic timestamp."""
        now = datetime.datetime.now()
        # Add random minutes/seconds to avoid exact timing patterns
        random_minutes = random.randint(-30, 30)
        random_seconds = random.randint(0, 59)
        adjusted_time = now + datetime.timedelta(minutes=random_minutes, seconds=random_seconds)
        return formatdate(time.mktime(adjusted_time.timetuple()), localtime=True)
    
    def obfuscate_text(self, text: str) -> str:
        """Apply content obfuscation techniques."""
        # Replace some characters with HTML entities
        obfuscations = {
            'a': ['a', '&#97;', '&#x61;'],
            'e': ['e', '&#101;', '&#x65;'],
            'i': ['i', '&#105;', '&#x69;'],
            'o': ['o', '&#111;', '&#x6F;'],
            'u': ['u', '&#117;', '&#x75;']
        }
        
        result = text
        for char, options in obfuscations.items():
            if char in result.lower():
                # Randomly replace some instances
                positions = [i for i, c in enumerate(result.lower()) if c == char]
                for pos in random.sample(positions, min(len(positions), max(1, len(positions) // 3))):
                    if pos < len(result):
                        replacement = random.choice(options)
                        result = result[:pos] + replacement + result[pos+1:]
        
        return result
    
    def avoid_spam_triggers(self, text: str) -> str:
        """Replace common spam trigger words with alternatives."""
        alternatives = {
            "free": ["complimentary", "no cost", "included"],
            "urgent": ["important", "timely", "priority"],
            "amazing": ["great", "excellent", "wonderful"],
            "click here": ["visit our site", "learn more", "read further"],
            "guarantee": ["promise", "commitment", "assurance"]
        }
        
        result = text
        for trigger, alts in alternatives.items():
            if trigger.lower() in result.lower():
                result = re.sub(
                    re.escape(trigger), 
                    random.choice(alts), 
                    result, 
                    flags=re.IGNORECASE
                )
        
        return result
    
    def generate_honeypot_fields(self) -> str:
        """Generate invisible honeypot fields to catch bots."""
        honeypot_fields = [
            '<input type="text" name="email_confirm" style="display:none !important;" tabindex="-1" autocomplete="off">',
            '<div style="position:absolute;left:-5000px;"><input type="text" name="website" tabindex="-1"></div>',
            '<input type="hidden" name="timestamp" value="">',
            '<!-- Do not fill this field --><input type="text" name="phone" style="opacity:0;position:absolute;top:0;left:0;height:0;width:0;z-index:-1;">',
            '<span style="display:none;">Leave this field empty: <input type="text" name="url"></span>'
        ]
        
        selected_fields = random.sample(honeypot_fields, random.randint(2, 4))
        return '\n'.join(selected_fields)
    
    def generate_dynamic_content(self) -> Dict[str, str]:
        """Generate dynamic content with randomization."""
        company_names = ["TechCorp", "InnovateCo", "DigitalHub", "FutureTech", "DataCorp"]
        seasons = ["Spring", "Summer", "Fall", "Winter"]
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        current_month = datetime.datetime.now().strftime("%B")
        current_year = datetime.datetime.now().year
        
        # Generate subject with randomization
        subject_template = random.choice(self.subject_templates)
        subject = subject_template.format(
            company=random.choice(company_names),
            month=current_month,
            year=current_year,
            season=random.choice(seasons)
        )
        
        # Generate content blocks
        content_sections = []
        for block in random.sample(self.content_blocks, random.randint(2, 3)):
            title = block["title"]
            content = random.choice(block["variations"])
            content_sections.append(f"<h2>{title}</h2><p>{content}</p>")
        
        return {
            "subject": subject,
            "content_sections": content_sections,
            "company": random.choice(company_names)
        }
    
    def optimize_text_image_ratio(self, html_content: str) -> str:
        """Optimize text-to-image ratio for better deliverability."""
        # Count text content (excluding HTML tags)
        text_content = re.sub(r'<[^>]+>', '', html_content)
        text_length = len(text_content.strip())
        
        # Count images
        image_count = len(re.findall(r'<img[^>]*>', html_content, re.IGNORECASE))
        
        # If ratio is poor, add more text content
        if image_count > 0 and text_length / image_count < 200:
            additional_text = [
                "<p>We appreciate your continued interest in our updates.</p>",
                "<p>Thank you for being a valued member of our community.</p>",
                "<p>Your feedback helps us improve our services continuously.</p>",
                "<p>We're committed to providing you with relevant and useful information.</p>"
            ]
            html_content += random.choice(additional_text)
        
        return html_content
    
    def generate_secure_headers(self, newsletter_id: str, recipient: str) -> Dict[str, str]:
        """Generate secure email headers."""
        headers = {
            "Message-ID": f"<{newsletter_id}@{random.choice(['mail', 'newsletter', 'updates'])}.example.com>",
            "Date": self.randomize_timestamp(),
            "List-Unsubscribe": f"<mailto:unsubscribe@example.com?subject=unsubscribe-{newsletter_id}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            "Precedence": "bulk",
            "Auto-Submitted": "auto-generated",
            "X-Newsletter-ID": newsletter_id,
            "X-Recipient-Hash": hashlib.sha256(recipient.encode()).hexdigest()[:16],
            "MIME-Version": "1.0",
            "Content-Type": "multipart/alternative"
        }
        
        return headers
    
    def create_html_template(self, content_data: Dict[str, str], newsletter_id: str) -> str:
        """Create HTML email template with anti-spam techniques."""
        honeypot_fields = self.generate_honeypot_fields()
        
        # Basic styling to avoid spam triggers
        css_styles = """
        <style type="text/css">
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 25px; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
        .unsubscribe { text-align: center; margin-top: 20px; }
        </style>
        """
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{html.escape(content_data['subject'])}</title>
            {css_styles}
        </head>
        <body>
            <div class="container">
                <h1>Newsletter from {content_data['company']}</h1>
                
                {''.join(content_data['content_sections'])}
                
                <div class="footer">
                    <p>Thank you for your continued support!</p>
                    <p>Newsletter ID: {newsletter_id}</p>
                    <div class="unsubscribe">
                        <a href="mailto:unsubscribe@example.com?subject=unsubscribe-{newsletter_id}">Unsubscribe</a>
                    </div>
                </div>
                
                {honeypot_fields}
            </div>
        </body>
        </html>
        """
        
        # Apply obfuscation and spam avoidance
        html_content = self.avoid_spam_triggers(html_content)
        html_content = self.obfuscate_text(html_content)
        html_content = self.optimize_text_image_ratio(html_content)
        
        return html_content
    
    def create_text_version(self, content_data: Dict[str, str], newsletter_id: str) -> str:
        """Create plain text version of the newsletter."""
        text_content = f"""
Newsletter from {content_data['company']}
{'=' * (len(content_data['company']) + 17)}

"""
        
        for section in content_data['content_sections']:
            # Extract title and content from HTML
            title_match = re.search(r'<h2>(.*?)</h2>', section)
            content_match = re.search(r'<p>(.*?)</p>', section)
            
            if title_match and content_match:
                title = title_match.group(1)
                content = content_match.group(1)
                text_content += f"{title}\n{'-' * len(title)}\n{content}\n\n"
        
        text_content += f"""
Thank you for your continued support!

Newsletter ID: {newsletter_id}

To unsubscribe, reply to this email with "UNSUBSCRIBE" in the subject line.
"""
        
        # Apply spam avoidance to text version
        text_content = self.avoid_spam_triggers(text_content)
        
        return text_content
    
    def generate_newsletter(self, recipient: str) -> MIMEMultipart:
        """Generate a complete newsletter email."""
        newsletter_id = self.generate_unique_id()
        content_data = self.generate_dynamic_content()
        
        # Create multipart message
        msg = MIMEMultipart('alternative')
        
        # Set headers
        headers = self.generate_secure_headers(newsletter_id, recipient)
        for key, value in headers.items():
            if key not in ['Date', 'Message-ID']:  # These are set automatically
                msg[key] = value
        
        # Set standard email fields
        msg['Subject'] = content_data['subject']
        msg['From'] = formataddr((content_data['company'], 'newsletter@example.com'))
        msg['To'] = recipient
        msg['Date'] = headers['Date']
        msg['Message-ID'] = headers['Message-ID']
        
        # Create text and HTML versions
        text_content = self.create_text_version(content_data, newsletter_id)
        html_content = self.create_html_template(content_data, newsletter_id)
        
        # Attach text and HTML parts
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        return msg
    
    def get_ip_rotation_suggestions(self) -> List[str]:
        """Provide IP rotation suggestions for better deliverability."""
        return [
            "Use multiple SMTP servers with different IP addresses",
            "Implement IP warming: gradually increase sending volume",
            "Use dedicated IP addresses for bulk email sending",
            "Rotate between different email service providers",
            "Consider using email delivery services like SendGrid, Mailgun, or Amazon SES",
            "Monitor IP reputation using tools like SenderScore or BarracudaCentral",
            "Implement proper SPF, DKIM, and DMARC records for each IP",
            "Use different IP pools for different types of emails",
            "Maintain separate IPs for transactional vs. marketing emails",
            "Monitor blacklist status and have backup IPs ready"
        ]
    
    def get_authentication_setup_guide(self) -> Dict[str, str]:
        """Provide email authentication setup suggestions."""
        return {
            "SPF": """
SPF (Sender Policy Framework) Record:
Add this TXT record to your domain's DNS:

v=spf1 include:_spf.google.com include:amazonses.com ip4:YOUR_IP_ADDRESS ~all

Replace YOUR_IP_ADDRESS with your actual sending IP.
The ~all means soft fail (recommended for testing).
Use -all for hard fail once you're confident in your setup.
            """,
            
            "DKIM": """
DKIM (DomainKeys Identified Mail) Setup:
1. Generate DKIM keys using your email service provider
2. Add the public key to your DNS as a TXT record:
   
   selector._domainkey.yourdomain.com TXT "v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY"

3. Configure your email server to sign outgoing emails with the private key
4. Test DKIM signature using tools like mail-tester.com
            """,
            
            "DMARC": """
DMARC (Domain-based Message Authentication) Policy:
Add this TXT record to _dmarc.yourdomain.com:

v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; ruf=mailto:dmarc@yourdomain.com; sp=quarantine; adkim=r; aspf=r;

Policy options:
- p=none: Monitor only (recommended for testing)
- p=quarantine: Move suspicious emails to spam
- p=reject: Reject unauthenticated emails

Set up aggregate (rua) and forensic (ruf) reporting emails.
            """
        }


def main():
    """Main function to demonstrate the newsletter generator."""
    generator = NewsletterGenerator()
    
    print("Advanced Newsletter Generator with Anti-Spam Techniques")
    print("=" * 55)
    
    # Load email list
    emails = generator.load_email_list()
    print(f"Loaded {len(emails)} email addresses")
    
    if not emails:
        print("No email addresses found. Please check your mails.txt file.")
        return
    
    # Generate sample newsletter
    print("\nGenerating sample newsletter...")
    sample_email = emails[0] if emails else "test@example.com"
    newsletter = generator.generate_newsletter(sample_email)
    
    print(f"Sample newsletter generated for: {sample_email}")
    print(f"Subject: {newsletter['Subject']}")
    print(f"Newsletter ID: {newsletter['X-Newsletter-ID']}")
    
    # Save sample to file
    with open('sample_newsletter.eml', 'w', encoding='utf-8') as f:
        f.write(newsletter.as_string())
    print("Sample newsletter saved to: sample_newsletter.eml")
    
    # Display authentication setup guide
    print("\n" + "=" * 55)
    print("EMAIL AUTHENTICATION SETUP GUIDE")
    print("=" * 55)
    
    auth_guide = generator.get_authentication_setup_guide()
    for auth_type, instructions in auth_guide.items():
        print(f"\n{auth_type}:")
        print(instructions)
    
    # Display IP rotation suggestions
    print("\n" + "=" * 55)
    print("IP ROTATION SUGGESTIONS")
    print("=" * 55)
    
    ip_suggestions = generator.get_ip_rotation_suggestions()
    for i, suggestion in enumerate(ip_suggestions, 1):
        print(f"{i}. {suggestion}")
    
    print(f"\nTotal anti-spam techniques implemented: 10")
    print("Newsletter generation complete!")


if __name__ == "__main__":
    main()