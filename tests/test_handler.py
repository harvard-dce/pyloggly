# -*- coding: utf-8 -*-

import json
import logging
import unittest
import traceback
from mock import Mock, patch
from requests import RequestException
from pyloggly import LogglyHandler, LogglyBulkHandler

@patch('pyloggly.handler.atexit', new=Mock()) # disable atexit cleanup
class TestLogglyHandler(unittest.TestCase):

    def test_init(self):
        """test the various constructor options"""
        handler = LogglyHandler('my_token', 'my_domain', 'test-tag')
        self.assertEqual(handler.url, 'https://my_domain/inputs/my_token/tag/test-tag')
        handler = LogglyHandler('my_token', 'my_domain', 'tag1,tag:')
        self.assertEqual(handler.url, 'https://my_domain/inputs/my_token/tag/tag1,tag%3A')
        handler = LogglyHandler('my_token', 'my_domain')
        self.assertEqual(handler.url, 'https://my_domain/inputs/my_token/tag/pyloggly')
        handler = LogglyHandler('my_token', 'my_domain', fmt="%(foo)")
        self.assertEqual(handler.formatter._fmt, "%(foo)")

    def test_emit(self):
        """test basic emit"""
        handler = LogglyHandler('my_token', 'my_domain')
        handler.session = Mock()
        handler.format = Mock()
        handler.format.return_value = "foo"
        rec = Mock()
        handler.emit(rec)
        handler.format.assert_called_once_with(rec)
        handler.session.post.assert_called_once_with(
            handler.url, data="foo", background_callback=handler.resp_callback)

    def test_emit_json(self):
        """test emitting json"""
        handler = LogglyHandler('my_token', 'my_domain')
        handler.session = Mock()
        logger = logging.getLogger('test-emit-json')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.info("testing!")
        call_args, call_kwargs = handler.session.post.call_args
        # don't test every key, just that it's valid json
        data = json.loads(call_kwargs['data'])
        self.assertEqual(data['funcName'], 'test_emit_json')

    def test_custom_fmt(self):
        """test user-provided format"""
        handler = LogglyHandler('my_token', 'my_domain', fmt='{"message": "%(message)s"}')
        handler.session = Mock()
        logger = logging.getLogger('test-custom-fmt')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.info("testing!")
        expected = '{"message": "testing!"}'
        handler.session.post.assert_called_once_with(
            handler.url, data=expected, background_callback=handler.resp_callback)

    def test_emit_exc(self):
        """test exception data included in event"""
        handler = LogglyHandler('my_token', 'my_domain')
        handler.session = Mock()
        logger = logging.getLogger('test-emit-exc')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        try:
            raise Exception("boom!")
        except:
            logger.error("Something went boom!", exc_info=True)
            expected_exc_info_value = traceback.format_exc()
        call_args, call_kwargs = handler.session.post.call_args
        data = json.loads(call_kwargs['data'])
        self.assertTrue('exc_info' in data)
        self.assertTrue(data['exc_info'], expected_exc_info_value)

    def test_post_exc(self):
        exc_cb = Mock()
        exc = RequestException('boom!')
        handler = LogglyHandler('my_token', 'my_domain', exc_callback=exc_cb)
        handler.session = Mock()
        handler.session.post.side_effect = exc
        logger = logging.getLogger('test-post-exc')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.info("this is a test")
        exc_cb.assert_called_once_with(exc)

    def test_bulk_init(self):
        handler = LogglyBulkHandler('my_token', 'my_domain', 'test-tag')
        self.assertEqual(handler.url, 'https://my_domain/bulk/my_token/tag/test-tag')

    def test_bulk_emit(self):
        handler = LogglyBulkHandler('my_token', 'my_domain', 'test-tag')
        handler.flush = Mock()
        logger = logging.getLogger('test-bulk-emit')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.info("this is a test")
        self.assertEqual(len(handler.events), 1)
        logger.info("this is another test")
        logger.info("and another")
        self.assertEqual(len(handler.events), 3)

    def test_bulk_flush(self):
        handler = LogglyBulkHandler('my_token', 'my_domain', 'test-tag')
        handler.session = Mock()
        logger = logging.getLogger('test-bulk-emit')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.info("this is a test")
        handler.flush()
        handler.session.post.assert_called_once()

    def test_assert_batch_size_flush(self):
        handler = LogglyBulkHandler('my_token', 'my_domain', 'test-tag',
                                    batch_size=2)
        handler.session = Mock()
        logger = logging.getLogger('test-bulk-emit')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.info("this is a test")
        self.assertEqual(len(handler.events), 1)
        logger.info("this is another test")
        handler.session.post.assert_called_once()
        self.assertEqual(len(handler.events), 0)
