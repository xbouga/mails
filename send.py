import smtplib
import dns.resolver
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import threading
import queue
import socks
import socket

NUM_THREADS = 150  # Number of threads
BATCH_SIZE = 200   # Emails per batch

# Optional: SOCKS5 proxy
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 30003)
# socket.socket = socks.socksocket

def read_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as html_file:
        html_content = html_file.read()
    return html_content

def send_email_task(q, mx_server, sender_email, sender_name, subject, message, to_email):
    while True:
        batch = q.get()
        if batch is None:
            break  # Stop thread when None is received

        try:
            server = smtplib.SMTP(mx_server)
            server.ehlo("noez.de")

            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, sender_email))
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))

            server.sendmail(sender_email, batch, msg.as_string())
            print("Batch of {} emails successfully sent.".format(len(batch)))

            server.quit()
        except Exception as e:
            print("Failed to send email batch: {}".format(e))
        finally:
            q.task_done()

def prepare_and_send_batches(recipient_emails, subject, message, sender_email, sender_name, to_email):
    domain = recipient_emails[0].split('@')[1]
    # Use dns.resolver.query() for dnspython 1.x compatibility
    mx_records = dns.resolver.query(domain, 'MX')
    mx_record = sorted(mx_records, key=lambda rec: rec.preference)[0]
    mx_server = str(mx_record.exchange).strip('.')

    q = queue.Queue()

    # Create threads to send emails
    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(
            target=send_email_task,
            args=(q, mx_server, sender_email, sender_name, subject, message, to_email)
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Add emails to queue by batches
    for i in range(0, len(recipient_emails), BATCH_SIZE):
        batch = recipient_emails[i:i + BATCH_SIZE]
        q.put(batch)

    # Wait for all emails to be sent
    q.join()

    # Send stop signal to threads
    for _ in range(NUM_THREADS):
        q.put(None)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    sender_email = "kontakt@mail-info.de"
    sender_name = "𝗔𝗗𝗔𝗖"
    subject = "Limitierte Aktion: Ihr Auto-Notfallset kostenlos"
    message = read_html_file("message.html")

    with open("mails.txt", "r") as file:
        recipient_emails = [line.strip() for line in file.readlines()]

    to_email = "kontakt@mail-info.de"

    # Send emails with NUM_THREADS and BATCH_SIZE
    prepare_and_send_batches(recipient_emails, subject, message, sender_email, sender_name, to_email)
