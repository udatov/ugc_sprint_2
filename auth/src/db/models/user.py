from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .base import Base


class User(Base):
    login = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    is_superuser = Column(Boolean, default=False)

    role = relationship(
        "UserRole", back_populates="user", cascade="all, delete", passive_deletes=True
    )
    history = relationship(
        "History", back_populates="user", cascade="all, delete", passive_deletes=True
    )
    oauthprovider = relationship(
        "UserOauthProvider",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password: str) -> bool:
        self.password = generate_password_hash(password)

    def __repr__(self) -> str:
        return f"<User {self.login}>"


class History(Base):
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="history")
