import asyncio

from uncountable.integration.db.connect import IntegrationDBService, create_db_engine
from uncountable.integration.db.session import get_session_maker
from uncountable.integration.queue_runner.command_server import serve
from uncountable.integration.queue_runner.command_server.types import CommandQueue
from uncountable.integration.queue_runner.datastore import DatastoreSqlite
from uncountable.integration.queue_runner.job_scheduler import start_scheduler


async def queue_runner_loop() -> None:
    command_queue: CommandQueue = asyncio.Queue()
    engine = create_db_engine(IntegrationDBService.RUNNER)
    session_maker = get_session_maker(engine)

    datastore = DatastoreSqlite(session_maker)
    datastore.setup(engine)

    command_server = asyncio.create_task(serve(command_queue, datastore))

    scheduler = asyncio.create_task(start_scheduler(command_queue, datastore))

    await scheduler
    await command_server


def start_queue_runner() -> None:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(queue_runner_loop())
    loop.close()


if __name__ == "__main__":
    start_queue_runner()
