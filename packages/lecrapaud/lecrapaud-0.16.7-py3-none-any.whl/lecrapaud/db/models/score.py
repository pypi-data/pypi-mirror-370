from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    BigInteger,
    TIMESTAMP,
    JSON,
)
from sqlalchemy import func
from sqlalchemy.orm import relationship
from lecrapaud.db.models.base import Base
from lecrapaud.config import LECRAPAUD_TABLE_PREFIX


class Score(Base):
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
    type = Column(
        String(50), nullable=False
    )  # either hyperopts or validation or crossval
    training_time = Column(Integer)
    eval_data_std = Column(Float)
    rmse = Column(Float)
    rmse_std_ratio = Column(Float)
    mae = Column(Float)
    mape = Column(Float)
    mam = Column(Float)
    mad = Column(Float)
    mae_mam_ratio = Column(Float)
    mae_mad_ratio = Column(Float)
    r2 = Column(Float)
    logloss = Column(Float)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1 = Column(Float)
    roc_auc = Column(Float)
    thresholds = Column(JSON)
    precision_at_threshold = Column(Float)
    recall_at_threshold = Column(Float)
    f1_at_threshold = Column(Float)
    model_training_id = Column(
        BigInteger,
        ForeignKey(f"{LECRAPAUD_TABLE_PREFIX}_model_trainings.id", ondelete="CASCADE"),
        nullable=False,
    )

    model_trainings = relationship(
        "ModelTraining", back_populates="score", lazy="selectin"
    )
