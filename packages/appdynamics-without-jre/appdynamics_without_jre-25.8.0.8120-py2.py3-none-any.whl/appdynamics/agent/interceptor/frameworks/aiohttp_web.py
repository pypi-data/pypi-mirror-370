import sys

from appdynamics.agent.core.eum import inject_eum_metadata
from appdynamics.agent.models.transactions import ENTRY_AIOHTTP
from ..base import EntryPointInterceptor
from appdynamics.aiohttp_lib import LazyAioHTTPRequest


class AIOHTTPInterceptor(EntryPointInterceptor):
    def attach(self, application):
        super(AIOHTTPInterceptor, self).attach(application)

    async def __handle(self, _handle, instance, request):
        bt = self.start_transaction(ENTRY_AIOHTTP, LazyAioHTTPRequest(request))
        try:
            response = await _handle(instance, request)
        except:
            with self.log_exceptions():
                if bt:
                    bt.add_exception(*sys.exc_info())
            raise
        finally:
            self.end_transaction(bt)
        return response

    def ___init__(self, func, instance, status, reason, headers):
        response = func(instance, status=status, reason=reason, headers=headers)
        with self.log_exceptions():
            bt = self.bt
            if bt:
                self.make_response_wrapper(status, reason, headers)
        return response

    def make_response_wrapper(self, status, reason, headers):
        """Deal with HTTP status codes, errors and EUM correlation.

        """
        with self.log_exceptions():
            bt = self.bt
            if bt:
                # Store the HTTP status code and deal with errors.
                status_code = status
                msg = reason
                self.handle_http_status_code(bt, int(status_code), msg)

                # Inject EUM metadata into the response headers.
                inject_eum_metadata(self.agent.eum_config, bt, headers)


def intercept_aiohttp_web(agent, mod):
    AIOHTTPInterceptor(agent, mod.Application).attach('_handle')
    AIOHTTPInterceptor(agent, mod.StreamResponse).attach('__init__')
