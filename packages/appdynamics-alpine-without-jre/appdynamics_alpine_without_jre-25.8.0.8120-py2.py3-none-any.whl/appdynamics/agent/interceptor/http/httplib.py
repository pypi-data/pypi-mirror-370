# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for httplib/http.client.

"""

from __future__ import unicode_literals

from . import HTTPConnectionInterceptor
from appdynamics import config
from appdynamics.agent.interceptor.utils.genai_utils import OpenaiConstants


class HttplibConnectionInterceptor(HTTPConnectionInterceptor):
    def _putrequest(self, putrequest, connection, method, url, *args, **kwargs):
        exit_call = None
        # disable exit call creation when _appd_exit_created is set
        suppress_openai_exit_calls = False
        if config.ENABLE_OPENAI and hasattr(connection, "_appd_exit_created"):
            suppress_openai_exit_calls = True

        with self.log_exceptions():
            bt = self.bt
            if not suppress_openai_exit_calls and bt:
                scheme = 'https' if self._request_is_https(connection) else 'http'
                backend = self.get_backend(connection.host, connection.port, scheme, url)
                if backend:
                    exit_call = self.start_exit_call(bt, backend, operation=url)
                    connection._appd_exit_call = exit_call
        return putrequest(connection, method, url, appd_exit_call=exit_call, *args, **kwargs)

    def _endheaders(self, endheaders, connection, *args, **kwargs):
        exit_call = getattr(connection, '_appd_exit_call', None)
        with self.log_exceptions():
            header = self.make_correlation_header(exit_call)
            if header is not None:
                connection.putheader(*header)
                self.agent.logger.debug('Added correlation header to HTTP request: %s, %s' % header)
        return endheaders(connection, appd_exit_call=exit_call, *args, **kwargs)

    def _getresponse(self, getresponse, connection, *args, **kwargs):
        # CORE-40945 Catch TypeError as a special case for Python 2.6 and call getresponse with just the
        # HTTPConnection instance.
        exit_call = getattr(connection, '_appd_exit_call', None)
        try:
            with self.end_exit_call_and_reraise_on_exception(exit_call,
                                                             ignored_exceptions=(TypeError,)):
                response = getresponse(connection, *args, **kwargs)
        except TypeError:
            with self.end_exit_call_and_reraise_on_exception(exit_call):
                response = getresponse(connection)

        self.end_exit_call(exit_call)
        try:
            del connection._appd_exit_call
        except AttributeError:
            pass
        return response

    def _putheader(self, putheader, connection, *args, **kwargs):
        # args[0]: the header key(being set at openai interceptors)
        if (args and len(args) > 0 and args[0] == OpenaiConstants.OPENAI_EXIT_CREATED_HEADER):
            connection._appd_exit_created = True
        return putheader(connection, *args, **kwargs)


def intercept_httplib(agent, mod):
    HTTPConnectionInterceptor.https_connection_classes.add(mod.HTTPSConnection)
    interceptor = HttplibConnectionInterceptor(agent, mod.HTTPConnection)
    interceptor.attach(['putrequest', 'endheaders'])
    interceptor.attach('getresponse', wrapper_func=None)   # CORE-40945 Do not wrap getresponse in the default wrapper.
    # if enable_openai is True, intercept putheader and check for appd_already_intercepted set it in the connection obj
    # to avoid creating multiple exits
    if config.ENABLE_OPENAI:
        interceptor.attach('putheader')
