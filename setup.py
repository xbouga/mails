#!/usr/bin/env python3
"""
Setup script for the Advanced Newsletter Generator
=================================================

This script sets up the newsletter generation system with all required
directories, dependencies, and initial configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def create_directories():
    """Create necessary directories for the newsletter system."""
    directories = [
        'templates',
        'output',
        'logs',
        'backups',
        'static/images',
        'static/css'
    ]
    
    print("Creating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Created: {directory}/")


def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("  ✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to install dependencies: {e}")
        return False


def create_sample_templates():
    """Create sample email templates."""
    print("\nCreating sample templates...")
    
    # HTML template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; text-align: center; }
        .content { padding: 20px 0; }
        .footer { border-top: 1px solid #eee; padding: 20px 0; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ company_name }}</h1>
        </div>
        <div class="content">
            {% for section in content_sections %}
            <div class="section">
                {{ section|safe }}
            </div>
            {% endfor %}
        </div>
        <div class="footer">
            <p>Thank you for subscribing to our newsletter!</p>
            <p><a href="{{ unsubscribe_url }}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>"""
    
    # Text template
    text_template = """{{ company_name }} Newsletter
{{ "=" * (company_name|length + 11) }}

{% for section in content_sections %}
{{ section }}

{% endfor %}

Thank you for subscribing to our newsletter!

To unsubscribe, visit: {{ unsubscribe_url }}
"""
    
    # Save templates
    with open('templates/newsletter.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    with open('templates/newsletter.txt', 'w', encoding='utf-8') as f:
        f.write(text_template)
    
    print("  ✓ Created sample HTML template")
    print("  ✓ Created sample text template")


def create_environment_file():
    """Create sample environment configuration file."""
    print("\nCreating environment configuration...")
    
    env_content = """# Newsletter Generator Environment Configuration
# ============================================
# Copy this file to .env and update with your actual values

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true

# Email Settings
FROM_NAME=Your Company Name
FROM_EMAIL=newsletter@yourcompany.com
REPLY_TO=support@yourcompany.com

# Security Settings
SECRET_KEY=your_secret_key_here

# Optional: Database Configuration
# DATABASE_URL=postgresql://user:password@localhost/newsletter_db

# Optional: Redis Configuration (for queues)
# REDIS_URL=redis://localhost:6379/0

# Monitoring and Analytics
# ANALYTICS_API_KEY=your_analytics_key
# WEBHOOK_URL=https://your-webhook-url.com/newsletter-stats
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("  ✓ Created .env.example file")
    print("  → Copy .env.example to .env and update with your settings")


def create_sample_css():
    """Create sample CSS files for email styling."""
    print("\nCreating sample CSS files...")
    
    css_content = """/* Newsletter CSS Styles */
/* ===================== */

/* Reset styles */
body, table, td, p, a, li, blockquote {
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
}

/* Main container */
.email-container {
    max-width: 600px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333333;
}

/* Header styles */
.email-header {
    background-color: #f8f9fa;
    padding: 30px 20px;
    text-align: center;
    border-bottom: 3px solid #007bff;
}

.email-header h1 {
    margin: 0;
    color: #007bff;
    font-size: 28px;
    font-weight: bold;
}

/* Content styles */
.email-content {
    padding: 30px 20px;
    background-color: #ffffff;
}

.content-section {
    margin-bottom: 30px;
}

.content-section h2 {
    color: #333333;
    font-size: 22px;
    margin-bottom: 15px;
    border-bottom: 2px solid #e9ecef;
    padding-bottom: 8px;
}

.content-section p {
    margin-bottom: 15px;
    line-height: 1.7;
}

/* Button styles */
.email-button {
    display: inline-block;
    padding: 12px 24px;
    background-color: #007bff;
    color: #ffffff;
    text-decoration: none;
    border-radius: 4px;
    font-weight: bold;
    margin: 10px 0;
}

.email-button:hover {
    background-color: #0056b3;
}

/* Footer styles */
.email-footer {
    background-color: #f8f9fa;
    padding: 20px;
    text-align: center;
    border-top: 1px solid #e9ecef;
    font-size: 12px;
    color: #6c757d;
}

.email-footer a {
    color: #007bff;
    text-decoration: none;
}

.email-footer a:hover {
    text-decoration: underline;
}

/* Responsive styles */
@media only screen and (max-width: 600px) {
    .email-container {
        width: 100% !important;
    }
    
    .email-header,
    .email-content,
    .email-footer {
        padding: 20px 15px !important;
    }
    
    .email-header h1 {
        font-size: 24px !important;
    }
    
    .content-section h2 {
        font-size: 20px !important;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .email-container {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    .email-header {
        background-color: #2d2d2d;
    }
    
    .email-content {
        background-color: #1a1a1a;
    }
    
    .email-footer {
        background-color: #2d2d2d;
        color: #cccccc;
    }
}
"""
    
    with open('static/css/newsletter.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print("  ✓ Created newsletter.css")


def run_initial_test():
    """Run initial test to verify installation."""
    print("\nRunning initial test...")
    
    try:
        # Import our modules to test
        from newsletter_generator import NewsletterGenerator
        
        # Create generator instance
        generator = NewsletterGenerator()
        
        # Test content generation
        content = generator.generate_dynamic_content()
        print(f"  ✓ Content generation test passed")
        
        # Test newsletter generation
        newsletter = generator.generate_newsletter("test@example.com")
        print(f"  ✓ Newsletter generation test passed")
        
        # Save test newsletter
        test_file = 'output/installation_test.eml'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(newsletter.as_string())
        print(f"  ✓ Test newsletter saved to {test_file}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Installation test failed: {e}")
        return False


def display_setup_complete():
    """Display setup completion message."""
    print("\n" + "="*60)
    print("🎉 NEWSLETTER GENERATOR SETUP COMPLETE!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Copy .env.example to .env and configure your settings")
    print("2. Set up your SMTP credentials in .env")
    print("3. Configure DNS records (SPF, DKIM, DMARC)")
    print("4. Test the configuration: python batch_sender.py")
    print("5. Generate sample newsletter: python newsletter_generator.py")
    print()
    print("Files created:")
    print("  📁 templates/           - Email templates")
    print("  📁 output/             - Generated newsletters")
    print("  📁 logs/               - Application logs")
    print("  📁 backups/            - Progress backups")
    print("  📄 .env.example        - Environment configuration")
    print("  📄 static/css/         - CSS stylesheets")
    print()
    print("Documentation:")
    print("  📖 README.md           - Complete usage guide")
    print("  📖 config.py           - Configuration options")
    print()
    print("Anti-spam features implemented:")
    print("  ✓ Dynamic content generation")
    print("  ✓ Email structure optimization")
    print("  ✓ HTML encoding & spam avoidance")
    print("  ✓ Honeypot fields")
    print("  ✓ Content obfuscation")
    print("  ✓ Authentication setup guide")
    print("  ✓ Image handling")
    print("  ✓ Text-to-image ratio optimization")
    print("  ✓ Randomized IDs & timestamps")
    print("  ✓ IP rotation suggestions")
    print()
    print("Ready to generate newsletters! 🚀")


def main():
    """Main setup function."""
    print("Advanced Newsletter Generator Setup")
    print("=" * 35)
    print()
    
    steps = [
        ("Creating directories", create_directories),
        ("Installing dependencies", install_dependencies),
        ("Creating sample templates", create_sample_templates),
        ("Creating environment file", create_environment_file),
        ("Creating CSS files", create_sample_css),
        ("Running initial test", run_initial_test),
    ]
    
    success_count = 0
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        try:
            result = step_function()
            if result is not False:  # Allow None as success
                success_count += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    if success_count == len(steps):
        display_setup_complete()
    else:
        print(f"\n⚠️  Setup completed with {len(steps) - success_count} issues.")
        print("Please check the error messages above and retry if needed.")


if __name__ == "__main__":
    main()