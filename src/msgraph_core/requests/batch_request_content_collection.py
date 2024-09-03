class BatchRequestContentCollection:
    """A collection of request content objects."""

    def __init__(self):
        self._request_contents = []

    def add_request_content(self, request_content):
        """Add a request content object to the collection.

        Args:
            request_content (RequestContent): The request content object to add.

        Returns:
            BatchRequestContentCollection: The BatchRequestContentCollection object.
        """
        self._request_contents.append(request_content)
        return self

    def __iter__(self):
        return iter(self._request_contents)

    def __len__(self):
        return len(self._request_contents)
