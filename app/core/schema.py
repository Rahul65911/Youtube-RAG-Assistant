from pydantic import BaseModel, EmailStr, field_validator
import re

class YoutubeIngestRequest(BaseModel):
    video_id: str

class ChatRequest(BaseModel):
    video_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str

USERNAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{2,19}$")
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$"
)

class LoginRequest(BaseModel):
    username: str
    password: str

class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if not USERNAME_REGEX.match(v):
            raise ValueError(
                "Username must start with a letter and contain 3–20 "
                "letters, numbers, or underscores only"
            )
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long and include "
                "uppercase, lowercase, number, and special character"
            )
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"