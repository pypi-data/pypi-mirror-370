# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for Uvicorn Webserver.

"""

from __future__ import unicode_literals
import sys

from appdynamics.asgi_lib import LazyAsgiRequest
from appdynamics.agent.models.transactions import ENTRY_ASGI
from appdynamics.agent.interceptor.frameworks.asgi import ASGIInterceptor


class UvicornInterceptor(ASGIInterceptor):
    async def ___call__(self, func, middleware, scope, receive, send, *args, **kwargs):
        # asgi interceptor only support http type request
        if scope['type'] != 'http':
            return await func(middleware, scope, receive, send, *args, **kwargs)
        bt = self.start_transaction(ENTRY_ASGI, LazyAsgiRequest(scope))
        try:
            response = await func(middleware, scope, receive,
                                  self._make_send_wrapper(send), *args, **kwargs)
        except:
            with self.log_exceptions():
                if bt:
                    bt.add_exception(*sys.exc_info())
            raise
        finally:
            self.end_transaction(bt)
        return response


def intercept_uvicorn(agent, mod):
    UvicornInterceptor(agent, mod.ProxyHeadersMiddleware).attach('__call__')
