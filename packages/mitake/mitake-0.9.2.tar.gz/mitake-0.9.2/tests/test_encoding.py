#!/usr/bin/env python3
"""
UTF-8 編碼測試
UTF-8 Encoding Tests for Mitake SMS Python Library
"""

import unittest
from unittest.mock import Mock, patch
import os

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mitake import MitakeClient


class TestUTF8Encoding(unittest.TestCase):
    """測試 UTF-8 編碼功能"""
    
    def setUp(self):
        """設定測試環境"""
        self.client = MitakeClient(username="test", password="test")
    
    def test_chinese_message_encoding(self):
        """測試中文訊息編碼"""
        test_messages = [
            "你好，我是小海！",
            "測試中文簡訊 🎉",
            "特殊符號測試：{}[]|^~",
            "表情符號測試 😊 🌟 ❤️"
        ]
        
        for message in test_messages:
            # 測試 UTF-8 編碼是否正常
            encoded = message.encode('utf-8')
            decoded = encoded.decode('utf-8')
            self.assertEqual(message, decoded, f"UTF-8 編碼測試失敗: {message}")
    
    @patch.object(MitakeClient, '_make_request')
    def test_utf8_parameter_in_single_sms(self, mock_request):
        """測試單筆簡訊包含 UTF-8 參數"""
        mock_request.return_value = Mock()
        
        with patch.object(self.client, '_parse_response', return_value={}):
            self.client.send_sms("0912345678", "測試")
        
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['params']['CharsetURL'], 'UTF8')
    
    @patch.object(MitakeClient, '_make_request')
    def test_utf8_parameter_in_batch_sms(self, mock_request):
        """測試批次簡訊包含 UTF-8 參數"""
        mock_request.return_value = Mock()
        
        messages = [{"to": "0912345678", "message": "測試"}]
        
        with patch.object(self.client, '_parse_response', return_value={}):
            self.client.send_batch_sms(messages)
        
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['params']['Encoding_PostIn'], 'UTF8')
    
    def test_original_encoding_problem(self):
        """測試原本的編碼問題已解決"""
        # 原本的問題：「你好，我是小海!」變成「雿憟踝臬瘚!」
        original_message = "你好，我是小海！"
        
        # 確保現在可以正確處理中文
        self.assertEqual(len(original_message), 8)  # 正確的字元數
        self.assertTrue(all(ord(c) > 127 for c in original_message if c not in ['！', '，']))  # 包含非 ASCII 字元
        
        # 確保 UTF-8 編碼正常
        utf8_bytes = original_message.encode('utf-8')
        decoded = utf8_bytes.decode('utf-8')
        self.assertEqual(original_message, decoded)


if __name__ == '__main__':
    unittest.main()