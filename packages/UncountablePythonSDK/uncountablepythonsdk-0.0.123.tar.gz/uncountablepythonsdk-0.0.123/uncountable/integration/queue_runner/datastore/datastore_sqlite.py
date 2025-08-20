import datetime
import uuid
from datetime import UTC

from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from pkgs.argument_parser import CachedParser
from pkgs.serialization_util import serialize_for_storage
from uncountable.integration.db.session import DBSessionMaker
from uncountable.integration.queue_runner.datastore.interface import Datastore
from uncountable.integration.queue_runner.datastore.model import Base, QueuedJob
from uncountable.types import queued_job_t

queued_job_payload_parser = CachedParser(queued_job_t.QueuedJobPayload)


class DatastoreSqlite(Datastore):
    def __init__(self, session_maker: DBSessionMaker) -> None:
        self.session_maker = session_maker
        super().__init__()

    @classmethod
    def setup(cls, engine: Engine) -> None:
        Base.metadata.create_all(engine)

    def add_job_to_queue(
        self, job_payload: queued_job_t.QueuedJobPayload, job_ref_name: str
    ) -> queued_job_t.QueuedJob:
        with self.session_maker() as session:
            serialized_payload = serialize_for_storage(job_payload)
            queued_job_uuid = str(uuid.uuid4())
            num_attempts = 0
            submitted_at = datetime.datetime.now(UTC)
            insert_stmt = insert(QueuedJob).values({
                QueuedJob.id.key: queued_job_uuid,
                QueuedJob.job_ref_name.key: job_ref_name,
                QueuedJob.payload.key: serialized_payload,
                QueuedJob.num_attempts: num_attempts,
                QueuedJob.submitted_at: submitted_at,
            })
            session.execute(insert_stmt)
            return queued_job_t.QueuedJob(
                queued_job_uuid=queued_job_uuid,
                job_ref_name=job_ref_name,
                payload=job_payload,
                submitted_at=submitted_at,
                num_attempts=num_attempts,
            )

    def increment_num_attempts(self, queued_job_uuid: str) -> int:
        with self.session_maker() as session:
            update_stmt = (
                update(QueuedJob)
                .values({QueuedJob.num_attempts.key: QueuedJob.num_attempts + 1})
                .filter(QueuedJob.id == queued_job_uuid)
            )
            session.execute(update_stmt)
            session.flush()
            # IMPROVE: python3's sqlite does not support the RETURNING clause
            select_stmt = select(QueuedJob.num_attempts).filter(
                QueuedJob.id == queued_job_uuid
            )
            return int(session.execute(select_stmt).one().num_attempts)

    def remove_job_from_queue(self, queued_job_uuid: str) -> None:
        with self.session_maker() as session:
            delete_stmt = delete(QueuedJob).filter(QueuedJob.id == queued_job_uuid)
            session.execute(delete_stmt)

    def list_queued_job_metadata(
        self, offset: int = 0, limit: int | None = 100
    ) -> list[queued_job_t.QueuedJobMetadata]:
        with self.session_maker() as session:
            select_statement = (
                select(
                    QueuedJob.id,
                    QueuedJob.job_ref_name,
                    QueuedJob.num_attempts,
                    QueuedJob.submitted_at,
                )
                .order_by(QueuedJob.submitted_at)
                .offset(offset)
                .limit(limit)
            )

            queued_job_metadata: list[queued_job_t.QueuedJobMetadata] = [
                queued_job_t.QueuedJobMetadata(
                    queued_job_uuid=row.id,
                    job_ref_name=row.job_ref_name,
                    num_attempts=row.num_attempts,
                    submitted_at=row.submitted_at,
                )
                for row in session.execute(select_statement)
            ]

            return queued_job_metadata

    def get_next_queued_job_for_ref_name(
        self, job_ref_name: str
    ) -> queued_job_t.QueuedJob | None:
        with self.session_maker() as session:
            select_stmt = (
                select(
                    QueuedJob.id,
                    QueuedJob.payload,
                    QueuedJob.num_attempts,
                    QueuedJob.job_ref_name,
                    QueuedJob.submitted_at,
                )
                .filter(QueuedJob.job_ref_name == job_ref_name)
                .limit(1)
                .order_by(QueuedJob.submitted_at)
            )

            for row in session.execute(select_stmt):
                parsed_payload = queued_job_payload_parser.parse_storage(row.payload)
                return queued_job_t.QueuedJob(
                    queued_job_uuid=row.id,
                    job_ref_name=row.job_ref_name,
                    num_attempts=row.num_attempts,
                    submitted_at=row.submitted_at,
                    payload=parsed_payload,
                )

            return None

    def load_job_queue(self) -> list[queued_job_t.QueuedJob]:
        with self.session_maker() as session:
            select_stmt = select(
                QueuedJob.id,
                QueuedJob.payload,
                QueuedJob.num_attempts,
                QueuedJob.job_ref_name,
                QueuedJob.submitted_at,
            ).order_by(QueuedJob.submitted_at)

            queued_jobs: list[queued_job_t.QueuedJob] = []
            for row in session.execute(select_stmt):
                parsed_payload = queued_job_payload_parser.parse_storage(row.payload)
                queued_jobs.append(
                    queued_job_t.QueuedJob(
                        queued_job_uuid=row.id,
                        job_ref_name=row.job_ref_name,
                        num_attempts=row.num_attempts,
                        submitted_at=row.submitted_at,
                        payload=parsed_payload,
                    )
                )

            return queued_jobs
