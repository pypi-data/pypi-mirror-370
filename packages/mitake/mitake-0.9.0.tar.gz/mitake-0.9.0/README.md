# 三竹簡訊 Python 函式庫

三竹簡訊 API 的 Python 包裝函式庫，讓您可以透過台灣三竹簡訊服務發送簡訊。

## 特色

- ✅ **預設 UTF-8 編碼**：完美支援中文簡訊，不會出現亂碼
- ✅ **單筆與批次發送**：支援單筆與批次簡訊發送
- ✅ **預約發送**：支援預約時間發送簡訊
- ✅ **狀態查詢**：查詢簡訊發送狀態與帳戶餘額
- ✅ **錯誤處理**：完整的錯誤處理機制
- ✅ **易於使用**：簡潔的 API 設計

## 安裝

```bash
pip install -e .
```

## 快速開始

### 基本設定

```python
from mitake import MitakeClient

# 方法 1：直接輸入帳號密碼
client = MitakeClient(username="your_username", password="your_password")

# 方法 2：使用環境變數
# 設定 MITAKE_USERNAME 和 MITAKE_PASSWORD 環境變數
client = MitakeClient()
```

### 發送單筆簡訊

```python
# 發送中文簡訊（自動使用 UTF-8 編碼，不會有亂碼問題）
result = client.send_sms(
    to="0912345678",  # 台灣手機號碼
    message="你好，我是小海！這是測試訊息 🎉"
)
print(result)
```

### 發送批次簡訊

```python
messages = [
    {"to": "0912345678", "message": "嗨！這是第一則訊息"},
    {"to": "0987654321", "message": "嗨！這是第二則訊息", "message_id": "custom_id_1"},
    {
        "to": "0966666666", 
        "message": "這是完整參數的訊息",
        "message_id": "full_example",
        "send_time": "20241231235900",  # YYYYMMDDHHMMSS 格式
        "dest_name": "收訊人姓名"
    }
]

result = client.send_batch_sms(messages)
print(result)
```

### 預約發送

```python
# 預約指定時間發送簡訊
result = client.send_sms(
    to="0912345678",
    message="這是預約發送的簡訊！",
    send_time="2024-12-31 23:59:00"  # YYYY-MM-DD HH:MM:SS 格式
)
```

### 查詢帳戶餘額

```python
balance = client.query_account_balance()
print(f"帳戶餘額：{balance}")
```

### 查詢簡訊狀態

```python
# 查詢已發送簡訊的狀態
status = client.query_message_status(["message_id_1", "message_id_2"])
print(status)
```

## 環境變數設定

您可以使用環境變數來設定認證資訊：

```bash
export MITAKE_USERNAME="你的帳號"
export MITAKE_PASSWORD="你的密碼"
```

## 錯誤處理

```python
from mitake import MitakeClient, MitakeError, AuthenticationError, APIError

try:
    client = MitakeClient()
    result = client.send_sms("0912345678", "測試訊息")
except AuthenticationError as e:
    print(f"認證失敗：{e}")
except APIError as e:
    print(f"API 錯誤：{e}")
    print(f"狀態碼：{e.status_code}")
    print(f"回應內容：{e.response_data}")
except MitakeError as e:
    print(f"三竹簡訊錯誤：{e}")
```

## API 方法

### send_sms(to, message, message_id=None, send_time=None)
發送單筆簡訊

**參數：**
- `to` (str): 收訊人手機號碼（台灣格式：09xxxxxxxx）
- `message` (str): 簡訊內容
- `message_id` (str, 可選): 自訂訊息 ID
- `send_time` (str, 可選): 預約發送時間（YYYY-MM-DD HH:MM:SS 格式）

### send_batch_sms(messages)
發送批次簡訊

**參數：**
- `messages` (List[Dict]): 訊息列表，每個訊息包含：
  - `to` (str): 收訊人手機號碼（必填）
  - `message` (str): 簡訊內容（必填）
  - `message_id` (str, 可選): 自訂訊息 ID
  - `send_time` (str, 可選): 預約發送時間（YYYYMMDDHHMMSS 格式）
  - `valid_time` (str, 可選): 訊息有效時間（YYYYMMDDHHMMSS 格式）
  - `dest_name` (str, 可選): 收訊人姓名
  - `callback_url` (str, 可選): 狀態回報網址

### query_account_balance()
查詢帳戶餘額

### query_message_status(message_ids)
查詢簡訊發送狀態

**參數：**
- `message_ids` (List[str]): 要查詢的訊息 ID 列表

## UTF-8 編碼支援

本函式庫預設使用 UTF-8 編碼，完美支援中文簡訊：

```python
# ✅ 正確：支援中文、表情符號等
client.send_sms("0912345678", "你好！今天天氣真好 ☀️")

# ✅ 正確：支援各種特殊字元
client.send_sms("0912345678", "測試特殊符號：{} [] | ^ ~ 等等")
```

## 系統需求

- Python 3.7+
- requests 函式庫

## 授權條款

MIT License

## 開發者

使用前請確保您已向三竹資訊申請 API 發送權限，並提供程式發送主機的 IP 位址進行鎖定。

更多 API 詳細資訊請參考：[三竹簡訊 API 文件](HTTP_MitakeAPI_v2.14.pdf)