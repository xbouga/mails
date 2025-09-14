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
import logging
import time
from collections import defaultdict

NUM_THREADS = 150  # Fixer le nombre de threads à 100
BATCH_SIZE = 200    # Chaque batch contient 50 emails
DNS_TIMEOUT = 10    # Timeout for DNS lookups in seconds
SMTP_TIMEOUT = 30   # Timeout for SMTP connections in seconds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Définir SOCKS5 comme proxy
#socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 30003)
#socket.socket = socks.socksocket  # Remplacer le socket par celui qui passe par le proxy

def read_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as html_file:
        html_content = html_file.read()
    return html_content

def resolve_mx_with_timeout(domain, timeout=DNS_TIMEOUT):
    """Resolve MX records with timeout handling."""
    try:
        logger.info(f"Resolving MX records for domain: {domain}")
        
        # Set DNS timeout
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        mx_records = resolver.resolve(domain, 'MX')
        mx_record = sorted(mx_records, key=lambda rec: rec.preference)[0]
        mx_server = str(mx_record.exchange).strip('.')
        
        logger.info(f"Found MX server for {domain}: {mx_server}")
        return mx_server
    except dns.resolver.NXDOMAIN:
        logger.error(f"Domain {domain} does not exist")
        raise
    except dns.resolver.NoAnswer:
        logger.error(f"No MX records found for domain {domain}")
        raise
    except dns.resolver.Timeout:
        logger.error(f"DNS timeout when resolving MX records for {domain}")
        raise
    except Exception as e:
        logger.error(f"DNS resolution failed for {domain}: {e}")
        raise

def get_smtp_connection(mx_server, use_ipv6=True, timeout=SMTP_TIMEOUT):
    """
    Establish SMTP connection with IPv6/IPv4 fallback handling.
    
    Args:
        mx_server: MX server hostname
        use_ipv6: Whether to attempt IPv6 connections
        timeout: Connection timeout in seconds
    
    Returns:
        smtplib.SMTP: Connected SMTP server object
    """
    connection_attempts = []
    
    if use_ipv6:
        # Try IPv6 first
        try:
            logger.info(f"Attempting IPv6 connection to {mx_server}")
            
            # Get IPv6 addresses with timeout
            ipv6_addrs = socket.getaddrinfo(
                mx_server, 25, socket.AF_INET6, 
                socket.SOCK_STREAM, socket.IPPROTO_TCP
            )
            
            if ipv6_addrs:
                ipv6_addr = ipv6_addrs[0][4][0]
                logger.info(f"Found IPv6 address for {mx_server}: {ipv6_addr}")
                
                # Create IPv6 socket with timeout
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                sock.connect((ipv6_addr, 25))
                
                # Create SMTP connection from existing socket
                server = smtplib.SMTP()
                server.sock = sock
                server.file = sock.makefile('rb')
                
                # Complete SMTP handshake
                server.connect(mx_server, 25)
                
                logger.info(f"Successfully connected to {mx_server} via IPv6")
                connection_attempts.append(f"IPv6 ({ipv6_addr}): SUCCESS")
                return server
                
        except socket.gaierror as e:
            error_msg = f"IPv6 DNS resolution failed for {mx_server}: {e}"
            logger.warning(error_msg)
            connection_attempts.append(f"IPv6 DNS: FAILED ({e})")
        except socket.timeout:
            error_msg = f"IPv6 connection timeout to {mx_server}"
            logger.warning(error_msg)
            connection_attempts.append(f"IPv6 connection: TIMEOUT")
        except Exception as e:
            error_msg = f"IPv6 connection failed to {mx_server}: {e}"
            logger.warning(error_msg)
            connection_attempts.append(f"IPv6 connection: FAILED ({e})")
    else:
        logger.info(f"IPv6 disabled, skipping IPv6 attempt for {mx_server}")
        connection_attempts.append("IPv6: SKIPPED (disabled)")
    
    # Try IPv4 fallback
    try:
        logger.info(f"Attempting IPv4 connection to {mx_server}")
        
        # Get IPv4 addresses with timeout
        ipv4_addrs = socket.getaddrinfo(
            mx_server, 25, socket.AF_INET, 
            socket.SOCK_STREAM, socket.IPPROTO_TCP
        )
        
        if ipv4_addrs:
            ipv4_addr = ipv4_addrs[0][4][0]
            logger.info(f"Found IPv4 address for {mx_server}: {ipv4_addr}")
            
            # Create IPv4 socket with timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ipv4_addr, 25))
            
            # Create SMTP connection from existing socket
            server = smtplib.SMTP()
            server.sock = sock
            server.file = sock.makefile('rb')
            
            # Complete SMTP handshake
            server.connect(mx_server, 25)
            
            logger.info(f"Successfully connected to {mx_server} via IPv4")
            connection_attempts.append(f"IPv4 ({ipv4_addr}): SUCCESS")
            return server
            
    except socket.gaierror as e:
        error_msg = f"IPv4 DNS resolution failed for {mx_server}: {e}"
        logger.error(error_msg)
        connection_attempts.append(f"IPv4 DNS: FAILED ({e})")
    except socket.timeout:
        error_msg = f"IPv4 connection timeout to {mx_server}"
        logger.error(error_msg)
        connection_attempts.append(f"IPv4 connection: TIMEOUT")
    except Exception as e:
        error_msg = f"IPv4 connection failed to {mx_server}: {e}"
        logger.error(error_msg)
        connection_attempts.append(f"IPv4 connection: FAILED ({e})")
    
    # All connection attempts failed
    attempts_summary = "; ".join(connection_attempts)
    error_msg = f"All connection attempts failed for {mx_server}. Attempts: {attempts_summary}"
    logger.error(error_msg)
    raise ConnectionError(error_msg)

