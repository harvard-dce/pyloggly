# -*- coding: utf-8 -*-

import atexit
import logging
import requests
from six.moves.urllib.parse import quote
from pythonjsonlogger import jsonlogger
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor

DEFAULT_MESSAGE_FORMAT = ('{ "loggerName":"%(name)s",'
                          ' "asciTime":"%(asctime)s",'
                          ' "fileName":"%(filename)s",'
                          ' "logRecordCreationTime":"%(created)f",'
                          ' "functionName":"%(funcName)s",'
                          ' "lineNo":"%(lineno)d",'
                          ' "time":"%(msecs)d",'
                          ' "levelName":"%(levelname)s",'
                          ' "message":"%(message)s",'
                          ' "exc_info":"%(exc_info)s"}')


class BaseLogglyHandler(logging.Handler):

    url_format = None

    def __init__(self, token, host, tags=None, fmt=None):

        logging.Handler.__init__(self)
        tags = tags or 'pyloggly'
        fmt = fmt or DEFAULT_MESSAGE_FORMAT
        self.url = self.url_format.format(
            host=host,
            token=token,
            tags=quote(tags, safe=',')
        )
        self.formatter = jsonlogger.JsonFormatter(fmt)
        self.setFormatter(self.formatter)


class LogglyHandler(BaseLogglyHandler):

    url_format = "https://{host}/inputs/{token}/tag/{tags}"

    def __init__(self, token, host, tags=None, fmt=None,
                 resp_callback=None, exc_callback=None):

        super(LogglyHandler, self).__init__(token, host, tags, fmt)

        executor = ThreadPoolExecutor(max_workers=2)
        self.executor = executor
        self.session = FuturesSession(executor=executor)

        @atexit.register
        def cleanup():
            executor.shutdown()

        if resp_callback is not None:
            self.resp_callback = resp_callback

        if exc_callback is not None:
            self.exc_callback = exc_callback

    def flush(self, wait=False):
        self.executor.shutdown(wait=wait)

    def resp_callback(self, session, resp):
        pass

    def exc_callback(self, exc):
        raise exc

    def emit(self, record):
        try:
            self.session.post(self.url,
                              data=self.format(record),
                              background_callback=self.resp_callback)
        except RequestException as e:
            self.exc_callback(e)


class LogglyBulkHandler(LogglyHandler):

    url_format = "https://{host}/bulk/{token}/tag/{tags}"

    def __init__(self, token, host, tags=None, fmt=None, batch_size=100):

        super(LogglyHandler, self).__init__(token, host, tags, fmt)
        self.batch_size = batch_size

        events = []
        url = self.url
        session = requests.Session()
        session.headers.update({'Content-type': 'text/plain'})

        @atexit.register
        def cleanup():
            session.post(url, data="\n".join(events))

        self.session = session
        self.events = events

    def emit(self, record):
        self.events.append(self.format(record))
        if len(self.events) == self.batch_size:
            self.flush()

    def flush(self):
        self.session.post(self.url, data="\n".join(self.events))
        self.events = []

    def cancel(self):
        self.events = []


