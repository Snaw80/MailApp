from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

app = FastAPI()

# Charger les variables d'environnement
load_dotenv()

# Configuration
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str

@app.post("/send-email")
async def send_email(email_request: EmailRequest):
    try:
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email_request.to
        msg['Subject'] = email_request.subject
        msg.attach(MIMEText(email_request.body, 'plain'))

        # Connexion au serveur SMTP
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, email_request.to, msg.as_string())
        
        return {"message": "Email envoyé avec succès"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inbox")
async def get_inbox(limit: int = 10):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        _, data = mail.search(None, 'ALL')
        email_ids = data[0].split()

        # Tri numérique descendant
        email_ids = sorted(email_ids, key=lambda x: int(x), reverse=True)
        emails = []

        def decode_body(part):
            charset = part.get_content_charset() or 'utf-8'
            try:
                return part.get_payload(decode=True).decode(charset, errors='replace')
            except UnicodeDecodeError:
                try:
                    return part.get_payload(decode=True).decode('latin-1', errors='replace')
                except:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')

        for num in email_ids[:limit]:
            _, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8', errors='replace')

            from_, encoding = decode_header(msg.get("From"))[0]
            if isinstance(from_, bytes):
                from_ = from_.decode(encoding or 'utf-8', errors='replace')

            date = msg.get("Date")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = decode_body(part)
                        break
            else:
                body = decode_body(msg)

            emails.append({
                "date": date,
                "subject": subject,
                "from": from_,
                "body": body
            })

        mail.close()
        mail.logout()
        
        return {"emails": emails}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inbox-from")
async def get_inbox_from(
    sender: str = Query(..., description="Adresse email de l'expéditeur"),
    limit: int = Query(10, description="Nombre maximum d'emails à retourner")
):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        # Recherche des emails de l'expéditeur spécifié
        status, data = mail.search(None, f'FROM "{sender}"')
        if status != 'OK':
            raise HTTPException(status_code=500, detail="Échec de la recherche IMAP")

        email_ids = data[0].split()
        
        # Tri numérique descendant
        email_ids = sorted(email_ids, key=lambda x: int(x), reverse=True)

        emails = []

        def decode_body(part):
            charset = part.get_content_charset() or 'utf-8'
            try:
                return part.get_payload(decode=True).decode(charset, errors='replace')
            except UnicodeDecodeError:
                try:
                    return part.get_payload(decode=True).decode('latin-1', errors='replace')
                except:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')

        for num in email_ids[:limit]:
            _, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8', errors='replace')

            from_, encoding = decode_header(msg.get("From"))[0]
            if isinstance(from_, bytes):
                from_ = from_.decode(encoding or 'utf-8', errors='replace')

            date = msg.get("Date")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = decode_body(part)
                        break
            else:
                body = decode_body(msg)

            emails.append({
                "date": date,
                "subject": subject,
                "from": from_,
                "body": body
            })

        mail.close()
        mail.logout()
        
        return {
            "sender": sender,
            "total_emails": len(email_ids),
            "emails": emails[:limit]
        }
    
    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=500, detail=f"Erreur IMAP : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur inattendue : {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)