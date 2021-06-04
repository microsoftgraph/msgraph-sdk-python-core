from collections import OrderedDict
from unittest import TestCase

from msgraph.core.middleware.middleware import BaseMiddleware, MiddlewarePipeline


class MiddlewarePipelineTest(TestCase):
    def test_adds_middlewares_in_order(self):
        middleware_pipeline = MiddlewarePipeline()
        middleware_pipeline.add_middleware(MockRequestMiddleware1())
        middleware_pipeline.add_middleware(MockRequestMiddleware2())

        first_middleware = middleware_pipeline._middleware
        second_middleware = middleware_pipeline._middleware.next

        self.assertIsInstance(first_middleware, MockRequestMiddleware1)
        self.assertIsInstance(second_middleware, MockRequestMiddleware2)

    def test_request_object_is_modified_in_order(self):
        middleware_pipeline = MiddlewarePipeline()
        middleware_pipeline.add_middleware(MockRequestMiddleware1())
        middleware_pipeline.add_middleware(MockRequestMiddleware2())

        request = OrderedDict()
        request.headers = {}
        result = middleware_pipeline.send(request=request)

        second, _ = result.popitem()
        first, _ = result.popitem()

        self.assertEqual(second, 'middleware2')
        self.assertEqual(first, 'middleware1')

    def test_response_object_is_modified_in_reverse_order(self):
        middleware_pipeline = MiddlewarePipeline()
        middleware_pipeline.add_middleware(
            MockResponseMiddleware1()
        )  # returns world as the response
        middleware_pipeline.add_middleware(
            MockResponseMiddleware2()
        )  # returns hello as the response

        # Responses are passed through the list of middlewares in reverse order.
        # This will return hello world
        request = OrderedDict()
        request.headers = {}
        resp = middleware_pipeline.send(request)

        self.assertEqual(resp, 'Hello World')


class MockRequestMiddleware1(BaseMiddleware):
    def __init__(self):
        super().__init__()

    def send(self, request, **kwargs):
        request['middleware1'] = 1
        return super().send(request, **kwargs)


class MockRequestMiddleware2(BaseMiddleware):
    def __init__(self):
        super().__init__()

    def send(self, request, **kwargs):
        request['middleware2'] = 2
        return request


class MockResponseMiddleware1(BaseMiddleware):
    def __init__(self):
        super().__init__()

    def send(self, request, **kwargs):
        resp = super().send(request, **kwargs)
        resp += 'World'
        return resp


class MockResponseMiddleware2(BaseMiddleware):
    def __init__(self):
        super().__init__()

    def send(self, request, **kwargs):
        return 'Hello '
