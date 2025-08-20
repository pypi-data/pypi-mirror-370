from uncountable.core.client import Client
from uncountable.types import async_batch_t, base_t
from uncountable.types.async_batch import AsyncBatchRequest
from uncountable.types.async_batch_processor import AsyncBatchProcessorBase


class AsyncBatchSubmissionError(Exception):
    pass


class AsyncBatchProcessor(AsyncBatchProcessorBase):
    _client: Client
    _queue: list[AsyncBatchRequest]
    _submitted_job_ids: list[base_t.ObjectId]

    def __init__(self, *, client: Client) -> None:
        super().__init__()
        self._client = client
        self._queue = []
        self._submitted_job_ids = []

    def _enqueue(self, req: async_batch_t.AsyncBatchRequest) -> None:
        self._queue.append(req)

    def current_queue_size(self) -> int:
        return len(self._queue)

    def send(self) -> base_t.ObjectId:
        if len(self._queue) == 0:
            raise AsyncBatchSubmissionError("queue is empty")
        job_id = self._client.execute_batch_load_async(requests=self._queue).job_id
        self._submitted_job_ids.append(job_id)
        self._queue = []
        return job_id

    def get_submitted_job_ids(self) -> list[base_t.ObjectId]:
        return self._submitted_job_ids
