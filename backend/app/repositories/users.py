import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_keycloak_id(self, keycloak_id: str) -> User | None:
        stmt = select(User).where(User.keycloak_id == keycloak_id)
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()

    def search(self, query: str, limit: int = 20) -> list[User]:
        stmt = (
            select(User)
            .where(
                User.is_active.is_(True),
                (User.email.ilike(f"%{query}%")) | (User.display_name.ilike(f"%{query}%")),
            )
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, keycloak_id: str, email: str, display_name: str | None = None) -> User:
        user = User(keycloak_id=keycloak_id, email=email, display_name=display_name)
        self.db.add(user)
        self.db.flush()
        return user

    def list_all(self, offset: int = 0, limit: int = 50) -> list[User]:
        stmt = select(User).offset(offset).limit(limit).order_by(User.created_at.desc())
        return list(self.db.scalars(stmt).all())
