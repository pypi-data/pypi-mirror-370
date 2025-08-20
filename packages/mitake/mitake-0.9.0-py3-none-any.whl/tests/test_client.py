#!/usr/bin/env python3
"""
客戶端測試
Client Tests for Mitake SMS Python Library
"""

import unittest
from unittest.mock import Mock, patch
import os

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mitake import MitakeClient, MitakeError, AuthenticationError, APIError


class TestMitakeClientInit(unittest.TestCase):
    """測試客戶端初始化"""
    
    def test_init_with_credentials(self):
        """測試使用帳號密碼初始化"""
        client = MitakeClient(username="user", password="pass")
        self.assertEqual(client.username, "user")
        self.assertEqual(client.password, "pass")
        self.assertEqual(client.base_url, MitakeClient.DEFAULT_BASE_URL)
    
    def test_init_without_credentials_raises_error(self):
        """測試沒有提供帳號密碼會拋出錯誤"""
        with self.assertRaises(AuthenticationError):
            MitakeClient()
    
    @patch.dict('os.environ', {'MITAKE_USERNAME': 'env_user', 'MITAKE_PASSWORD': 'env_pass'})
    def test_init_with_env_vars(self):
        """測試使用環境變數初始化"""
        client = MitakeClient()
        self.assertEqual(client.username, "env_user")
        self.assertEqual(client.password, "env_pass")
    
    def test_custom_base_url(self):
        """測試自訂 API 網址"""
        custom_url = "https://custom.example.com"
        client = MitakeClient(
            username="user", 
            password="pass", 
            base_url=custom_url
        )
        self.assertEqual(client.base_url, custom_url)


if __name__ == '__main__':
    unittest.main()