[![Build Status](https://travis-ci.org/harvard-dce/pyloggly.svg?branch=master)](https://travis-ci.org/harvard-dce/pyloggly)

# pyloggly

Python logging handlers for sending json-formatted events to [loggly](http://loggly.com). Basically the simplest thing I could make on the quick.

## Installation

Install via pip:

```
pip install pyloggly
```

## Usage

```python

import logging
from pyloggly import LogglyHandler

logger = logging.getLogger()
handler = LogglyHandler('mytoken', 'logs-01.loggly.com', 'mytag')
logger.addHandler(handler)

logger.info("Hey, I'm logging to loggly!")
```

### Config via fileConfig

If you roll that way you can use a logging file config like this:

```

    [handlers]
    keys=LogglyHandler
    
    [handler_LogglyHandler]
    class=pyloggly.handler.LogglyHandler
    args=('mytoken','logs-01.loggly.com','mytag')
    
    [loggers]
    keys=root
    
    [logger_root]
    handlers=LogglyHandler
    level=INFO
    
    [formatters]
    keys=
```

## Response and Exception callbacks

If you want to do something to the response from the loggly api you can pass in a reference to a callback function thusly:

```handler = LogglyHandler('token','host','tags', resp_callback=my_callback)```

The handler's `emit` method will catch and re-raise any exceptions of type `requests.exceptions.RequestException` (and won't catch any others). 
You can override this by passing in another callback:

```handler = LogglyHandler('token','host','tags', exc_callback=my_callback)```

## Bulk endpoint handler

pyloggly also includes a `LogglyBulkHandler` which utilizes the Loggly [bulk api endpoint](https://www.loggly.com/docs/http-bulk-endpoint/).
Rather than sending each event is it is emitted, the bulk handler collects events up to `batch_size` and sends them in batches. A cleanup
function is registered via `atexit.register` that will send remaining collected events. You can also explicitly call `handler.flush()`.

## Flushing at exit

`LogglyHandler` uses the standard Loggly HTTPS endpoint and uses a `FuturesSession` session from [requests-futures](https://github.com/ross/requests-futures)
to execute async http requests. The handler registers an atexit cleanup function that tries to ensure all pending requests are completed, but YMMV as to reliability.
In some environments, e.g. AWS Lambda, the main program thread may not signal when it exits (note, this is hearsay based on info in another project's [README](https://github.com/zach-taylor/splunk_handler)). For those cases it may be necessary to explicitly call the handler's `.flush()` method.


## Testing
pyloggly unit tests can be run by executing

    python setup.py test

Optionally, you can use [tox](https://tox.readthedocs.org/) with the provided `tox.ini` file

## Contributors

* Jay Luker \<<jay_luker@harvard.edu>\> [@lbjay](http://github.com/lbjay), maintainer

## License

Apache 2.0

## Copyright

2018 President and Fellows of Harvard College
