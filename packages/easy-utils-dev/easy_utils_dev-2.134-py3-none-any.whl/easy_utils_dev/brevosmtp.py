
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()

html_content = """
    <html>
    <head>
      <style>
        .email-container {
          font-family: Arial, sans-serif;
          background-color: #f4f4f4;
          padding: 20px;
        }

        .email-box {
          background-color: #ffffff;
          padding: 30px;
          border-radius: 8px;
          max-width: 600px;
          margin: auto;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }

        .message {
          font-size: 16px;
          margin-bottom: 20px;
          color: #333333;
        }

        .button {
          display: inline-block;
          padding: 12px 24px;
          margin: 10px 10px 0 0;
          font-size: 14px;
          text-decoration: none;
          border-radius: 6px;
          color: white;
          font-weight: bold;
        }

        .approve {
          background-color: #28a745;
        }

        .reject {
          background-color: #dc3545;
        }

        .footer {
          font-size: 12px;
          color: #888888;
          margin-top: 30px;
          text-align: center;
        }
      </style>
    </head>
    <body>
      <div class="email-container">
        <div class="email-box">
          <p class="message">
            There is a <strong>license request</strong> awaiting your action.
          </p>

          <a href="https://yourdomain.com/approve-request" class="button approve">Approve</a>
          <a href="https://yourdomain.com/reject-request" class="button reject">Reject</a>

          <p class="footer">
            This is an automated message. Please do not reply.
          </p>
        </div>
      </div>
    </body>
    </html>
    """

def send_email( subject, body, to_emails=[]):
    # Gmail SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    # Your Gmail credentials
    from_email = os.environ.get('SMTP_APP_USERNAME')
    password = os.environ.get('SMTP_APP_PASSWORD')  # Or use an app-specific password if 2FA is enabled
    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'html'))

    try:
        # Set up the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(from_email, password)  # Log in to the Gmail server

        # Send the email
        response = server.sendmail(from_email,to_emails , msg.as_string())
        print("Sendmail response:", response)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise
    finally:
        # Close the server connection
        server.quit()

# # Example usage
# send_email("Test Subject", "This is the body of the email.",[ 'ahmed.a.abdelhamid.ext@nokia.com' , 'elmeddany@gmail.com'])
