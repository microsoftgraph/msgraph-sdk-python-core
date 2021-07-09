import logging
import sys
import textwrap

# pylint: disable=no-member
root = logging.getLogger('graph_logger')


def log_roundtrip(response, *args, **kwargs):
    extra = {'req': response.request, 'res': response}
    root.debug('HTTP roundtrip', extra=extra)


# pylint: disable=no-member
class HttpFormatter(logging.Formatter):
    """
    Class containing methods to format the structure of the HTTP logs
    """
    def _format_headers(self, request_headers):
        """
        Helper method that returns the request/response headers in the
        desired format
        """
        return '\n'.join(f'{k}: {v}' for k, v in request_headers.items())

    def formatMessage(self, record):
        """
        Formats the HTTP logs to the provided structure.
        """
        result = super().formatMessage(record)
        if record.name == 'graph_logger':
            result += textwrap.dedent(
                '''
                ---------------- request ----------------
                {req.method} {req.url}
                {reqhdrs}

                {req.body}
                ---------------- response ----------------
                {res.status_code} {res.reason} {res.url}
                {reshdrs}

                {res.text}
            '''
            ).format(
                req=record.req,
                res=record.res,
                reqhdrs=self._format_headers(record.req.headers),
                reshdrs=self._format_headers(record.res.headers),
            )

        return result
