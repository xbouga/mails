import smtplib
import dns.resolver
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import threading
import queue
import socks
import socket

NUM_THREADS = 150  # Fixer le nombre de threads à 100
BATCH_SIZE = 200    # Chaque batch contient 50 emails
USE_IPV4_ONLY = True  # Skip IPv6 and use only IPv4 for faster connections

# Définir SOCKS5 comme proxy
#socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 30003)
#socket.socket = socks.socksocket  # Remplacer le socket par celui qui passe par le proxy

def read_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as html_file:
        html_content = html_file.read()
    return html_content

def create_smtp_connection(mx_server, use_ipv4_only=True):
    """Create SMTP connection with IPv4/IPv6 handling"""
    if use_ipv4_only:
        # Force IPv4 connection
        try:
            # Get IPv4 addresses only
            addresses = socket.getaddrinfo(mx_server, 25, socket.AF_INET, socket.SOCK_STREAM)
            if addresses:
                ipv4_addr = addresses[0][4][0]
                server = smtplib.SMTP()
                server.connect(ipv4_addr, 25)
                return server
        except Exception as e:
            print(f"IPv4 connection failed to {mx_server}: {e}")
            raise
    else:
        # Default behavior (tries IPv6 first, then IPv4)
        return smtplib.SMTP(mx_server)

def is_smtp_success_code(code):
    """Check if SMTP response code indicates success"""
    return 200 <= code < 300

def send_email(server, sender_email, recipient_emails, msg_string):
    """Send email with proper SMTP response code handling"""
    try:
        # Send to multiple recipients
        refused = server.sendmail(sender_email, recipient_emails, msg_string)
        
        # Check if any recipients were refused
        if refused:
            print(f"Some recipients were refused: {refused}")
            return False
        else:
            return True
            
    except smtplib.SMTPResponseException as e:
        # Handle SMTP response exceptions properly
        if is_smtp_success_code(e.smtp_code):
            # This is actually a success response (like 250)
            print(f"Email sent successfully (SMTP {e.smtp_code}: {e.smtp_error})")
            return True
        else:
            # This is an actual error
            print(f"SMTP Error {e.smtp_code}: {e.smtp_error}")
            return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_email_task(q, mx_server, sender_email, sender_name, subject, message, to_email):
    while True:
        batch = q.get()
        if batch is None:
            break  # Arrêter le thread quand on reçoit "None"

        try:
            # Use improved SMTP connection with IPv4-first approach
            server = create_smtp_connection(mx_server, use_ipv4_only=USE_IPV4_ONLY)
            server.ehlo("google.de")

            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, sender_email))
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))

            # Use improved email sending with proper response code handling
            success = send_email(server, sender_email, batch, msg.as_string())
            
            if success:
                print(f"Batch of {len(batch)} emails successfully sent.")
            else:
                print(f"Failed to send batch of {len(batch)} emails.")

            server.quit()
        except Exception as e:
            print(f"Failed to send email batch: {e}")
        finally:
            q.task_done()

def prepare_and_send_batches(recipient_emails, subject, message, sender_email, sender_name, to_email):
    domain = recipient_emails[0].split('@')[1]
    mx_records = dns.resolver.resolve(domain, 'MX')
    mx_record = sorted(mx_records, key=lambda rec: rec.preference)[0]
    mx_server = str(mx_record.exchange).strip('.')

    q = queue.Queue()

    # Créer les threads pour envoyer les e-mails
    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=send_email_task, args=(q, mx_server, sender_email, sender_name, subject, message, to_email))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Ajouter les emails dans la queue par batch de 50
    for i in range(0, len(recipient_emails), BATCH_SIZE):
        batch = recipient_emails[i:i + BATCH_SIZE]
        q.put(batch)

    # Attendre que tous les emails soient envoyés
    q.join()

    # Envoyer un signal d'arrêt aux threads
    for _ in range(NUM_THREADS):
        q.put(None)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    sender_email = "newsletter@amazon-info.de"
    sender_name = "𝖠𝖬𝖠𝖹𝖮𝖭"
    subject = "Sie wurden ausgewählt: Hochwertige Preise für treue Kunden"
    message = read_html_file("message.html")

    with open("mails.txt", "r") as file:
        recipient_emails = [line.strip() for line in file.readlines()]

    to_email = "newsletter@amazon-info.de"

    # Envoyer les emails avec 100 threads fixes et batch de 50 emails
    prepare_and_send_batches(recipient_emails, subject, message, sender_email, sender_name, to_email)
