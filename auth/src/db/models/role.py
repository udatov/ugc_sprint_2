from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class Role(Base):
    name = Column(String, unique=True, nullable=False, index=True)

    user = relationship(
        "UserRole", back_populates="role", cascade="all, delete", passive_deletes=True
    )


class UserRole(Base):
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"), nullable=False)

    role = relationship("Role", back_populates="user")
    user = relationship("User", back_populates="role")
