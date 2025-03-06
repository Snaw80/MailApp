import imaplib
import email
from email.header import decode_header

import re

from dotenv import load_dotenv
import os 


load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

email_whitelist = ['dan@tldrnewsletter.com']

def get_recent_emails(max_emails=20):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    
    try:
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')

        status, data = mail.uid('search', None, 'ALL')
        if status != 'OK':
            print("Erreur lors de la recherche")
            return []

        email_uids = data[0].split()
        email_uids = [int(uid) for uid in email_uids]
        email_uids.sort(reverse=True)  # Tri décroissant pour avoir les plus récents d'abord
        latest_uids = email_uids[:max_emails]

        emails = []
        for uid in latest_uids:
            # Récupération par UID
            status, msg_data = mail.uid('fetch', str(uid), '(RFC822)')
            if status != 'OK':
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = decode_header(msg["Subject"])[0][0]
            subject = subject.decode() if isinstance(subject, bytes) else subject

            from_ = decode_header(msg.get("From"))[0][0]
            from_ = from_.decode() if isinstance(from_, bytes) else from_
            
            match = re.search(r'[\w\.-]+@[\w\.-]+', from_)
            if (match is None) or (match.group() not in email_whitelist):
                continue 

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    try:
                        body_part = part.get_payload(decode=True).decode()
                    except:
                        continue
                    if content_type == "text/plain":
                        body = body_part
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            emails.append({
                'uid': uid,
                'subject': subject,
                'from': from_,
                'date': msg.get("Date"),
                'body': body
            })

        return emails

    except Exception as e:
        print(f"Erreur: {str(e)}")
        return []
    finally:
        try:
            mail.close()
        except:
            pass
        mail.logout()

if __name__ == "__main__":
    emails = get_recent_emails()
    for i, email in enumerate(emails):
        print(f"Email #{i+1}")
        print(f"UID: {email['uid']}")
        print(f"De: {email['from']}")
        print(f"Sujet: {email['subject']}")
        print(f"Date: {email['date']}")
        print(f"Corps: {email['body']}...\n")

