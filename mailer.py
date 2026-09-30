import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(gmail_address, gmail_app_password, to_address, user_name, summary):
    """
    Sends an expense summary email using Gmail SMTP (SSL on port 465).
    """
    if not gmail_address or not gmail_app_password:
        return False, "Gmail credentials not configured in secrets.toml"
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🧾 ReceiptSnap Summary for {user_name}"
        msg["From"] = gmail_address
        msg["To"] = to_address

        # Plain text content
        text_body = f"Hi {user_name},\n\nHere is your expense summary from ReceiptSnap:\n\n{summary}\n\n---\nSent via ReceiptSnap AI"
        
        # HTML content for rich rendering
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px;">
              <h2 style="color: #2E7D32;">🧾 ReceiptSnap Expense Summary</h2>
              <p>Hi <strong>{user_name}</strong>,</p>
              <p>Here is your expense & bill-splitting breakdown:</p>
              <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #2E7D32; font-family: monospace; white-space: pre-wrap;">
{summary}
              </div>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
              <p style="font-size: 0.8em; color: #777;">Generated automatically by ReceiptSnap with Gemini AI.</p>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, gmail_app_password)
            server.send_message(msg)
            
        return True, "Email sent successfully!"
    except Exception as error:
        return False, str(error)
