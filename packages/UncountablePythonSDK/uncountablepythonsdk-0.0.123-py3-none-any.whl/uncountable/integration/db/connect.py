import os
from enum import StrEnum

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


class IntegrationDBService(StrEnum):
    CRON = "cron"
    RUNNER = "runner"


def create_db_engine(service: IntegrationDBService) -> Engine:
    match service:
        case IntegrationDBService.CRON:
            return create_engine(os.environ["UNC_CRON_SQLITE_URI"])
        case IntegrationDBService.RUNNER:
            return create_engine(os.environ["UNC_RUNNER_SQLITE_URI"])
