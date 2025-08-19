from email.mime.base import MIMEBase
import smtplib
from smtplib import SMTPDataError
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from os import path

from send_mail.ConfigParser import ConfigHandler as ConfigParser


class SendMail:
    @staticmethod
    def send_email(email_message: str, subject: str, email_recepients: list, file_attachments=[], attempt=0, email_server='email_server',extra_email_server = 'secondary_server'): 
        try:
            if attempt <= 0:
                attempt = 0

            if attempt <= 1 and attempt >= 0:
                config = ConfigParser('.config.ini', email_server)
                params = config.read_config()
            elif attempt < 5 and attempt > 1:
                if extra_email_server is None:
                    raise Exception("No Secondary Email Server Name provided")
                
                config = ConfigParser('.config.ini', extra_email_server)
                params = config.read_config()
            else:
                raise Exception("Emailing attempt stopped at 5 tries")

        except Exception as e:
            raise e

     

        try:
            port = params['port']
            smtp_server = params['smtp_server']
            sender_email = params['sender_email']
            login_email = params['sender_username']
            password = params['password']
            platform = params['platform']
            Bcc = ''

            message = MIMEMultipart()
            message['Subject'] = '%s' % (subject)
            message['From'] = sender_email
            message['To'] = ", ".join(email_recepients)
            message['Cc'] = None

            html = '''
            <html>
            <head></head>
            <body>
            <p>Hello All,
            <br> 
            %s 
            </p>
            </body>
            </html>
            ''' %(email_message)

            message.attach(MIMEText(html, 'html'))
            if file_attachments is not None or len(file_attachments) > 0:
                for filename in file_attachments:
                    if path.isdir(path.split(filename)[0]):
                        filenamex = path.split(filename)[-1]
                    else:
                        filenamex = filename
                    with open(filename, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)

                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={filenamex}',
                    )

                    message.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                print('sending mail started.....')
                server.starttls(context=context)
                server.login(login_email, password)
                server.sendmail(sender_email, email_recepients, message.as_string())
                print('sending mail ended.....')
        
        except SMTPDataError as e:
            if attempt == 0:
                print(f"SMTPDataError occurred, retrying attempt 2")
                SendMail.send_email(email_message, subject, email_recepients, file_attachments, attempt=attempt+1, email_server=email_server,extra_email_server=extra_email_server)
            elif attempt < 5 and attempt > 0:
                print(f"SMTPDataError occurred, retrying attempt {attempt+2}")
                SendMail.send_email(email_message, subject, email_recepients, file_attachments, attempt=attempt+1, extra_email_server=extra_email_server)
            else:
                error_code, error_message = e.smtp_code, e.smtp_error
                
                print(f"SMTPDataError after {attempt+1} retries: ({error_code}, {error_message})")
                return {'code':error_code,'message':error_message}

        
        return {'code':200,'message':'Email should be sent successfully.'}