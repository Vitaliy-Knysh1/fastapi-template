from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.crud import user as user_crud
from app.schemas.auth import LoginRequest, MessageResponse, RegisterRequest
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"message": "auth ok"}


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: DbSession) -> UserPublic:
    exists = await user_crud.get_user_by_email(db, str(payload.email))
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    try:
        user = await user_crud.create_user_with_password(
            db,
            email=str(payload.email),
            name=payload.name,
            password_hash=hash_password(payload.password),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    return UserPublic.model_validate(user)


@router.post("/login")
async def login(payload: LoginRequest, db: DbSession, response: Response) -> dict[str, object]:
    user = await user_crud.get_user_by_email(db, str(payload.email))
    if user is None or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(sub=str(user.id))
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite=settings.cookie_samesite,  # type: ignore[arg-type]
        secure=settings.cookie_secure,
        path="/",
    )
    return {"user": UserPublic.model_validate(user).model_dump(mode="json")}


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response) -> MessageResponse:
    response.delete_cookie(settings.auth_cookie_name, path="/")
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=UserPublic)
async def auth_me(user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(user)
