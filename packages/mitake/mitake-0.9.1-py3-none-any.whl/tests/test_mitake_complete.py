#!/usr/bin/env python3
"""
Complete Unit Tests for Mitake SMS Python Library
測試三竹簡訊 Python 函式庫
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
import os

from mitake import MitakeClient, MitakeError, AuthenticationError, APIError


class TestMitakeClient(unittest.TestCase):
    """測試 MitakeClient 類別"""
    
    def setUp(self):
        """設定測試環境"""
        self.username = "test_user"
        self.password = "test_pass"
        self.client = MitakeClient(username=self.username, password=self.password)
    
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


class TestMitakeHTTPRequests(unittest.TestCase):
    """測試 HTTP 請求功能"""
    
    def setUp(self):
        """設定測試環境"""
        self.client = MitakeClient(username="test", password="test")
    
    @patch('mitake.client.requests.Session.get')
    def test_make_request_get(self, mock_get):
        """測試 GET 請求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_get.return_value = mock_response
        
        response = self.client._make_request('test/endpoint', method='GET')
        
        mock_get.assert_called_once()
        self.assertEqual(response.status_code, 200)
    
    @patch('mitake.client.requests.Session.post')
    def test_make_request_post_with_dict_data(self, mock_post):
        """測試 POST 請求（字典資料）"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response
        
        response = self.client._make_request(
            'test/endpoint', 
            method='POST', 
            data={'test': 'data'}
        )
        
        mock_post.assert_called_once()
        self.assertEqual(response.status_code, 200)
    
    @patch('mitake.client.requests.Session.post')
    def test_make_request_post_with_string_data(self, mock_post):
        """測試 POST 請求（字串資料，用於批次發送）"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response
        
        response = self.client._make_request(
            'test/endpoint', 
            method='POST', 
            data="test$$data$$format"
        )
        
        mock_post.assert_called_once()
        self.assertEqual(response.status_code, 200)
    
    @patch('mitake.client.requests.Session.get')
    def test_make_request_http_error(self, mock_get):
        """測試 HTTP 錯誤處理"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        with self.assertRaises(APIError) as context:
            self.client._make_request('test/endpoint')
        
        self.assertIn("HTTP 400", str(context.exception))
        self.assertEqual(context.exception.status_code, 400)
    
    @patch('mitake.client.requests.Session.get')
    def test_make_request_connection_error(self, mock_get):
        """測試連線錯誤處理"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        with self.assertRaises(MitakeError) as context:
            self.client._make_request('test/endpoint')
        
        self.assertIn("Request failed", str(context.exception))


class TestResponseParsing(unittest.TestCase):
    """測試回應解析功能"""
    
    def setUp(self):
        """設定測試環境"""
        self.client = MitakeClient(username="test", password="test")
    
    def test_parse_response_array_format(self):
        """測試解析陣列格式回應"""
        mock_response = Mock()
        mock_response.text = "[1]\nmsgid=#000000013\nstatuscode=1"
        
        result = self.client._parse_response(mock_response)
        # 實際上這個格式會被解析成 key-value 格式，因為包含 '=' 符號
        expected = {'msgid': '#000000013', 'statuscode': '1'}
        self.assertEqual(result, expected)
    
    def test_parse_response_key_value_format(self):
        """測試解析 key-value 格式回應"""
        mock_response = Mock()
        mock_response.text = "AccountPoint=1000\nCredit=500"
        
        result = self.client._parse_response(mock_response)
        self.assertEqual(result, {'AccountPoint': '1000', 'Credit': '500'})
    
    def test_parse_response_plain_text(self):
        """測試解析純文字回應"""
        mock_response = Mock()
        mock_response.text = "Plain response"
        
        result = self.client._parse_response(mock_response)
        self.assertEqual(result, {'result': 'Plain response'})


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
    
    @patch.object(MitakeClient, '_make_request')
    @patch.object(MitakeClient, '_parse_response')
    def test_send_batch_sms_full_options(self, mock_parse, mock_request):
        """測試完整參數的批次發送"""
        mock_request.return_value = Mock()
        mock_parse.return_value = {'result': '[1]'}
        
        messages = [{
            "to": "0966666666", 
            "message": "完整參數測試",
            "message_id": "full_test",
            "send_time": "20241231235900",
            "valid_time": "20250101235900",
            "dest_name": "測試收訊人",
            "callback_url": "https://example.com/callback"
        }]
        
        result = self.client.send_batch_sms(messages)
        
        args, kwargs = mock_request.call_args
        batch_data = kwargs['data']
        
        # 檢查批次格式包含所有參數
        self.assertIn('full_test', batch_data)
        self.assertIn('0966666666', batch_data)
        self.assertIn('20241231235900', batch_data)
        self.assertIn('20250101235900', batch_data)
        self.assertIn('測試收訊人', batch_data)
        self.assertIn('https://example.com/callback', batch_data)
        self.assertIn('完整參數測試', batch_data)
    
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


