# -*- coding: utf-8 -*-

import json
import logging
import unittest
from mock import Mock
from requests import RequestException
from pyloggly import LogglyHandler

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
        call_args, call_kwargs = handler.session.post.call_args
        data = json.loads(call_kwargs['data'])
        self.assertTrue('exc_info' in data)
        self.assertTrue(isinstance(data['exc_info'], list))
        self.assertEqual(data['exc_info'][1], 'Exception: boom!')

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
