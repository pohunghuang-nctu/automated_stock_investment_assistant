from FinMind.data import DataLoader
import json
import os

# 初始化資料載入器
dl = DataLoader()

# 未登入使用 (有使用限制)
# 獲取台灣股票資訊


# 或直接使用 token
# read token from .finMind (json format, key is "token")
with open(os.path.join(os.path.expanduser("~"), ".finMind"), "r") as f:
    api_token = json.load(f)["token"]
dl.login_by_token(api_token=api_token)

stock_data = dl.taiwan_stock_daily(
    stock_id="2454",
    start_date="2025-01-01",
    end_date="2025-05-01"
)

print(stock_data)
