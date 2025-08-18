from sqlmodel import SQLModel


class NewTOTP(SQLModel):
    secret: str
    key: str
    uri: str


class NewTOTPResponse(SQLModel):
    key: str
    uri: str


class EnableTOTP(SQLModel):
    claim: str
    uri: str
    password: str | None = None
