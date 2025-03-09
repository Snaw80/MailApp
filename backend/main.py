from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import imaplib
import email
from email.header import decode_header
from email import policy
from email.parser import BytesParser

from bs4 import BeautifulSoup
import re

from dotenv import load_dotenv
import os 


load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

app = FastAPI()

# Mock database (remplacer par une vraie DB en production)
whitelist_db = set()

class WhitelistEmail(BaseModel):
    email: str

@app.post("/whitelist")
async def add_to_whitelist(email: WhitelistEmail):
    whitelist_db.add(email.email)
    return {"message": f"{email.email} added to whitelist"}

@app.get("/whitelist")
async def get_whitelist():
    return {"whitelist": list(whitelist_db)}

@app.get("/newsletters")
async def get_newsletters():
    newsletters = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        if mail.state != 'AUTH':
            raise HTTPException(status_code=500, detail="Could not authenticate")
        
        mail.select("inbox")

        for sender in whitelist_db:
            status, data = mail.search(None, f'FROM "{sender}"')
            if status == 'OK':
                email_ids = data[0].split()
                email_ids = email_ids[-10:] # On ne récupère que les 5 derniers emails
                for num in email_ids:
                    _, data = mail.fetch(num, '(RFC822)')
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    newsletter = process_newsletter(msg)
                    newsletters.append(newsletter)
        
        mail.close()
        mail.logout()
        newsletters.reverse()
        
        return {"newsletters": newsletters}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def decode_subject(subject):
    """Decode the email subject line."""
    decoded_parts = decode_header(subject)
    decoded_subject = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_subject += part.decode(encoding or "utf-8", errors="replace")
        else:
            decoded_subject += part
    return decoded_subject

def process_email_content(content):
    """Process email content to improve formatting and link handling"""
    # Convert newlines to HTML line breaks
    content = content.replace('\n', '<br>')
    
    # Remove excessive whitespace and non-breaking spaces
    content = re.sub(r'[\s‌]+', ' ', content)  # Match regular and non-breaking spaces
    content = re.sub(r'(<br>){2,}', '<br><br>', content)  # Limit consecutive line breaks
    
    # Convert plain text links to HTML links
    content = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', content)
    
    return content

def extract_email_content(msg):
    """Extract and process email content with improved formatting"""
    content = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ['text/plain', 'text/html']:
                payload = part.get_payload(decode=True).decode()
                if content_type == 'text/plain':
                    payload = process_email_content(payload)
                elif content_type == 'text/html':
                    soup = BeautifulSoup(payload, 'html.parser')
                    payload = soup.prettify()
                content += payload
                break
    else:
        content = msg.get_payload(decode=True).decode()
        if msg.get_content_type() == 'text/plain':
            content = process_email_content(content)
    
    # Handle footnote references [1], [2], etc.
    content = re.sub(r'\[(\d+)\]', r'<sup>[\1]</sup>', content)
    
    return content

def process_newsletter(msg):
    subject = decode_subject(msg["Subject"])
    content = extract_email_content(msg)

    return {
        "id": msg["Message-ID"],
        "from": msg["From"],
        "date": msg["Date"],
        "subject": subject,
        "content": content,
        "links": extract_links(msg)
    }


def extract_links(msg):
    # Logique pour extraire les liens
    pass