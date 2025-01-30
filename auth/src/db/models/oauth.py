from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class OauthProvider(Base):
    name = Column(String, unique=True, nullable=False, index=True)

    user = relationship(
        "UserOauthProvider",
        back_populates="oauthprovider",
        cascade="all, delete",
        passive_deletes=True,
    )


class UserOauthProvider(Base):
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    oauthprovider_id = Column(
        UUID(as_uuid=True), ForeignKey("oauthprovider.id"), nullable=False
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)

    oauthprovider = relationship("OauthProvider", back_populates="user")
    user = relationship("User", back_populates="oauthprovider")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
