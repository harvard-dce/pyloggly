pyloggly change log
===================

0.1.0 (2015-06-25)
------------------

Initial release!

0.2.0 (2018-02-26)
------------------

Python 3 compatibility

0.3.0 (2018-02-28)
------------------

New bulk handler + event cleanup.

* Added `LogglyBulkHandler`
* `LogglyHandler` uses own instance of `ThreadPoolExecutor`
* Register `atexit` cleanup methods
* `.flush` methods for both handlers to explicitly flush pending events
