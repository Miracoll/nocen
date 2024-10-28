from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import subprocess
import datetime
import zipfile

from django.conf import settings

from account.models import Log

def tupleToDict(fieldName, value):
    if len(fieldName) == len(value):
        return dict(zip(fieldName, value))
    else:
        return 'unmatch length'
    
def numberToAlphabet(number):
    if 1 <= number <= 26:
        return chr(number + 64)
    else:
        return None
    
def backupMysqlDatabase(database_name, backup_path):
    # Define the backup file name with the current date
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_path}/{database_name}_backup_{date_str}.sql"
    newFilePath = f"{backup_path}/zipped/{database_name}_backup_{date_str}.zip"
    
    # Construct the mysqldump command without specifying user and password
    # Remember to setup the .my.cnf file
    command = [
        "mysqldump",
        database_name
    ]
    
    try:
        # Run mysqldump and capture the output
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        
        # Write the output to the backup file
        with open(backup_file, "wb") as file:
            file.write(output)
        
        print(f"Backup successful! File saved to: {backup_file}")
        zipFile(backup_file, newFilePath)
        return newFilePath
    
    except subprocess.CalledProcessError as e:
        # Print detailed error message if mysqldump fails
        print(f"Error during backup: {e.output.decode().strip()}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def sendFile(path,subject,body,recipient_email):
    sender_email = settings.EMAIL
    sender_password = settings.PASSWORD
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    body_part = MIMEText(body)
    message.attach(body_part)

    with open(path, 'rb') as file:
        message.attach(MIMEApplication(file.read(), Name='backup.zip'))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

def zipFile(file_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        zipf.write(file_path)
    return zip_file_path

def sendEmail(toEmail, subject, user, code):
    message = render_to_string('account/confirm_email.html', {
            'l_user':user.last_name,
            'f_user':user.first_name,
            'code':code,
        }
    )
    # email = EmailMessage(mail_subject, message, to=[to_email])
    email = EmailMultiAlternatives(subject, message, to=[toEmail])
    email.attach_alternative(message, "text/html")
    email.content_subtype = 'html'
    check = email.send()
    return check

def getIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP if there are multiple
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def createLog(actionPerformed,status,user):
    Log.objects.create(action=actionPerformed,is_success=status,ip_address=user.last_login_ip,user=user)