# app/core/dependencies.py
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_token


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    from app.models.user import User
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user or not user.is_active:
        return None
    return user


def flash(request: Request, type: str, message: str):
    request.session["_flash"] = {"type": type, "message": message}


def get_flash(request: Request):
    return request.session.pop("_flash", None)
