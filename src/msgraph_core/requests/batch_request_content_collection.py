from typing import List

from kiota_abstractions.request_information import RequestInformation

from .batch_request_content import BatchRequestContent
from .batch_request_item import BatchRequestItem


class BatchRequestContentCollection:
    """A collection of request content objects."""

    def __init__(self, batch_max_requests: int = 20):
        self.batch_max_requests = batch_max_requests or BatchRequestContent.MAX_REQUESTS
        self.batches: List[BatchRequestContent] = []
        self.current_batch: BatchRequestContent = BatchRequestContent(
        )  # fix, how we get the current batch?

    def add_batch_request_step(self, request: BatchRequestItem) -> None:
        try:
            self.current_batch.add_request(request)
        except ValueError as e:
            if "Maximum number of requests is" in str(e):
                self.batches.append(self.current_batch.finalize())

                self.current_batch = BatchRequestContent()
                self.current_batch.add_request(request)
            else:
                raise e

    def get_batch_requests_for_execution(self):
        if not self.current_batch.is_finalized:
            self.batches.append(self.current_batch.finalize())
        return self.batches
