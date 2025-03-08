from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
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

def process_newsletter(msg):
    subject = decode_subject(msg["Subject"])
    # Convertit un email en format newsletter standard
    return {
        "id": msg["Message-ID"],
        "from": msg["From"],
        "date": msg["Date"],
        "subject": subject,
        "content": extract_content(msg),
        "links": extract_links(msg)
    }

def extract_content(msg):
    # Logique pour extraire le contenu principal
    pass

def extract_links(msg):
    # Logique pour extraire les liens
    pass