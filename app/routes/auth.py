from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.schema import TokenResponse, LoginRequest, SignUpRequest

from app.db.session import get_db
from app.auth.users import authenticate_user, get_user_by_username, create_user, get_user_by_email
from app.auth.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", status_code=201)
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    if get_user_by_username(db, req.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    if get_user_by_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    create_user(db, req.username, req.email, req.password)

    return {"message": "User Created Successfully"}

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)
