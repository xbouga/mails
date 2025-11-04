#!/usr/bin/env python3
"""
Newsletter Batch Sender
======================

This script handles batch sending of newsletters with anti-spam techniques,
IP rotation, and delivery optimization.
"""

import time
import logging
import smtplib
import random
from typing import List, Dict, Optional
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr
import threading
import queue
import sys
import os
from datetime import datetime, timedelta

# Import our modules
from newsletter_generator import NewsletterGenerator
from config import (
    SMTP_SETTINGS, DELIVERY_SETTINGS, MONITORING_SETTINGS,
    IP_ROTATION, ANTI_SPAM_SETTINGS, FILE_PATHS
)


class NewsletterBatchSender:
    """Handles batch sending with anti-spam techniques."""
    
    def __init__(self):
        self.generator = NewsletterGenerator()
        self.setup_logging()
        self.sent_count = 0
        self.failed_count = 0
        self.start_time = None
        
        # Create output directories
        self.create_directories()
        
        # Load email list
        self.email_list = self.generator.load_email_list()
        
        # Validate email addresses if enabled
        if ANTI_SPAM_SETTINGS.get('validate_email_addresses', True):
            self.email_list = self.validate_emails(self.email_list)
        
        self.logger.info(f"Loaded {len(self.email_list)} valid email addresses")
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, MONITORING_SETTINGS.get('log_level', 'INFO'))
        log_file = MONITORING_SETTINGS.get('log_file', 'newsletter_sender.log')
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_directories(self):
        """Create necessary directories."""
        for path in [FILE_PATHS['output_dir'], FILE_PATHS['log_dir'], FILE_PATHS['backup_dir']]:
            os.makedirs(path, exist_ok=True)
    
    def validate_emails(self, emails: List[str]) -> List[str]:
        """Validate email addresses format."""
        valid_emails = []
        for email in emails:
            try:
                name, addr = parseaddr(email)
                if '@' in addr and '.' in addr.split('@')[1]:
                    valid_emails.append(email)
            except Exception:
                self.logger.warning(f"Invalid email format: {email}")
        
        self.logger.info(f"Validated {len(valid_emails)} out of {len(emails)} emails")
        return valid_emails
    
    def get_smtp_connection(self) -> smtplib.SMTP:
        """Create SMTP connection with rotation if enabled."""
        if IP_ROTATION.get('enabled', False) and IP_ROTATION.get('ip_addresses'):
            # Select IP based on rotation strategy
            ip_address = self.select_ip_address()
            smtp_server = ip_address
        else:
            smtp_server = SMTP_SETTINGS['smtp_server']
        
        try:
            if SMTP_SETTINGS.get('use_tls', True):
                server = smtplib.SMTP(smtp_server, SMTP_SETTINGS['smtp_port'])
                server.starttls()
            else:
                server = smtplib.SMTP(smtp_server, SMTP_SETTINGS['smtp_port'])
            
            if SMTP_SETTINGS.get('username') and SMTP_SETTINGS.get('password'):
                server.login(SMTP_SETTINGS['username'], SMTP_SETTINGS['password'])
            
            return server
        except Exception as e:
            self.logger.error(f"Failed to connect to SMTP server {smtp_server}: {e}")
            raise
    
    def select_ip_address(self) -> str:
        """Select IP address based on rotation strategy."""
        ip_addresses = IP_ROTATION['ip_addresses']
        strategy = IP_ROTATION.get('rotation_strategy', 'round_robin')
        
        if strategy == 'random':
            return random.choice(ip_addresses)
        elif strategy == 'round_robin':
            # Simple round-robin based on sent count
            index = self.sent_count % len(ip_addresses)
            return ip_addresses[index]
        else:
            return ip_addresses[0]
    
    def send_single_email(self, smtp_server: smtplib.SMTP, recipient: str) -> bool:
        """Send a single newsletter email."""
        try:
            # Generate newsletter
            newsletter = self.generator.generate_newsletter(recipient)
            
            # Send email
            smtp_server.send_message(newsletter)
            
            self.logger.info(f"Successfully sent newsletter to {recipient}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send newsletter to {recipient}: {e}")
            return False
    
    def send_batch(self, batch_emails: List[str]) -> Dict[str, int]:
        """Send a batch of emails."""
        batch_stats = {'sent': 0, 'failed': 0}
        
        try:
            smtp_server = self.get_smtp_connection()
            
            for email in batch_emails:
                try:
                    if self.send_single_email(smtp_server, email):
                        batch_stats['sent'] += 1
                        self.sent_count += 1
                    else:
                        batch_stats['failed'] += 1
                        self.failed_count += 1
                    
                    # Add small delay between emails to avoid being flagged
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    self.logger.error(f"Error sending to {email}: {e}")
                    batch_stats['failed'] += 1
                    self.failed_count += 1
            
            smtp_server.quit()
            
        except Exception as e:
            self.logger.error(f"Batch sending failed: {e}")
            batch_stats['failed'] += len(batch_emails) - batch_stats['sent']
            self.failed_count += len(batch_emails) - batch_stats['sent']
        
        return batch_stats
    
    def calculate_delay(self) -> float:
        """Calculate delay to maintain sending rate limits."""
        if not DELIVERY_SETTINGS.get('enable_throttling', True):
            return DELIVERY_SETTINGS.get('batch_delay_seconds', 60)
        
        emails_per_hour = DELIVERY_SETTINGS.get('emails_per_hour', 100)
        batch_size = DELIVERY_SETTINGS.get('batch_size', 50)
        
        # Calculate required delay between batches
        emails_per_second = emails_per_hour / 3600
        batch_time = batch_size / emails_per_second
        
        return max(batch_time, DELIVERY_SETTINGS.get('batch_delay_seconds', 60))
    
    def create_batches(self, emails: List[str]) -> List[List[str]]:
        """Create email batches."""
        batch_size = DELIVERY_SETTINGS.get('batch_size', 50)
        batches = []
        
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def save_progress(self, completed_batches: int, total_batches: int):
        """Save sending progress."""
        progress_file = os.path.join(FILE_PATHS['backup_dir'], 'sending_progress.txt')
        
        with open(progress_file, 'w') as f:
            f.write(f"Completed: {completed_batches}/{total_batches}\n")
            f.write(f"Sent: {self.sent_count}\n")
            f.write(f"Failed: {self.failed_count}\n")
            f.write(f"Last updated: {datetime.now()}\n")
    
    def load_progress(self) -> Dict[str, int]:
        """Load previous sending progress."""
        progress_file = os.path.join(FILE_PATHS['backup_dir'], 'sending_progress.txt')
        
        if not os.path.exists(progress_file):
            return {'completed_batches': 0, 'sent': 0, 'failed': 0}
        
        try:
            with open(progress_file, 'r') as f:
                lines = f.readlines()
                
            completed = int(lines[0].split(':')[1].split('/')[0].strip())
            sent = int(lines[1].split(':')[1].strip())
            failed = int(lines[2].split(':')[1].strip())
            
            return {'completed_batches': completed, 'sent': sent, 'failed': failed}
            
        except Exception as e:
            self.logger.warning(f"Could not load progress: {e}")
            return {'completed_batches': 0, 'sent': 0, 'failed': 0}
    
    def send_all_newsletters(self, resume: bool = False) -> Dict[str, int]:
        """Send newsletters to all email addresses."""
        self.start_time = datetime.now()
        
        # Load progress if resuming
        if resume:
            progress = self.load_progress()
            self.sent_count = progress['sent']
            self.failed_count = progress['failed']
            start_batch = progress['completed_batches']
        else:
            start_batch = 0
        
        # Create batches
        batches = self.create_batches(self.email_list)
        total_batches = len(batches)
        
        self.logger.info(f"Starting newsletter campaign: {total_batches} batches")
        self.logger.info(f"Total emails to send: {len(self.email_list)}")
        
        if resume:
            self.logger.info(f"Resuming from batch {start_batch + 1}")
        
        # Send batches
        for batch_num, batch_emails in enumerate(batches[start_batch:], start_batch):
            self.logger.info(f"Processing batch {batch_num + 1}/{total_batches}")
            
            # Send batch
            batch_stats = self.send_batch(batch_emails)
            
            # Log batch results
            self.logger.info(
                f"Batch {batch_num + 1} completed: "
                f"{batch_stats['sent']} sent, {batch_stats['failed']} failed"
            )
            
            # Save progress
            self.save_progress(batch_num + 1, total_batches)
            
            # Wait between batches (except for the last batch)
            if batch_num < total_batches - 1:
                delay = self.calculate_delay()
                self.logger.info(f"Waiting {delay:.1f} seconds before next batch...")
                time.sleep(delay)
        
        # Calculate final statistics
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        final_stats = {
            'total_sent': self.sent_count,
            'total_failed': self.failed_count,
            'duration_minutes': duration.total_seconds() / 60,
            'emails_per_hour': (self.sent_count / duration.total_seconds()) * 3600
        }
        
        self.logger.info("Newsletter campaign completed!")
        self.logger.info(f"Total sent: {final_stats['total_sent']}")
        self.logger.info(f"Total failed: {final_stats['total_failed']}")
        self.logger.info(f"Duration: {final_stats['duration_minutes']:.1f} minutes")
        self.logger.info(f"Average rate: {final_stats['emails_per_hour']:.1f} emails/hour")
        
        return final_stats
    
    def test_configuration(self) -> bool:
        """Test SMTP configuration and settings."""
        self.logger.info("Testing newsletter configuration...")
        
        try:
            # Test SMTP connection
            smtp_server = self.get_smtp_connection()
            smtp_server.noop()  # Test connection
            smtp_server.quit()
            self.logger.info("✓ SMTP connection successful")
            
            # Test newsletter generation
            test_email = "test@example.com"
            newsletter = self.generator.generate_newsletter(test_email)
            self.logger.info("✓ Newsletter generation successful")
            
            # Save test newsletter
            test_file = os.path.join(FILE_PATHS['output_dir'], 'test_newsletter.eml')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(newsletter.as_string())
            self.logger.info(f"✓ Test newsletter saved to {test_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration test failed: {e}")
            return False
    
    def get_campaign_estimate(self) -> Dict[str, any]:
        """Estimate campaign duration and requirements."""
        total_emails = len(self.email_list)
        batch_size = DELIVERY_SETTINGS.get('batch_size', 50)
        emails_per_hour = DELIVERY_SETTINGS.get('emails_per_hour', 100)
        
        total_batches = (total_emails + batch_size - 1) // batch_size  # Ceiling division
        estimated_hours = total_emails / emails_per_hour
        
        return {
            'total_emails': total_emails,
            'total_batches': total_batches,
            'estimated_duration_hours': estimated_hours,
            'estimated_duration_minutes': estimated_hours * 60,
            'batch_size': batch_size,
            'sending_rate': emails_per_hour
        }


