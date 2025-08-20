from sqlalchemy import JSON, BigInteger, Column, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class QueuedJob(Base):
    __tablename__ = "queued_jobs"

    id = Column(Text, primary_key=True)
    job_ref_name = Column(Text, nullable=False, index=True)
    submitted_at = Column(
        DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False
    )
    payload = Column(JSON, nullable=False)
    num_attempts = Column(BigInteger, nullable=False, default=0, server_default="0")
