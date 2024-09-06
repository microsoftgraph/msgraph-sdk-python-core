from typing import List, Optional

from kiota_abstractions.request_information import RequestInformation

from .batch_request_content import BatchRequestContent
from .batch_request_item import BatchRequestItem


class BatchRequestContentCollection:
    """A collection of request content objects."""

    def __init__(self, batch_request_limit: int = 20):
        self.batch_request_limit = batch_request_limit or BatchRequestContent.MAX_REQUESTS
        self.batches: [List[BatchRequestContent]] = []
        self.current_batch: BatchRequestContent = BatchRequestContent()

    def add_batch_request_item(self, request: BatchRequestItem) -> None:
        try:
            self.current_batch.add_request(request)
        except ValueError as e:
            if "Maximum number of requests is" in str(e):
                self.batches.append(self.current_batch.finalize())

                self.current_batch = BatchRequestContent()
                self.current_batch.add_request(request)
        self.batches.append(self.current_batch)

    def remove_batch_request_item(self, request_id: str) -> None:
        for batch in self.batches:
            for request in batch.requests:
                if request.id == request_id:
                    batch.requests.remove(request)
                    return
        for request in self.current_batch.requests:
            if request.id == request_id:
                self.current_batch.requests.remove(request)
                return

    def new_batch_with_failed_requests(self) -> Optional[BatchRequestContent]:
        # Use IDs to get response status codes, generate new batch with failed requests
        batch_with_failed_responses: Optional[BatchRequestContent] = BatchRequestContent()
        for batch in self.batches:
            for request in batch.requests:
                if request.status_code != 200:
                    return batch_with_failed_responses.add_request(request)
        return batch_with_failed_responses

    def get_batch_requests_for_execution(self) -> List[BatchRequestContent]:
        if not self.current_batch.is_finalized:
            self.current_batch.finalize()
            self.batches.append(self.current_batch)
        return self.batches
