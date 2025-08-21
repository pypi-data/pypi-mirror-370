from __future__ import unicode_literals
from appdynamics.lang import urlparse
from . import HTTPConnectionInterceptor
from appdynamics import config
from appdynamics.agent.interceptor.utils.genai_utils import OpenaiConstants


class AioHTTPClientInterceptor(HTTPConnectionInterceptor):

    async def __request(self, request, client, method, url, *args, **kwargs):
        # Do not create exit call for openai backend if already created at early instrumenation of openai
        suppress_openai_exit_calls = False
        if config.ENABLE_OPENAI and kwargs and 'headers' in kwargs and isinstance(kwargs.get('headers'), dict) \
                and OpenaiConstants.OPENAI_EXIT_CREATED_HEADER in kwargs.get('headers'):
            suppress_openai_exit_calls = True
            kwargs.get('headers').pop(OpenaiConstants.OPENAI_EXIT_CREATED_HEADER)

        exit_call = None
        # suppress exit creation in case it was already created by openai exit interceptors
        if not suppress_openai_exit_calls:
            url_str = str(url) # because the url we passed in can be a yarl.URL object, urllib.urlparse expects a string
            exit_call = self.start_exit_call(url_str)
            if exit_call:
                correlation_header = self.make_correlation_header(exit_call)
                if correlation_header:
                    headers = kwargs.setdefault('headers', {})
                    headers[correlation_header[0]] = correlation_header[1]

        response = await request(client, method, url, *args, **kwargs)

        self.end_exit_call(exit_call)

        return response

    def start_exit_call(self, url):
        bt = self.bt
        if not bt:
            return None

        parsed_url = urlparse(url)
        port = parsed_url.port or ('443' if parsed_url.scheme == 'https' else '80')
        backend = self.get_backend(parsed_url.hostname, port, parsed_url.scheme, url)
        if not backend:
            return None

        return super(AioHTTPClientInterceptor, self).start_exit_call(bt, backend, operation=parsed_url.path)

    def end_exit_call(self, exit_call):
        super(AioHTTPClientInterceptor, self).end_exit_call(exit_call)


def intercept_aiohttp_client(agent, mod):
    AioHTTPClientInterceptor(agent, mod.ClientSession).attach('_request')
