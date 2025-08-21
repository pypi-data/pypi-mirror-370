# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import contextlib
import sys

from appdynamics.lib import LazyWsgiRequest
from appdynamics.agent.core.eum import inject_eum_metadata
from appdynamics.agent.models.transactions import ENTRY_TORNADO
from ..base import EntryPointInterceptor

_APPD_INTERCEPTED_KEY = '_appd_patched'

try:
    import tornado
    import tornado.httputil
    import tornado.ioloop
    import tornado.web
    import tornado.wsgi
    from tornado import escape
    from io import BytesIO

    class TornadoFallbackHandlerInterceptor(EntryPointInterceptor):
        # When using FallbackHandler, the RequestHandler's finish method is
        # never called.  Wrap the custom fallback callable to end the bt here.
        def _initialize(self, initialize, handler, fallback):
            def _fallback(request):
                fallback(request)
                bt = self.bt
                if bt:
                    self.end_transaction(bt)
            initialize(handler, _fallback)

    class TornadoRequestHandlerInterceptor(EntryPointInterceptor):
        def __execute(self, _execute, handler, *args, **kwargs):

            ContentType = None
            ContentLength = None

            # PYTHON-323: The tornado.wsgi.WSGIContainer.environ internally uses
            # pop on handler.request.headers for Content-Type and Content-Length,
            # so we need to restore them after the API call.
            if "Content-Type" in handler.request.headers:
                ContentType = handler.request.headers.get("Content-Type")

            if "Content-Length" in handler.request.headers:
                ContentLength = handler.request.headers.get("Content-Length")

            bt = self.start_transaction(ENTRY_TORNADO,
                                        LazyWsgiRequest(tornado.wsgi.WSGIContainer.environ(handler.request)))

            if ContentType:
                handler.request.headers.add("Content-Type", ContentType)

            if ContentLength:
                handler.request.headers.add("Content-Length", ContentLength)

            if bt:
                @contextlib.contextmanager
                def current_bt_manager():
                    """Set and unset current_bt as tornado moves between execution contexts.

                    By wrapping the handler's execution with this we can ensure that whenever the
                    IOLoop is executing code for a particular BT, that BT is the 'current_bt'.
                    For more information see http://www.tornadoweb.org/en/stable/stack_context.html.

                    """
                    self.agent.set_current_bt(bt)
                    try:
                        yield
                    except:
                        # Currently can't figure out how to get here, so this code is untested.
                        bt.add_exception(*sys.exc_info())
                        raise
                    finally:
                        self.agent.unset_current_bt()

                with tornado.stack_context.StackContext(current_bt_manager):
                    result = _execute(handler, *args, **kwargs)
            else:
                result = _execute(handler, *args, **kwargs)

            return result

        def _finish(self, finish, handler, *args, **kwargs):
            result = finish(handler, *args, **kwargs)
            bt = self.bt
            if bt:
                with self.log_exceptions():
                    self.handle_http_status_code(bt, handler._status_code, handler._reason)
                    self.end_transaction(bt)
            return result

        def __handle_request_exception(self, _handle_request_exception, handler, e, *args, **kwargs):
            with self.log_exceptions():
                bt = self.bt
                if bt and not (hasattr(tornado.web, 'Finish') and isinstance(e, tornado.web.Finish)):
                    bt.add_exception(*sys.exc_info())
            return _handle_request_exception(handler, e, *args, **kwargs)

        def ___init__(self, init, handler, *args, **kwargs):
            # Only init is patched for tornado 6 and above
            # prepare, on_finish and log_exception methods can be overwridden and don't
            # necessarily need to call parent's prepare, on_finish & log_exception
            # Thus these functions have to be dynamically patched for children who've overwridden them
            cls = handler.__class__
            try_patching_methods(self.agent, cls)
            return init(handler, *args, **kwargs)

        def _prepare(self, prepare, handler, *args, **kwargs):
            self.start_transaction(ENTRY_TORNADO,
                                   LazyWsgiRequest(convert_request(handler.request)))

            result = prepare(handler, *args, **kwargs)
            return result

        def _on_finish(self, on_finish, handler, *args, **kwargs):
            bt = self.bt
            if bt:
                with self.log_exceptions():
                    self.handle_http_status_code(bt, handler._status_code, handler._reason)
                    self.end_transaction(bt)
            result = on_finish(handler, *args, **kwargs)
            return result

        def _log_exception(self, log_exception, handler, *args, **kwargs):
            with self.log_exceptions():
                bt = self.bt
                if bt:
                    bt.add_exception(*sys.exc_info())
                    self.end_transaction(bt)
            result = log_exception(handler, *args, **kwargs)
            return result

        def _flush(self, flush, handler, *args, **kwargs):
            with self.log_exceptions():
                if not handler._headers_written:
                    bt = self.bt
                    if bt:
                        headers = list(handler._headers.get_all())
                        inject_eum_metadata(self.agent.eum_config, bt, headers)
                        handler._headers = tornado.httputil.HTTPHeaders(headers)
            return flush(handler, *args, **kwargs)

    def try_patching_methods(agent, cls):
        # Dynamically patches the prepare, flush, log_exception and on_finish functions
        # _appd_patched attribute is set on the class to make sure that
        # the functions aren't patched twice
        if getattr(cls, _APPD_INTERCEPTED_KEY, False):
            return False
        setattr(cls, _APPD_INTERCEPTED_KEY, True)
        TornadoRequestHandlerInterceptor(agent, cls).attach(['prepare', 'flush', 'log_exception', 'on_finish'])
        return True

    def intercept_tornado_web(agent, mod):
        patch_arr = []
        if int(tornado.version.split('.')[0]) >= 6:
            patch_arr = ['__init__']
        else:
            patch_arr = ['_execute', 'flush', '_handle_request_exception', 'finish']
        TornadoRequestHandlerInterceptor(agent, mod.RequestHandler).attach(patch_arr)
        TornadoFallbackHandlerInterceptor(agent, mod.FallbackHandler).attach('initialize')

    def to_wsgi_str(s: bytes) -> str:
        assert isinstance(s, bytes)
        return s.decode("latin1")

    # from tornado 6.3+, tornado.wsgi.WSGIContainer.environ is not static anymore
    # One change is "wsgi.multithread" field in tornado code will get set depending on executor.
    # since our LazyWsgiRequest don't actually capture that field. Set to False like earlier version here.
    def convert_request(request):
        hostport = request.host.split(":")
        if len(hostport) == 2:
            host = hostport[0]
            port = int(hostport[1])
        else:
            host = request.host
            port = 443 if request.protocol == "https" else 80
        environ = {
            "REQUEST_METHOD": request.method,
            "SCRIPT_NAME": "",
            "PATH_INFO": to_wsgi_str(
                escape.url_unescape(request.path, encoding=None, plus=False)
            ),
            "QUERY_STRING": request.query,
            "REMOTE_ADDR": request.remote_ip,
            "SERVER_NAME": host,
            "SERVER_PORT": str(port),
            "SERVER_PROTOCOL": request.version,
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": request.protocol,
            "wsgi.input": BytesIO(escape.utf8(request.body)),
            "wsgi.errors": sys.stderr,
            "wsgi.multithread": False,
            "wsgi.multiprocess": True,
            "wsgi.run_once": False,
        }
        if "Content-Type" in request.headers:
            environ["CONTENT_TYPE"] = request.headers.get("Content-Type")
        if "Content-Length" in request.headers:
            environ["CONTENT_LENGTH"] = request.headers.get("Content-Length")
        for key, value in request.headers.items():
            environ["HTTP_" + key.replace("-", "_").upper()] = value
        return environ

except ImportError:
    def intercept_tornado_web(agent, mod):
        pass
