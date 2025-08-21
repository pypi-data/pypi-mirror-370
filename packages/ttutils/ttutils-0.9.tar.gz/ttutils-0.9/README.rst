Python utils and configuration
==============================

Configuration
-------------

Constants and valiables

.. code-block:: bash

    export CONFIG='/path/to/base_config.yaml;/path/to/config.toml'


.. code-block:: python

    from ttutils import Config

    CFG = Config()

    CFG.PUBLIC_URL  # get from config files
    CFG.ENV.CONFIG  # get from os env
    CFG.SECRET.KEY  # get from os env and clean


Logging configuration

.. code-block:: bash

    export CONFIG='/path/to/base_log_config.yaml;/path/to/logging.toml'


.. code-block:: python

    from ttutils import LoggingConfig

    CFG = LoggingConfig({
        'loggers': {
            'aiohttp.access': {  # local overriding
                'level': 'ERROR',
            }
        }
    })


Safe type convertors
--------------------

.. code-block:: python

    from ttutils import try_int, as_bool, to_string, safe_text, text_crop, int_list, int_set

    try_int('123') == 123
    try_int('asd') is None

    as_bool('t') is True
    as_bool(1) is True
    as_bool('false') is False

    to_string(AClass) == '<AClass>'
    to_string('text') == 'text'
    to_string(b'text') == 'text'

    to_bytes('text') == b'text'
    to_bytes(b'text') == b'text'
    to_bytes(1234567890) == b'I\x96\x02\xd2'

    safe_text('<b>text</b>') == '&lt;b&gt;text&lt;/b&gt;'
    safe_text('text') == 'text'

    text_crop('text', 5) == 'text'
    text_crop('sometext', 6) == 'some …'

    int_list(['1', '2', 'a', 'b', None]) == [1, 2]
    int_set(['1', '2', 'a', 'b', None]) == {1, 2}


Compress
--------

Integer, dict integers, list integers compression/decompression functions

.. code-block:: python

    from ttutils import compress

    compress.encode(11232423)  # 'GSiD'
    compress.decode('GSi')  # 175506

    compress.encode_list([12312, 34535, 12323])  # '30o-8rD-30z'
    compress.decode_list('30o-8rD-30z--30C')  # [12312, 34535, 12323, 12324, 12325, 12326]

    compress.encode_dict({12: [234, 453], 789: [12, 98, 99, 100, 101]})  # 'c-3G-75/cl-c-1y--1B'
    compress.decode_dict('c-3G-75/cl-c-1y--1B')  # {12: [234, 453], 789: [12, 98, 99, 100, 101]}


DateTime
--------

Datetime parse and serialize utils

.. code-block:: python

    from ttutils import (utcnow, utcnow_ms, utcnow_sec, parsedt, parsedt_ms,
        parsedt_sec, try_parsedt, isoformat, safe_isoformat)

    utcnow()      # datetime(2022, 2, 22, 14, 28, 10, 158164, tzinfo=datetime.timezone.utc)
    utcnow_ms()   # datetime(2022, 2, 22, 14, 28, 20, 824000, tzinfo=datetime.timezone.utc)
    utcnow_sec()  # datetime(2022, 2, 22, 14, 28, 24, tzinfo=datetime.timezone.utc)

    parsedt('2022-02-22T11:22:33.123456Z')      # datetime(2022, 2, 22, 11, 22, 33, 123456, tzinfo=datetime.timezone.utc)
    parsedt_ms('2022-02-22T11:22:33.123456Z')   # datetime(2022, 2, 22, 11, 22, 33, 123000, tzinfo=datetime.timezone.utc)
    parsedt_sec('2022-02-22T11:22:33.123456Z')  # datetime(2022, 2, 22, 11, 22, 33, tzinfo=datetime.timezone.utc)

    try_parsedt('2022-02-22T11:22:33.123456Z')  # datetime(2022, 2, 22, 11, 22, 33, 123456, tzinfo=datetime.timezone.utc)
    try_parsedt(None)  # None

    isoformat(utcnow())      # '2022-02-22T14:33:51.381164Z'
    try_isoformat(utcnow())  # '2022-02-22T14:33:51.381164Z'
    try_isoformat(None)      # None


Concurrency
-----------

Tools for asyncio

To limit the parallelism of an asynchronous function, install a decorator

.. code-block:: python

    from ttutils import concurrency_limit

    @concurrency_limit(2)
    async def my_task(...) -> None:
        ...  # there are only 2 concurrent executions

    # the queue length will be recorded in the log when the function is overloaded
    log = logging.getLogger('concurrency_logger')

    @concurrency_limit(2, logger=log)
    async def my_task(...) -> None:
        ...  # there are only 2 concurrent executions