def send_email_task(q, mx_server, sender_email, sender_name, subject, message, to_email, use_ipv6=True):
    while True:
        batch = q.get()
        if batch is None:
            break  # Arrêter le thread quand on reçoit "None"

        try:
            logger.info(f"Processing batch of {len(batch)} emails via {mx_server}")
            
            # Use improved connection handling
            server = get_smtp_connection(mx_server, use_ipv6=use_ipv6)
            server.ehlo("google.de")

            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, sender_email))
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))

            server.sendmail(sender_email, batch, msg.as_string())
            logger.info(f"Batch of {len(batch)} emails successfully sent via {mx_server}")

            server.quit()
        except ConnectionError as e:
            logger.error(f"Connection failed for batch via {mx_server}: {e}")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error for batch via {mx_server}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for batch via {mx_server}: {e}")
        finally:
            q.task_done()

def prepare_and_send_batches(recipient_emails, subject, message, sender_email, sender_name, to_email, use_ipv6=True):
    """
    Group emails by domain and send them efficiently.
    
    Args:
        recipient_emails: List of recipient email addresses
        subject: Email subject
        message: Email message content
        sender_email: Sender email address
        sender_name: Sender display name
        to_email: To header email address
        use_ipv6: Whether to attempt IPv6 connections
    """
    # Group emails by domain to reduce MX lookups
    domain_groups = defaultdict(list)
    for email in recipient_emails:
        domain = email.split('@')[1]
        domain_groups[domain].append(email)
    
    logger.info(f"Grouped {len(recipient_emails)} emails into {len(domain_groups)} domains")
    
    # Process each domain group
    for domain, emails in domain_groups.items():
        logger.info(f"Processing {len(emails)} emails for domain: {domain}")
        
        try:
            # Resolve MX server for this domain with timeout handling
            mx_server = resolve_mx_with_timeout(domain)
            
            q = queue.Queue()

            # Créer les threads pour envoyer les e-mails
            threads = []
            for _ in range(NUM_THREADS):
                thread = threading.Thread(
                    target=send_email_task, 
                    args=(q, mx_server, sender_email, sender_name, subject, message, to_email, use_ipv6)
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)

            # Ajouter les emails dans la queue par batch
            for i in range(0, len(emails), BATCH_SIZE):
                batch = emails[i:i + BATCH_SIZE]
                q.put(batch)
                logger.info(f"Queued batch {i//BATCH_SIZE + 1} of {len(batch)} emails for {domain}")

            # Attendre que tous les emails soient envoyés
            q.join()

            # Envoyer un signal d'arrêt aux threads
            for _ in range(NUM_THREADS):
                q.put(None)
            
            for thread in threads:
                thread.join()
                
            logger.info(f"Completed processing {len(emails)} emails for domain: {domain}")
            
        except Exception as e:
            logger.error(f"Failed to process emails for domain {domain}: {e}")
            continue

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Send emails with improved IPv6/IPv4 connectivity handling"
    )
    
    parser.add_argument(
        "--no-ipv6",
        action="store_true",
        help="Disable IPv6 connection attempts and use IPv4 only"
    )
    
    parser.add_argument(
        "--emails-file",
        default="mails.txt",
        help="File containing recipient email addresses (default: mails.txt)"
    )
    
    parser.add_argument(
        "--message-file",
        default="message.html",
        help="HTML message file (default: message.html)"
    )
    
    parser.add_argument(
        "--sender-email",
        default="newsletter@amazon-info.de",
        help="Sender email address (default: newsletter@amazon-info.de)"
    )
    
    parser.add_argument(
        "--sender-name",
        default="𝖠𝖬𝖠𝖹𝖮𝖭",
        help="Sender display name (default: 𝖠𝖬𝖠𝖹𝖮𝖭)"
    )
    
    parser.add_argument(
        "--subject",
        default="Sie wurden ausgewählt: Hochwertige Preise für treue Kunden",
        help="Email subject line"
    )
    
    parser.add_argument(
        "--to-email",
        default="newsletter@amazon-info.de",
        help="To header email address (default: newsletter@amazon-info.de)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Configure logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Log configuration
    logger.info("Starting email sending script")
    logger.info(f"IPv6 enabled: {not args.no_ipv6}")
    logger.info(f"DNS timeout: {DNS_TIMEOUT}s")
    logger.info(f"SMTP timeout: {SMTP_TIMEOUT}s")
    logger.info(f"Threads: {NUM_THREADS}")
    logger.info(f"Batch size: {BATCH_SIZE}")
    
    try:
        # Read configuration
        sender_email = args.sender_email
        sender_name = args.sender_name
        subject = args.subject
        message = read_html_file(args.message_file)

        with open(args.emails_file, "r") as file:
            recipient_emails = [line.strip() for line in file.readlines() if line.strip()]

        to_email = args.to_email
        use_ipv6 = not args.no_ipv6

        logger.info(f"Loaded {len(recipient_emails)} recipient emails from {args.emails_file}")

        # Send emails with improved IPv6/IPv4 handling
        prepare_and_send_batches(
            recipient_emails, subject, message, 
            sender_email, sender_name, to_email, 
            use_ipv6=use_ipv6
        )
        
        logger.info("Email sending completed successfully")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)
