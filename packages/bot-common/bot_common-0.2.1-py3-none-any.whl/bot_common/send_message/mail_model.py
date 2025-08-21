from pydantic import BaseModel


class SendMailRequest(BaseModel):
    target_address_ls: list = []
    mail_title: str = ''
    mail_body: str = ''


class SenderMailConfig(BaseModel):
    sender_address: str
    sender_password: str
    provider_address: str = 'smtp.gmail.com'
    provider_port: int = 587
