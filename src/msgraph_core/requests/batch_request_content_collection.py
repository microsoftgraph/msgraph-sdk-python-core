from typing import List, Optional

from kiota_abstractions.request_information import RequestInformation
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
        self.batches: List[BatchRequestContent] = []
        self.current_batch: BatchRequestContent = BatchRequestContent()

    def add_batch_request_item(self, request: BatchRequestItem) -> None:
        """ 
        Adds a request item to the collection.
        Args:
            request (BatchRequestItem): The request item to add.
        """
        if len(self.current_batch.requests) >= self.max_requests_per_batch:
            self.batches.append(self.current_batch.finalize())
            self.current_batch = BatchRequestContent()
        self.current_batch.add_request(request.id, request)
        self.batches.append(self.current_batch)

    def remove_batch_request_item(self, request_id: str) -> None:
        """ 
        Removes a request item from the collection.
        Args:
            request_id (str): The ID of the request item to remove.
        """
        for batch in self.batches:
            if request_id in batch.requests:
                del batch.requests[request_id]
                return
        if request_id in self.current_batch.requests:
            del self.current_batch.requests[request_id]

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
                if request.status_code not in [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]:
                    if batch_with_failed_responses is not None:
                        batch_with_failed_responses.add_request(request.id, request)
                    else:
                        raise ValueError("batch_with_failed_responses is None")
        return batch_with_failed_responses

    def get_batch_requests_for_execution(self) -> List[BatchRequestContent]:
        """
        Gets the batch requests for execution.
        Returns:
            List[BatchRequestContent]: The batch requests for execution.
        """
        # if not self.current_batch.is_finalized:
        #     self.current_batch.finalize()
        #     self.batches.append(self.current_batch)
        return self.batches

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        pass
        # print(f"serializing {self.batches}")
        # writer.write_collection_of_object_values("requests", self.batches)
