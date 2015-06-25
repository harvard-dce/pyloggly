# pyloggly

Python logging handler for sending json-formatted events to [loggly](http://loggly.com). Basically the simplest thing I could make on the quick.

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

If you want to do something to the response from the loggly api you can pass in a reference to to all callback function thusly:

```handler = LogglyHandler('token','host','tags', resp_callback=my_callback)```

The handler's `emit` method will catch and re-raise any exceptions of type `requests.exceptions.RequestException` (and won't catch any others). You can override this by passing in another callback:

```handler = LogglyHandler('token','host','tags', exc=my_callback)```


## Testing
pyloggly unit tests can be run by executing

    python setup.py test

Optionally, you can use [tox](https://tox.readthedocs.org/) with the provided `tox.ini` file

## Contributors

* Jay Luker \<<jay_luker@harvard.edu>\> [@lbjay](http://github.com/lbjay), maintainer

## License

Apache 2.0

## Copyright

2015 President and Fellows of Harvard College
