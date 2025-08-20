#!/usr/bin/env python3
"""
簡訊發送功能測試
SMS Functionality Tests for Mitake SMS Python Library
"""

import unittest
from unittest.mock import Mock, patch
import os

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mitake import MitakeClient


class TestSingleSMS(unittest.TestCase):
    """測試單筆簡訊發送功能"""
    
    def setUp(self):
        """設定測試環境"""
        self.client = MitakeClient(username="test", password="test")
    
    @patch.object(MitakeClient, '_make_request')
    @patch.object(MitakeClient, '_parse_response')
    def test_send_sms_basic(self, mock_parse, mock_request):
        """測試基本簡訊發送"""
        mock_request.return_value = Mock()
        mock_parse.return_value = {'msgid': '#000000013', 'statuscode': '1'}
        
        result = self.client.send_sms("0912345678", "你好，我是小海！")
        
        # 檢查是否正確調用 _make_request
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'api/mtk/SmSend')
        self.assertEqual(kwargs['method'], 'POST')
        self.assertEqual(kwargs['data']['dstaddr'], '0912345678')
        self.assertEqual(kwargs['data']['smbody'], '你好，我是小海！')
        
        # 檢查是否包含 UTF-8 參數
        self.assertEqual(kwargs['params']['CharsetURL'], 'UTF8')
        
        self.assertEqual(result, {'msgid': '#000000013', 'statuscode': '1'})
    
    @patch.object(MitakeClient, '_make_request')
    @patch.object(MitakeClient, '_parse_response')
    def test_send_sms_with_options(self, mock_parse, mock_request):
        """測試帶選項參數的簡訊發送"""
        mock_request.return_value = Mock()
        mock_parse.return_value = {'msgid': '#000000014', 'statuscode': '1'}
        
        result = self.client.send_sms(
            "0912345678", 
            "預約發送測試",
            message_id="msg123",
            send_time="2024-12-31 23:59:00"
        )
        
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['data']['msgid'], 'msg123')
        self.assertEqual(kwargs['data']['dlvtime'], '2024-12-31 23:59:00')


class TestBatchSMS(unittest.TestCase):
    """測試批次簡訊發送功能"""
    
    def setUp(self):
        """設定測試環境"""
        self.client = MitakeClient(username="test", password="test")
    
    @patch.object(MitakeClient, '_make_request')
    @patch.object(MitakeClient, '_parse_response')
    def test_send_batch_sms_basic(self, mock_parse, mock_request):
        """測試基本批次發送"""
        mock_request.return_value = Mock()
        mock_parse.return_value = {'result': '[2]'}
        
        messages = [
            {"to": "0912345678", "message": "你好！這是第一則訊息"},
            {"to": "0987654321", "message": "你好！這是第二則訊息", "message_id": "msg2"}
        ]
        
        result = self.client.send_batch_sms(messages)
        
        # 檢查調用參數
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'api/mtk/SmBulkSend')
        self.assertEqual(kwargs['method'], 'POST')
        
        # 檢查批次格式
        batch_data = kwargs['data']
        self.assertIsInstance(batch_data, str)
        self.assertIn('0912345678', batch_data)
        self.assertIn('你好！這是第一則訊息', batch_data)
        self.assertIn('msg2', batch_data)
        
        # 檢查 UTF-8 編碼參數
        self.assertEqual(kwargs['params']['Encoding_PostIn'], 'UTF8')
    
    def test_send_batch_sms_empty_list(self):
        """測試空清單會拋出錯誤"""
        with self.assertRaises(ValueError):
            self.client.send_batch_sms([])
    
    def test_send_batch_sms_invalid_message(self):
        """測試無效訊息格式會拋出錯誤"""
        messages = [{"to": "0912345678"}]  # 缺少 'message' 欄位
        
        with self.assertRaises(ValueError) as context:
            self.client.send_batch_sms(messages)
        
        self.assertIn("must have 'to' and 'message' keys", str(context.exception))


if __name__ == '__main__':
    unittest.main()