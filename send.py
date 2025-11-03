import smtplib
import dns.resolver
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import threading
import queue
import socks
import socket
import argparse
import os
import sys
import re
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

NUM_THREADS = 150  # Fixer le nombre de threads à 100
BATCH_SIZE = 200    # Chaque batch contient 50 emails

# Définir SOCKS5 comme proxy
#socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 30001)
#socket.socket = socks.socksocket  # Remplacer le socket par celui qui passe par le proxy

# Global variables for tracking progress
total_sent = 0
total_failed = 0
progress_lock = threading.Lock()
progress_bar = None

def validate_email(email):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_file_exists(file_path):
    """Check if file exists and is readable."""
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Error: File '{file_path}' does not exist.{Style.RESET_ALL}")
        return False
    if not os.path.isfile(file_path):
        print(f"{Fore.RED}Error: '{file_path}' is not a file.{Style.RESET_ALL}")
        return False
    if not os.access(file_path, os.R_OK):
        print(f"{Fore.RED}Error: File '{file_path}' is not readable.{Style.RESET_ALL}")
        return False
    return True

def read_html_file(file_path):
    """Read HTML content from file."""
    if not validate_file_exists(file_path):
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as html_file:
            html_content = html_file.read()
        return html_content
    except Exception as e:
        print(f"{Fore.RED}Error reading HTML file: {e}{Style.RESET_ALL}")
        sys.exit(1)

