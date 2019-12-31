import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
import time
import os
from common.yaml_functions import read_yaml


class MAIL:
    def __init__(self,host,port,sender,pwd):
        self.host=host
        self.port=port
        self.sender=sender
        self.pwd=pwd
        self.connection=None

    def connect(self):
        smtpObj = smtplib.SMTP_SSL(self.host, self.port)
        smtpObj.login(self.sender,self.pwd)
        self.connection=smtpObj

    def close(self):
        self.connection.quit()

    @staticmethod
    def get_attachment_obj(file_name):
        with open(file_name, 'rb') as f:
            mime = MIMEBase('text', 'txt', filename=file_name)
            mime.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_name))
            mime.set_payload(f.read())
            encoders.encode_base64(mime)
            return mime

    def send_mail(self,subject,content,receivers,ccs,attachment_file):
        message = MIMEMultipart()
        message.attach(MIMEText(content, 'html', 'utf-8'))
        message['From'] = self.sender
        message['To'] = ','.join(receivers)
        message['Cc'] = ','.join(ccs)
        message['Subject'] = subject
        message.attach(self.get_attachment_obj(attachment_file))
        self.connection.sendmail(self.sender, receivers+ccs, str(message))


def send_mail_163(subject,content,attachment):
    config_path=r".\config\mail_config_163.yml"
    if os.path.exists(config_path):
        configs=read_yaml(config_path)
    else:
        return False
    my_host =configs.get("my_host")
    my_pass = configs.get("my_pass")
    my_sender = configs.get("my_sender")
    my_receivers = configs.get("my_receivers")
    my_ccs = []
    my_attachment_file =attachment
    my_port = 465
    my_subject = subject
    my_content = content
    mail = MAIL(my_host, my_port, my_sender, my_pass)
    mail.connect()
    mail.send_mail(my_subject, my_content, my_receivers, my_ccs, my_attachment_file)
    mail.close()
    return True


def send_mail_qq(subject,content,attachment):
    config_path=r".\config\mail_config_qq.yml"
    if os.path.exists(config_path):
        configs=read_yaml(config_path)
    else:
        return False
    my_host =configs.get("my_host")
    my_pass = configs.get("my_pass")
    my_sender = configs.get("my_sender")
    my_receivers = configs.get("my_receivers")
    my_ccs = []
    my_attachment_file = attachment
    my_port = 465
    my_subject = subject
    my_content = content
    mail = MAIL(my_host, my_port, my_sender, my_pass)
    mail.connect()
    mail.send_mail(my_subject, my_content, my_receivers, my_ccs, my_attachment_file)
    mail.close()
    return True