from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import TOKEN_TTL_SECONDS, create_access_token, get_current_user, hash_password, require_admin, verify_password
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import ChangePasswordRequest, CreateUserRequest, LoginRequest, LoginResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "INVALID_CREDENTIALS"})
    return LoginResponse(access_token=create_access_token(user), expires_in=TOKEN_TTL_SECONDS, user=user)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/change-password", status_code=204)
def change_password(payload: ChangePasswordRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect", headers={"X-Error-Code": "CURRENT_PASSWORD_INVALID"})
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from the current password", headers={"X-Error-Code": "PASSWORD_UNCHANGED"})
    user.password_hash = hash_password(payload.new_password)
    db.commit()


@router.get("/users", response_model=list[UserResponse])
def list_users(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(payload: CreateUserRequest, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)) is not None:
        raise HTTPException(status_code=409, detail="A user with this email already exists", headers={"X-Error-Code": "USER_EXISTS"})
    if payload.role == "BUSINESS_OWNER" and payload.business_id is None:
        raise HTTPException(status_code=422, detail="business_id is required for a business owner", headers={"X-Error-Code": "BUSINESS_REQUIRED"})
    if payload.business_id is not None:
        from backend.app.models.business import Business
        if db.get(Business, payload.business_id) is None:
            raise HTTPException(status_code=404, detail="Business not found", headers={"X-Error-Code": "BUSINESS_NOT_FOUND"})
    user = User(email=payload.email, password_hash=hash_password(payload.password), full_name=payload.full_name.strip(), role=payload.role, business_id=payload.business_id, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found", headers={"X-Error-Code": "USER_NOT_FOUND"})
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own admin account", headers={"X-Error-Code": "SELF_DEACTIVATION_FORBIDDEN"})
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