def read_emails_file(file_path):
    """Read and validate emails from file."""
    if not validate_file_exists(file_path):
        sys.exit(1)
    try:
        with open(file_path, "r") as file:
            emails = [line.strip() for line in file.readlines() if line.strip()]
        
        # Validate emails
        valid_emails = []
        invalid_emails = []
        for email in emails:
            if validate_email(email):
                valid_emails.append(email)
            else:
                invalid_emails.append(email)
        
        if invalid_emails:
            print(f"{Fore.YELLOW}Warning: Found {len(invalid_emails)} invalid email(s):{Style.RESET_ALL}")
            for email in invalid_emails[:5]:  # Show first 5
                print(f"  - {email}")
            if len(invalid_emails) > 5:
                print(f"  ... and {len(invalid_emails) - 5} more")
        
        if not valid_emails:
            print(f"{Fore.RED}Error: No valid emails found in '{file_path}'.{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_emails
    except Exception as e:
        print(f"{Fore.RED}Error reading emails file: {e}{Style.RESET_ALL}")
        sys.exit(1)

def confirm_send(num_emails, sender_email):
    """Ask user for confirmation before sending."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Email Sending Confirmation{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"  Sender: {Fore.YELLOW}{sender_email}{Style.RESET_ALL}")
    print(f"  Recipients: {Fore.YELLOW}{num_emails}{Style.RESET_ALL} email(s)")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    response = input(f"{Fore.YELLOW}Do you want to proceed? (yes/no): {Style.RESET_ALL}").strip().lower()
    return response in ['yes', 'y']

def send_email_task(q, mx_server, sender_email, sender_name, subject, message, to_email, verbose=False):
    global total_sent, total_failed, progress_bar
    
    while True:
        batch = q.get()
        if batch is None:
            break  # Arrêter le thread quand on reçoit "None"

        try:
            server = smtplib.SMTP(mx_server)
            server.ehlo("antgi.com")

            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, sender_email))
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))

            server.sendmail(sender_email, batch, msg.as_string())
            
            with progress_lock:
                total_sent += len(batch)
                if progress_bar:
                    progress_bar.update(len(batch))
                if verbose:
                    print(f"{Fore.GREEN}✓ Batch of {len(batch)} emails successfully sent.{Style.RESET_ALL}")

            server.quit()
        except Exception as e:
            with progress_lock:
                total_failed += len(batch)
                if progress_bar:
                    progress_bar.update(len(batch))
                if verbose:
                    print(f"{Fore.RED}✗ Failed to send email batch: {e}{Style.RESET_ALL}")
        finally:
            q.task_done()

def prepare_and_send_batches(recipient_emails, subject, message, sender_email, sender_name, to_email, num_threads=NUM_THREADS, batch_size=BATCH_SIZE, mx_server=None, smtp_port=25, verbose=False):
    global progress_bar, total_sent, total_failed
    
    # Reset counters
    total_sent = 0
    total_failed = 0
    
    # Determine MX server if not provided
    if not mx_server:
        try:
            domain = recipient_emails[0].split('@')[1]
            print(f"{Fore.CYAN}Resolving MX records for domain: {domain}...{Style.RESET_ALL}")
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_record = sorted(mx_records, key=lambda rec: rec.preference)[0]
            mx_server = str(mx_record.exchange).strip('.')
            print(f"{Fore.GREEN}Found SMTP server: {mx_server}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error resolving MX records: {e}{Style.RESET_ALL}")
            sys.exit(1)

    q = queue.Queue()

    # Créer les threads pour envoyer les e-mails
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=send_email_task, args=(q, mx_server, sender_email, sender_name, subject, message, to_email, verbose))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Initialize progress bar
    print(f"\n{Fore.CYAN}Starting email send with {num_threads} threads...{Style.RESET_ALL}\n")
    progress_bar = tqdm(total=len(recipient_emails), desc="Sending emails", unit="email", 
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')

    # Ajouter les emails dans la queue par batch
    for i in range(0, len(recipient_emails), batch_size):
        batch = recipient_emails[i:i + batch_size]
        q.put(batch)

    # Attendre que tous les emails soient envoyés
    q.join()

    # Close progress bar
    if progress_bar:
        progress_bar.close()

    # Envoyer un signal d'arrêt aux threads
    for _ in range(num_threads):
        q.put(None)
    
    for thread in threads:
        thread.join()
    
    return total_sent, total_failed

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Bulk Email Sender - Send emails to multiple recipients with threading support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --threads 50 --emails mails.txt --template message.html
  %(prog)s --sender user@domain.com --sender-name "John Doe" --subject "Hello"
  %(prog)s --verbose --threads 100 --batch-size 50
        '''
    )
    
    # Required arguments
    parser.add_argument('--emails', '-e', default='mails.txt',
                       help='Path to file containing recipient emails (default: mails.txt)')
    parser.add_argument('--template', '-t', default='message.html',
                       help='Path to HTML template file (default: message.html)')
    
    # Optional configuration
    parser.add_argument('--threads', type=int, default=NUM_THREADS,
                       help=f'Number of concurrent threads (default: {NUM_THREADS})')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                       help=f'Number of emails per batch (default: {BATCH_SIZE})')
    parser.add_argument('--sender', '-s', default='dkdiokpozp@infomailnedokod.de',
                       help='Sender email address (default: dkdiokpozp@infomailnedokod.de)')
    parser.add_argument('--sender-name', default='kdoklzeoz',
                       help='Sender display name (default: kdoklzeoz)')
    parser.add_argument('--to-email', default=None,
                       help='To email address in header (defaults to sender email)')
    parser.add_argument('--subject', default='kdokdldo',
                       help='Email subject (default: kdokdldo)')
    parser.add_argument('--smtp-server', default=None,
                       help='SMTP server address (default: auto-detect from MX records)')
    parser.add_argument('--smtp-port', type=int, default=25,
                       help='SMTP server port (default: 25)')
    
    # Flags
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output for debugging')
    parser.add_argument('--no-confirm', action='store_true',
                       help='Skip confirmation prompt before sending')
    
    return parser.parse_args()

def main():
    """Main function to orchestrate email sending."""
    # Parse arguments
    args = parse_arguments()
    
    # Print header
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}        Bulk Email Sender{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    # Validate sender email
    if not validate_email(args.sender):
        print(f"{Fore.RED}Error: Invalid sender email address: {args.sender}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Load emails and HTML content
    print(f"{Fore.CYAN}Loading configuration...{Style.RESET_ALL}")
    recipient_emails = read_emails_file(args.emails)
    message = read_html_file(args.template)
    
    print(f"{Fore.GREEN}✓ Loaded {len(recipient_emails)} valid recipient(s){Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Loaded HTML template from {args.template}{Style.RESET_ALL}")
    
    # Set to_email to sender if not specified
    to_email = args.to_email if args.to_email else args.sender
    
    # Confirmation
    if not args.no_confirm:
        if not confirm_send(len(recipient_emails), args.sender):
            print(f"\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
            sys.exit(0)
    
    # Send emails
    try:
        sent, failed = prepare_and_send_batches(
            recipient_emails=recipient_emails,
            subject=args.subject,
            message=message,
            sender_email=args.sender,
            sender_name=args.sender_name,
            to_email=to_email,
            num_threads=args.threads,
            batch_size=args.batch_size,
            mx_server=args.smtp_server,
            smtp_port=args.smtp_port,
            verbose=args.verbose
        )
        
        # Print summary
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Email Sending Summary{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"  Total attempted: {Fore.YELLOW}{len(recipient_emails)}{Style.RESET_ALL}")
        print(f"  Successfully sent: {Fore.GREEN}{sent}{Style.RESET_ALL}")
        print(f"  Failed: {Fore.RED}{failed}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        if failed > 0:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Operation interrupted by user.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
