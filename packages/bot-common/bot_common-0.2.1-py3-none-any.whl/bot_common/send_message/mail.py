from bot_common.send_message.mail_model import SendMailRequest, SenderMailConfig
from bot_common.utils import logger, catch_exception
import smtplib


class MailSender:
    def __init__(self, mail_sender: SenderMailConfig, mail_req: SendMailRequest):
        self.mail_sender = mail_sender
        self.req = mail_req

    @catch_exception
    def send(self):
        out_message = f'Subject: {self.req.mail_title}\n\n{self.req.mail_body}'
        server = smtplib.SMTP(self.mail_sender.provider_address, self.mail_sender.provider_port)
        server.starttls()
        server.login(self.mail_sender.sender_address, self.mail_sender.sender_password)
        for receiver_address in self.req.target_address_ls:
            server.sendmail(self.mail_sender.sender_address, receiver_address, out_message.encode('utf-8'))
        server.quit()
