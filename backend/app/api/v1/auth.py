from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.auth.keycloak import keycloak_client
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(tags=["auth"])


@router.get("/auth/config")
def get_auth_config():
    return keycloak_client.get_openid_config()


@router.get("/auth/me", response_model=UserRead)
def get_me(user: User = Depends(get_current_user)):
    return user
