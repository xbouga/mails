#!/usr/bin/env python3
"""
Newsletter Usage Examples
========================

This script demonstrates how to use the newsletter generator with various
anti-spam configurations and sending strategies.
"""

import os
import time
from newsletter_generator import NewsletterGenerator
from batch_sender import NewsletterBatchSender


def example_1_generate_single_newsletter():
    """Example 1: Generate a single newsletter with anti-spam features."""
    print("Example 1: Generating Single Newsletter")
    print("=" * 40)
    
    generator = NewsletterGenerator()
    
    # Generate newsletter for a test email
    test_email = "test@example.com"
    newsletter = generator.generate_newsletter(test_email)
    
    # Display newsletter information
    print(f"Subject: {newsletter['Subject']}")
    print(f"From: {newsletter['From']}")
    print(f"Newsletter ID: {newsletter['X-Newsletter-ID']}")
    print(f"Recipient Hash: {newsletter['X-Recipient-Hash']}")
    
    # Save to file
    filename = f"example_newsletter_{int(time.time())}.eml"
    with open(f"output/{filename}", 'w', encoding='utf-8') as f:
        f.write(newsletter.as_string())
    
    print(f"Newsletter saved to: output/{filename}")
    print()


def example_2_batch_generation():
    """Example 2: Generate multiple newsletters with different content."""
    print("Example 2: Batch Newsletter Generation")
    print("=" * 38)
    
    generator = NewsletterGenerator()
    
    # Load a few test emails
    test_emails = [
        "user1@example.com",
        "user2@example.com", 
        "user3@example.com"
    ]
    
    newsletters = []
    for email in test_emails:
        newsletter = generator.generate_newsletter(email)
        newsletters.append((email, newsletter))
        print(f"Generated newsletter for {email}")
        print(f"  Subject: {newsletter['Subject']}")
        print(f"  ID: {newsletter['X-Newsletter-ID']}")
    
    print(f"\nGenerated {len(newsletters)} unique newsletters with anti-spam features")
    print()


def example_3_anti_spam_demonstration():
    """Example 3: Demonstrate anti-spam techniques."""
    print("Example 3: Anti-Spam Techniques Demonstration")
    print("=" * 45)
    
    generator = NewsletterGenerator()
    
    # Show spam trigger avoidance
    test_text = "This is a free amazing offer! Click here now!"
    clean_text = generator.avoid_spam_triggers(test_text)
    print(f"Original: {test_text}")
    print(f"Cleaned:  {clean_text}")
    print()
    
    # Show content obfuscation
    test_content = "Newsletter content with obfuscation"
    obfuscated = generator.obfuscate_text(test_content)
    print(f"Original:    {test_content}")
    print(f"Obfuscated:  {obfuscated}")
    print()
    
    # Show honeypot fields
    honeypots = generator.generate_honeypot_fields()
    print("Generated honeypot fields:")
    print(honeypots[:200] + "..." if len(honeypots) > 200 else honeypots)
    print()


def example_4_authentication_setup():
    """Example 4: Display authentication setup information."""
    print("Example 4: Email Authentication Setup")
    print("=" * 35)
    
    generator = NewsletterGenerator()
    auth_guide = generator.get_authentication_setup_guide()
    
    for auth_type, instructions in auth_guide.items():
        print(f"{auth_type} Setup:")
        print("-" * (len(auth_type) + 7))
        print(instructions.strip())
        print()


def example_5_ip_rotation_info():
    """Example 5: Show IP rotation suggestions."""
    print("Example 5: IP Rotation Best Practices")
    print("=" * 35)
    
    generator = NewsletterGenerator()
    suggestions = generator.get_ip_rotation_suggestions()
    
    print("IP Rotation Strategies:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i:2d}. {suggestion}")
    print()


def example_6_campaign_estimate():
    """Example 6: Estimate campaign requirements."""
    print("Example 6: Campaign Estimation")
    print("=" * 28)
    
    sender = NewsletterBatchSender()
    estimate = sender.get_campaign_estimate()
    
    print(f"Total emails to send: {estimate['total_emails']:,}")
    print(f"Number of batches: {estimate['total_batches']}")
    print(f"Estimated duration: {estimate['estimated_duration_hours']:.1f} hours")
    print(f"Sending rate: {estimate['sending_rate']} emails/hour")
    print(f"Batch size: {estimate['batch_size']} emails per batch")
    print()


def example_7_content_variations():
    """Example 7: Show content generation variations."""
    print("Example 7: Content Generation Variations")
    print("=" * 37)
    
    generator = NewsletterGenerator()
    
    print("Generating 3 different newsletters to show variation:")
    for i in range(3):
        content = generator.generate_dynamic_content()
        print(f"\nNewsletter {i+1}:")
        print(f"  Subject: {content['subject']}")
        print(f"  Company: {content['company']}")
        print(f"  Sections: {len(content['content_sections'])}")
    print()


def example_8_security_features():
    """Example 8: Demonstrate security features."""
    print("Example 8: Security Features")
    print("=" * 26)
    
    generator = NewsletterGenerator()
    
    # Generate secure headers
    newsletter_id = generator.generate_unique_id()
    recipient = "secure@example.com"
    headers = generator.generate_secure_headers(newsletter_id, recipient)
    
    print("Secure headers generated:")
    for key, value in headers.items():
        if len(value) > 50:
            value = value[:47] + "..."
        print(f"  {key}: {value}")
    print()


def main():
    """Run all examples."""
    print("Advanced Newsletter Generator - Usage Examples")
    print("=" * 47)
    print()
    print("This script demonstrates all anti-spam features and capabilities")
    print("of the newsletter generation system.")
    print()
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    examples = [
        example_1_generate_single_newsletter,
        example_2_batch_generation,
        example_3_anti_spam_demonstration,
        example_4_authentication_setup,
        example_5_ip_rotation_info,
        example_6_campaign_estimate,
        example_7_content_variations,
        example_8_security_features
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print()
    
    print("=" * 47)
    print("All examples completed!")
    print()
    print("Next steps:")
    print("1. Configure your SMTP settings in config.py")
    print("2. Set up email authentication (SPF, DKIM, DMARC)")
    print("3. Test with a small batch before full campaign")
    print("4. Monitor delivery rates and adjust settings")


if __name__ == "__main__":
    main()