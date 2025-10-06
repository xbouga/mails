"""
Newsletter Generator Configuration
=================================

This file contains configuration settings for the newsletter generator.
Modify these settings to customize your newsletter campaigns.
"""

# Email Settings
EMAIL_SETTINGS = {
    "from_name": "Your Company Name",
    "from_email": "newsletter@yourcompany.com",
    "reply_to": "support@yourcompany.com",
    "bounce_email": "bounce@yourcompany.com",
}

# SMTP Configuration (for actual sending)
SMTP_SETTINGS = {
    "smtp_server": "smtp.yourprovider.com",
    "smtp_port": 587,
    "use_tls": True,
    "username": "your_username",
    "password": "your_password",  # Use environment variable in production
}

# Content Customization
CONTENT_SETTINGS = {
    "company_names": [
        "Your Company",
        "TechCorp",
        "InnovateCo",
        "DigitalHub",
        "FutureTech"
    ],
    
    "subject_templates": [
        "Updates from {company} - {month} {year}",
        "{company} Newsletter - {season} Edition", 
        "What's New at {company}",
        "Your {company} Update",
        "Latest from {company}",
        "{company} Insights - {month}",
        "Monthly Digest from {company}",
        "{company} News & Updates",
        "Important Updates from {company}",
        "{company} Monthly Roundup"
    ],
    
    "content_blocks": [
        {
            "title": "Company Updates",
            "variations": [
                "We're excited to share some recent developments",
                "Here are the latest updates from our team",
                "We wanted to keep you informed about our progress",
                "Some exciting news to share with you",
                "Important updates from our organization",
                "Recent developments we thought you'd like to know about"
            ]
        },
        {
            "title": "Product Features",
            "variations": [
                "Our latest improvements focus on user experience",
                "New features designed with your feedback in mind",
                "Enhanced functionality now available",
                "Updates that make your workflow smoother",
                "Innovative solutions we've been working on",
                "Improvements based on community suggestions"
            ]
        },
        {
            "title": "Community News",
            "variations": [
                "See what's happening in our community",
                "Community highlights from this month",
                "Stories from our valued customers",
                "Community spotlights and achievements",
                "Member success stories and updates",
                "Community-driven initiatives and results"
            ]
        },
        {
            "title": "Industry Insights",
            "variations": [
                "Key trends we're following in the industry",
                "Market insights and analysis",
                "Industry developments that matter to you",
                "Expert perspectives on current trends",
                "Research findings and industry reports",
                "Thought leadership and strategic insights"
            ]
        },
        {
            "title": "Educational Content",
            "variations": [
                "Tips and best practices for success",
                "Educational resources to help you grow",
                "Training materials and learning opportunities",
                "Skill development and professional growth",
                "How-to guides and tutorials",
                "Knowledge sharing from our experts"
            ]
        }
    ]
}

# Anti-Spam Settings
ANTI_SPAM_SETTINGS = {
    "obfuscation_rate": 0.3,  # Percentage of characters to obfuscate
    "honeypot_fields_count": 3,  # Number of honeypot fields to include
    "min_text_length": 500,  # Minimum text length for good deliverability
    "max_images": 3,  # Maximum number of images per email
    "text_to_image_ratio": 200,  # Minimum characters per image
    
    "spam_trigger_replacements": {
        "free": ["complimentary", "no cost", "included", "provided"],
        "urgent": ["important", "timely", "priority", "essential"],
        "amazing": ["great", "excellent", "wonderful", "outstanding"],
        "incredible": ["remarkable", "impressive", "notable", "exceptional"],
        "click here": ["visit our site", "learn more", "read further", "explore"],
        "guarantee": ["promise", "commitment", "assurance", "pledge"],
        "money back": ["refund available", "satisfaction promise", "return policy"],
        "limited time": ["available now", "current offer", "present opportunity"],
        "act now": ["take action", "get started", "begin today", "start now"],
        "call now": ["contact us", "get in touch", "reach out", "connect with us"]
    }
}

# Randomization Settings
RANDOMIZATION_SETTINGS = {
    "timestamp_variance_minutes": 30,  # Random minutes to add/subtract
    "content_selection_min": 2,  # Minimum content blocks per email
    "content_selection_max": 4,  # Maximum content blocks per email
    "subject_randomization": True,  # Enable subject line randomization
    "send_time_randomization": True,  # Enable send time randomization
}

# Security Settings
SECURITY_SETTINGS = {
    "enable_dkim": True,
    "enable_spf_check": True,
    "enable_dmarc": True,
    "list_unsubscribe": True,
    "include_abuse_contact": True,
    "enable_message_id": True,
    "enable_tracking_protection": True,
}

# Delivery Settings
DELIVERY_SETTINGS = {
    "batch_size": 50,  # Number of emails per batch
    "batch_delay_seconds": 60,  # Delay between batches
    "max_retries": 3,  # Maximum retry attempts for failed sends
    "retry_delay_seconds": 300,  # Delay between retries
    "enable_throttling": True,  # Enable sending rate limiting
    "emails_per_hour": 100,  # Maximum emails per hour
}

# Monitoring and Logging
MONITORING_SETTINGS = {
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_file": "newsletter_generator.log",
    "enable_delivery_tracking": True,
    "enable_open_tracking": False,  # Disable to improve privacy
    "enable_click_tracking": False,  # Disable to improve privacy
    "bounce_handling": True,
}

# File Paths
FILE_PATHS = {
    "email_list": "mails.txt",
    "template_dir": "templates/",
    "output_dir": "output/",
    "log_dir": "logs/",
    "backup_dir": "backups/",
}

# Advanced Anti-Spam Techniques
ADVANCED_ANTI_SPAM = {
    "rotate_message_ids": True,
    "randomize_headers": True,
    "vary_content_structure": True,
    "enable_content_spinning": True,
    "use_synonyms": True,
    "randomize_css_classes": True,
    "obfuscate_links": False,  # Can hurt deliverability if overdone
    "include_text_version": True,
    "optimize_html_structure": True,
    "validate_email_addresses": True,
}

# DNS and Authentication Records Templates
DNS_RECORDS = {
    "spf_record": "v=spf1 include:_spf.google.com include:amazonses.com ip4:{ip_address} ~all",
    "dkim_record": "v=DKIM1; k=rsa; p={public_key}",
    "dmarc_record": "v=DMARC1; p=quarantine; rua=mailto:dmarc@{domain}; ruf=mailto:dmarc@{domain}; sp=quarantine; adkim=r; aspf=r;",
}

# IP Rotation Configuration
IP_ROTATION = {
    "enabled": False,  # Enable when you have multiple IPs
    "ip_addresses": [
        # "192.168.1.1",
        # "192.168.1.2",
        # Add your IP addresses here
    ],
    "rotation_strategy": "round_robin",  # round_robin, random, weighted
    "warm_up_volume": [10, 25, 50, 100, 200],  # Daily volumes for IP warming
    "warm_up_days": 5,  # Days for IP warming process
}