def main():
    """Main function for the batch sender."""
    print("Newsletter Batch Sender")
    print("=" * 23)
    
    sender = NewsletterBatchSender()
    
    # Get campaign estimate
    estimate = sender.get_campaign_estimate()
    print(f"Campaign Estimate:")
    print(f"  Total emails: {estimate['total_emails']}")
    print(f"  Total batches: {estimate['total_batches']}")
    print(f"  Estimated duration: {estimate['estimated_duration_hours']:.1f} hours")
    print(f"  Sending rate: {estimate['sending_rate']} emails/hour")
    print()
    
    # Menu
    while True:
        print("Options:")
        print("1. Test configuration")
        print("2. Send sample newsletter")
        print("3. Start full campaign")
        print("4. Resume campaign")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            if sender.test_configuration():
                print("✓ Configuration test passed!")
            else:
                print("✗ Configuration test failed!")
        
        elif choice == '2':
            test_email = input("Enter test email address: ").strip()
            if test_email:
                try:
                    newsletter = sender.generator.generate_newsletter(test_email)
                    test_file = os.path.join(FILE_PATHS['output_dir'], f'test_{int(time.time())}.eml')
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(newsletter.as_string())
                    print(f"✓ Test newsletter saved to {test_file}")
                except Exception as e:
                    print(f"✗ Failed to generate test newsletter: {e}")
        
        elif choice == '3':
            confirm = input(f"Start campaign for {estimate['total_emails']} emails? (y/N): ")
            if confirm.lower() == 'y':
                sender.send_all_newsletters(resume=False)
                break
        
        elif choice == '4':
            confirm = input("Resume previous campaign? (y/N): ")
            if confirm.lower() == 'y':
                sender.send_all_newsletters(resume=True)
                break
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()