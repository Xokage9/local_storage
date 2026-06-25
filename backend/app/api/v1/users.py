from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, get_user_repo
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.user import UserRead, UserSearch

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserRead)
def get_current_user_profile(user: User = Depends(get_current_user)):
    return user


@router.get("/users/search", response_model=list[UserSearch])
def search_users(
    q: str = Query(..., min_length=1),
    user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    results = user_repo.search(q)
    return [r for r in results if r.id != user.id]