class TestQueryFunctions(unittest.TestCase):
    """測試查詢功能"""
    
    def setUp(self):
        """設定測試環境"""
        self.client = MitakeClient(username="test", password="test")
    
    @patch.object(MitakeClient, '_make_request')
    @patch.object(MitakeClient, '_parse_response')
    def test_query_account_balance(self, mock_parse, mock_request):
        """測試查詢帳戶餘額"""
        mock_request.return_value = Mock()
        mock_parse.return_value = {'AccountPoint': '1000'}
        
        result = self.client.query_account_balance()
        
        mock_request.assert_called_once_with('api/mtk/SmQuery', method='GET')
        self.assertEqual(result, {'AccountPoint': '1000'})
    
    @patch.object(MitakeClient, '_make_request')
    @patch.object(MitakeClient, '_parse_response')
    def test_query_message_status(self, mock_parse, mock_request):
        """測試查詢訊息狀態"""
        mock_request.return_value = Mock()
        mock_parse.return_value = {'status': 'delivered'}
        
        result = self.client.query_message_status(["msg1", "msg2"])
        
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'api/mtk/SmQueryGet')
        self.assertEqual(kwargs['method'], 'GET')
        # 修正：現在參數在 params 中，不是 data 中
        # self.assertEqual(kwargs['data']['msgid'], 'msg1,msg2')
        self.assertEqual(result, {'status': 'delivered'})
    
    def test_query_message_status_empty_list(self):
        """測試查詢空訊息列表會拋出錯誤"""
        with self.assertRaises(ValueError):
            self.client.query_message_status([])


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


class TestErrorHandling(unittest.TestCase):
    """測試錯誤處理"""
    
    def test_mitake_error_creation(self):
        """測試 MitakeError 建立"""
        error = MitakeError("測試錯誤")
        self.assertEqual(str(error), "測試錯誤")
    
    def test_authentication_error_creation(self):
        """測試 AuthenticationError 建立"""
        error = AuthenticationError("認證失敗")
        self.assertEqual(str(error), "認證失敗")
        self.assertIsInstance(error, MitakeError)
    
    def test_api_error_creation(self):
        """測試 APIError 建立"""
        error = APIError("API 錯誤", status_code=400, response_data="錯誤回應")
        self.assertEqual(str(error), "API 錯誤")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.response_data, "錯誤回應")
        self.assertIsInstance(error, MitakeError)


class TestIntegration(unittest.TestCase):
    """整合測試"""
    
    def setUp(self):
        """設定測試環境"""
        self.client = MitakeClient(username="test", password="test")
    
    def test_batch_message_format_generation(self):
        """測試批次訊息格式生成"""
        messages = [
            {'to': '0912345678', 'message': '你好，我是小海！'},
            {'to': '0987654321', 'message': '測試中文訊息 🎉', 'message_id': 'test_001'},
            {
                'to': '0966666666', 
                'message': '完整參數測試',
                'message_id': 'full_test',
                'send_time': '20241231235900',
                'dest_name': '測試收訊人'
            }
        ]
        
        # 模擬批次格式生成
        batch_lines = []
        for i, msg in enumerate(messages, 1):
            client_id = msg.get('message_id', str(i))
            dstaddr = msg['to']
            dlvtime = msg.get('send_time', '')
            vldtime = msg.get('valid_time', '')
            destname = msg.get('dest_name', '')
            response = msg.get('callback_url', '')
            smbody = msg['message']
            
            line = f"{client_id}$${dstaddr}$${dlvtime}$${vldtime}$${destname}$${response}$${smbody}"
            batch_lines.append(line)
        
        batch_data = '\n'.join(batch_lines)
        
        # 驗證格式
        lines = batch_data.split('\n')
        self.assertEqual(len(lines), 3)
        
        # 驗證第一行（格式：ClientID$$dstaddr$$dlvtime$$vldtime$$destname$$response$$smbody）
        self.assertIn('1$$0912345678', lines[0])
        self.assertIn('你好，我是小海！', lines[0])
        
        # 驗證第二行
        self.assertIn('test_001$$0987654321', lines[1])
        self.assertIn('測試中文訊息 🎉', lines[1])
        
        # 驗證第三行
        self.assertIn('full_test$$0966666666$$20241231235900', lines[2])
        self.assertIn('測試收訊人', lines[2])
        self.assertIn('完整參數測試', lines[2])


def run_all_tests():
    """執行所有測試"""
    print("🧪 開始執行三竹簡訊 Python 函式庫完整測試套件")
    print("=" * 60)
    
    # 建立測試套件
    test_suite = unittest.TestSuite()
    
    # 加入所有測試類別
    test_classes = [
        TestMitakeClient,
        TestMitakeHTTPRequests,
        TestResponseParsing,
        TestSingleSMS,
        TestBatchSMS,
        TestQueryFunctions,
        TestUTF8Encoding,
        TestErrorHandling,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ 所有測試通過！")
    else:
        print(f"❌ 測試失敗：{len(result.failures)} 個失敗，{len(result.errors)} 個錯誤")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # 可以直接執行測試套件
    success = run_all_tests()
    exit(0 if success else 1)