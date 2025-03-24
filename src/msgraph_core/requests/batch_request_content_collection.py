from typing import Optional

from kiota_abstractions.serialization import SerializationWriter

from .batch_request_content import BatchRequestContent
from .batch_request_item import BatchRequestItem


class BatchRequestContentCollection:
    """A collection of request content objects."""

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchRequestContentCollection class.


        """
        self.max_requests_per_batch = BatchRequestContent.MAX_REQUESTS
        self.current_batch: BatchRequestContent = BatchRequestContent()
        self.batches: list[BatchRequestContent] = [self.current_batch]

    def add_batch_request_item(self, request: BatchRequestItem) -> None:
        """
        Adds a request item to the collection.
        Args:
            request (BatchRequestItem): The request item to add.
        """
        if len(self.current_batch.requests) >= self.max_requests_per_batch:
            self.current_batch.finalize()
            self.current_batch = BatchRequestContent()
            self.batches.append(self.current_batch)
        self.current_batch.add_request(request.id, request)

    def remove_batch_request_item(self, request_id: str) -> None:
        """
        Removes a request item from the collection.
        Args:
            request_id (str): The ID of the request item to remove.
        """
        for batch in self.batches:
            if request_id in batch.requests:
                batch.remove(request_id)
                return

    def new_batch_with_failed_requests(self) -> Optional[BatchRequestContent]:
        """
        Creates a new batch with failed requests.
        Returns:
            Optional[BatchRequestContent]: A new batch with failed requests.
        """
        # Use IDs to get response status codes, generate new batch with failed requests
        batch_with_failed_responses: Optional[BatchRequestContent] = BatchRequestContent()
        for batch in self.batches:
            for request in batch.requests:
                if request.status_code not in [ # type: ignore # Method should be deprecated
                    200, 201, 202, 203, 204, 205, 206, 207, 208, 226
                ]:
                    if batch_with_failed_responses is not None:
                        batch_with_failed_responses.add_request(
                            request.id,  # type: ignore # Bug. Method should be deprecated
                            request  # type: ignore
                        )
                    else:
                        raise ValueError("batch_with_failed_responses is None")
        return batch_with_failed_responses

    def get_batch_requests_for_execution(self) -> list[BatchRequestContent]:
        """
        Gets the batch requests for execution.
        Returns:
            list[BatchRequestContent]: The batch requests for execution.
        """
        return self.batches

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        pass
