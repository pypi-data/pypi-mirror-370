import os
import requests
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urlencode

from .exceptions import MitakeError, AuthenticationError, APIError


class MitakeClient:
    """Mitake SMS API Client"""
    
    DEFAULT_BASE_URL = "https://smsapi.mitake.com.tw"
    
    def __init__(
        self, 
        username: Optional[str] = None, 
        password: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize Mitake SMS client
        
        Args:
            username: Mitake username (or set MITAKE_USERNAME env var)
            password: Mitake password (or set MITAKE_PASSWORD env var)
            base_url: API base URL (defaults to https://smsapi.mitake.com.tw)
        """
        self.username = username or os.getenv('MITAKE_USERNAME')
        self.password = password or os.getenv('MITAKE_PASSWORD')
        self.base_url = base_url or self.DEFAULT_BASE_URL
        
        if not self.username or not self.password:
            raise AuthenticationError(
                "Username and password are required. "
                "Set them via parameters or MITAKE_USERNAME/MITAKE_PASSWORD env vars."
            )
        
        self.session = requests.Session()
    
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Make HTTP request to Mitake API"""
        url = f"{self.base_url}/{endpoint}"
        
        # Add authentication to requests
        if params is None:
            params = {}
        params.update({
            'username': self.username,
            'password': self.password
        })
        
        try:
            if method.upper() == "POST":
                if isinstance(data, str):
                    # For batch SMS, send as raw data
                    response = self.session.post(url, data=data, params=params)
                else:
                    # For regular requests, send as form data
                    if data is None:
                        data = {}
                    response = self.session.post(url, data=data, params=params)
            else:
                # For GET requests, merge data into params
                if isinstance(data, dict):
                    params.update(data)
                response = self.session.get(url, params=params)
            
            # Check for HTTP errors
            if response.status_code >= 400:
                raise APIError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    response_data=response.text
                )
            
            return response
            
        except requests.RequestException as e:
            raise MitakeError(f"Request failed: {str(e)}")
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse Mitake API response"""
        content = response.text.strip()
        
        # Handle different response formats
        if content.startswith('[') and content.endswith(']'):
            # Array format like [1]
            return {'result': content}
        
        # Key-value format like "AccountPoint=1000"
        if '=' in content:
            result = {}
            for line in content.split('\n'):
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    result[key] = value
            return result
        
        # Plain text response
        return {'result': content}
    
    def send_sms(
        self, 
        to: str, 
        message: str,
        message_id: Optional[str] = None,
        send_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message
        
        Args:
            to: Recipient phone number (Taiwan format: 09xxxxxxxx)
            message: SMS message content
            message_id: Custom message ID (optional)
            send_time: Scheduled send time in YYYY-MM-DD HH:MM:SS format (optional)
        
        Returns:
            Dict containing the API response
        """
        data = {
            'dstaddr': to,
            'smbody': message
        }
        
        # Add UTF-8 encoding parameter by default
        params = {
            'CharsetURL': 'UTF8'
        }
        
        if message_id:
            data['msgid'] = message_id
        
        if send_time:
            data['dlvtime'] = send_time
        
        response = self._make_request('api/mtk/SmSend', method='POST', data=data, params=params)
        return self._parse_response(response)
    
    def send_batch_sms(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send multiple SMS messages
        
        Args:
            messages: List of message dicts with:
                - 'to': Recipient phone number (required)
                - 'message': SMS message content (required)
                - 'message_id': Custom message ID (optional)
                - 'send_time': Scheduled send time in YYYYMMDDHHMMSS format (optional)
                - 'valid_time': Message valid time in YYYYMMDDHHMMSS format (optional)
                - 'dest_name': Recipient name (optional)
                - 'callback_url': Status callback URL (optional)
        
        Returns:
            Dict containing the API response
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        # Build batch request data
        # Format: ClientID $$ dstaddr $$ dlvtime $$ vldtime $$ destname $$ response $$ smbody
        batch_lines = []
        for i, msg in enumerate(messages, 1):
            if 'to' not in msg or 'message' not in msg:
                raise ValueError(f"Message at index {i-1} must have 'to' and 'message' keys")
            
            client_id = msg.get('message_id', str(i))
            dstaddr = msg['to']
            dlvtime = msg.get('send_time', '')
            vldtime = msg.get('valid_time', '')
            destname = msg.get('dest_name', '')
            response = msg.get('callback_url', '')
            smbody = msg['message']
            
            line = f"{client_id}$${dstaddr}$${dlvtime}$${vldtime}$${destname}$${response}$${smbody}"
            batch_lines.append(line)
        
        # Join with newlines
        batch_data = '\n'.join(batch_lines)
        
        # Add UTF-8 encoding parameter by default
        params = {
            'Encoding_PostIn': 'UTF8'
        }
        
        response = self._make_request('api/mtk/SmBulkSend', method='POST', data=batch_data, params=params)
        return self._parse_response(response)
    
    def query_account_balance(self) -> Dict[str, Any]:
        """
        Query account balance/points
        
        Returns:
            Dict containing account balance information
        """
        response = self._make_request('api/mtk/SmQuery', method='GET')
        return self._parse_response(response)
    
    def query_message_status(self, message_ids: List[str]) -> Dict[str, Any]:
        """
        Query SMS message delivery status
        
        Args:
            message_ids: List of message IDs to query
        
        Returns:
            Dict containing message status information
        """
        if not message_ids:
            raise ValueError("Message IDs list cannot be empty")
        
        data = {
            'msgid': ','.join(message_ids)
        }
        
        response = self._make_request('api/mtk/SmQueryGet', method='GET', data=data)
        return self._parse_response(response)