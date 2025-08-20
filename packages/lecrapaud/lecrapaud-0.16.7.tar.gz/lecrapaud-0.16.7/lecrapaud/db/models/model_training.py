from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Float,
    JSON,
    Table,
    ForeignKey,
    BigInteger,
    Index,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy import desc, asc, cast, text, func

from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase

from lecrapaud.db.session import get_db
from lecrapaud.db.models.base import Base
from lecrapaud.config import LECRAPAUD_TABLE_PREFIX


class ModelTraining(Base):

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    best_params = Column(JSON)
    model_path = Column(String(255))
    training_time = Column(Integer)
    model_id = Column(
        BigInteger, ForeignKey(f"{LECRAPAUD_TABLE_PREFIX}_models.id"), nullable=False
    )
    model_selection_id = Column(
        BigInteger,
        ForeignKey(f"{LECRAPAUD_TABLE_PREFIX}_model_selections.id", ondelete="CASCADE"),
        nullable=False,
    )

    model = relationship("Model", lazy="selectin")
    model_selection = relationship(
        "ModelSelection", back_populates="model_trainings", lazy="selectin"
    )
    score = relationship(
        "Score",
        back_populates="model_trainings",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "model_id", "model_selection_id", name="uq_model_training_composite"
        ),
    )
