# -*- coding: utf-8 -*-

import logging
from six.moves.urllib.parse import quote
from pythonjsonlogger import jsonlogger
from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException

INPUT_URL_FORMAT = "https://{host}/inputs/{token}/tag/{tags}"
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


class LogglyHandler(logging.Handler):

    def __init__(self, token, host, tags=None, fmt=None,
                 resp_callback=None, exc_callback=None):

        logging.Handler.__init__(self)

        tags = tags or 'pyloggly'
        fmt = fmt or DEFAULT_MESSAGE_FORMAT

        self.url = INPUT_URL_FORMAT.format(
            host=host,
            token=token,
            tags=quote(tags, safe=',')
        )

        self.session = FuturesSession()
        self.formatter = jsonlogger.JsonFormatter(fmt)
        self.setFormatter(self.formatter)

        if resp_callback is not None:
            self.resp_callback = resp_callback

        if exc_callback is not None:
            self.exc_callback = exc_callback

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
