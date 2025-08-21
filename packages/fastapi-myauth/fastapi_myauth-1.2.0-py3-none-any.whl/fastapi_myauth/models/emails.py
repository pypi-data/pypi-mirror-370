from pydantic import EmailStr
from sqlmodel import SQLModel


class EmailContent(SQLModel):
    email: EmailStr
    subject: str
    content: str


class EmailValidation(SQLModel):
    email: EmailStr
    subject: str
    token: str
