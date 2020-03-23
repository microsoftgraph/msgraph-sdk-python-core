from collections import OrderedDict
from unittest import TestCase

from requests.adapters import HTTPAdapter

from src.core.middleware_pipeline import MiddlewarePipeline


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
        result = middleware_pipeline.send(request=request)

        second, _ = result.popitem()
        first, _ = result.popitem()

        self.assertEqual(second, 'middleware2')
        self.assertEqual(first, 'middleware1')

    def test_response_object_is_modified_in_reverse_order(self):
        middleware_pipeline = MiddlewarePipeline()
        middleware_pipeline.add_middleware(MockResponseMiddleware1()) # returns world as the response
        middleware_pipeline.add_middleware(MockResponseMiddleware2()) # returns hello as the response

        # Responses are passed through the list of middlewares in reverse order. This will return hello world
        resp = middleware_pipeline.send({})

        self.assertEqual(resp, 'Hello World')


class MockRequestMiddleware1(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.next = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        request['middleware1'] = 1

        if self.next is None:
            return request

        return self.next.send(request)


class MockRequestMiddleware2(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.next = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        request['middleware2'] = 2

        if self.next is None:
            return request

        return self.next.send(request)


class MockResponseMiddleware1(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.next = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        if self.next is None:
            pass

        resp = self.next.send(request)
        resp += 'World'
        return resp


class MockResponseMiddleware2(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.next = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        if self.next is None:
            response = 'Hello '
            return response

        resp = self.next.send(request)
        return resp



