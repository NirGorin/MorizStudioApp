from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from .database import Base
from .enums import RoleEnum, GenderEnum 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(30), index=True)
    last_name  = Column(String(30), index=True)
    username   = Column(String(30), unique=True, index=True)
    email      = Column(String(50), unique=True, index=True)
    hashed_password = Column(String)
    role = Column(PgEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.trainee)
    phone_number = Column(String(15), unique=True, index=True)

    studio_id = Column(Integer, ForeignKey("studios.id", ondelete="SET NULL"), index=True)
    studio    = relationship("Studio", backref="users")

    trainee_profile = relationship(
        "TraineeProfile",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",   
        passive_deletes=True
    )


class Studio(Base):
    __tablename__ = "studios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    studio_email = Column(String, unique=True, index=True)


class TraineeProfile(Base):
    __tablename__ = "trainee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    gender = Column(PgEnum(GenderEnum, name="gender_enum"), nullable=False)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    level = Column(String(15))
    number_of_week_training = Column(Integer)
    limitations = Column(Text, nullable=True)

    ai_status  = Column(String(16), default="idle", nullable=False)
    ai_summary = Column(Text)
    ai_json    = Column(Text)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    user    = relationship("User", back_populates="trainee_profile")

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_trainee_profiles_user_id"),
    )