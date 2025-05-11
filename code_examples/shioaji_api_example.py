"""
永豐金證券 Shioaji Python API 使用範例
此腳本展示如何使用永豐金證券的 Shioaji API 進行基本操作
包括：登入、獲取行情資料、下單等功能
"""

import os
import time
import json
from dotenv import load_dotenv
import shioaji as sj
from shioaji import constant
from shioaji.account import StockAccount, FutureAccount
from shioaji.order import Status as OrderStatus
from shioaji.position import Position
import pandas as pd

# 載入環境變數
load_dotenv()

class SinopacTrader:
    def __init__(self):
        self.api = None
        self.logged_in = False
        self.stock_account = None
        self.future_account = None
    
    def login(self, simulation=True, api_key=None, secret_key=None, person_id=None, password=None, 
              cert_path=None, cert_password=None):
        """登入永豐金證券 API"""
        try:
            # 初始化 API 物件
            self.api = sj.Shioaji(simulation=simulation)
            
            # 方法一：使用 API Key 和 Secret Key 登入
            if api_key and secret_key:
                accounts = self.api.login(
                    api_key=api_key,
                    secret_key=secret_key
                )
            # 方法二：使用身分證號、密碼和憑證登入
            elif person_id and password and cert_path:
                if cert_password is None:
                    cert_password = person_id  # 憑證密碼預設為身分證字號
                
                # 注意：憑證路徑要用斜線(/)，不要用反斜線(\)
                cert_path = cert_path.replace('\\', '/')
                
                accounts = self.api.login(
                    person_id=person_id,
                    password=password,
                    ca_path=cert_path,
                    ca_passwd=cert_password,
                    encrypt_passwd=True  # 加密傳輸密碼
                )
            else:
                print("錯誤：缺少登入參數")
                return False
            
            # 檢查登入狀態
            if accounts:
                print("登入成功")
                self.logged_in = True
                
                # 取得股票和期貨帳戶
                for account in accounts:
                    if isinstance(account, StockAccount):
                        self.stock_account = account
                        print(f"股票帳戶: {account.account_id}")
                    elif isinstance(account, FutureAccount):
                        self.future_account = account
                        print(f"期貨帳戶: {account.account_id}")
                
                # 檢查是否已簽署
                if self.stock_account and self.stock_account.signed:
                    print("股票帳戶已簽署，可以下單")
                if self.future_account and self.future_account.signed:
                    print("期貨帳戶已簽署，可以下單")
                
                return True
            else:
                print("登入失敗")
                return False
                
        except Exception as e:
            print(f"登入過程發生錯誤: {e}")
            return False
    
    def get_ticks(self, contract_id):
        """取得合約的Tick資料"""
        if not self.logged_in:
            print("尚未登入，無法獲取Tick資料")
            return None
        
        try:
            # 取得合約資訊
            contract = self.api.Contracts.Stocks[contract_id]
            ticks = self.api.ticks(contract, 10)  # 取得最新的10筆tick資料
            return ticks
        except Exception as e:
            print(f"獲取Tick資料失敗: {e}")
            return None
    
    def get_kbars(self, contract_id, start_date, end_date=None):
        """取得合約的K線資料"""
        if not self.logged_in:
            print("尚未登入，無法獲取K線資料")
            return None
        
        try:
            # 取得合約資訊
            contract = self.api.Contracts.Stocks[contract_id]
            
            # 如果沒有指定結束日期，使用今天
            if not end_date:
                end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
                
            # 取得K線資料
            kbars = self.api.kbars(contract, start_date, end_date)
            return kbars
        except Exception as e:
            print(f"獲取K線資料失敗: {e}")
            return None
    
    def place_order(self, contract_id, price, quantity, action, order_type, price_type, 
                    account_type="stock", custom_id=None):
        """下單"""
        if not self.logged_in:
            print("尚未登入，無法下單")
            return None
        
        try:
            # 根據帳戶類型選擇帳戶
            if account_type.lower() == "stock":
                if not self.stock_account:
                    print("找不到股票帳戶")
                    return None
                account = self.stock_account
                contract = self.api.Contracts.Stocks[contract_id]
            elif account_type.lower() == "future":
                if not self.future_account:
                    print("找不到期貨帳戶")
                    return None
                account = self.future_account
                contract = self.api.Contracts.Futures[contract_id]
            else:
                print(f"不支援的帳戶類型: {account_type}")
                return None
            
            # 檢查帳戶是否已簽署
            if not account.signed:
                print(f"{account_type}帳戶尚未簽署，無法下單")
                return None
            
            # 根據參數設置下單選項
            action_map = {
                "buy": sj.constant.Action.Buy,
                "sell": sj.constant.Action.Sell
            }
            order_type_map = {
                "market": sj.constant.OrderType.Market,
                "limit": sj.constant.OrderType.Limit,
                "fixed": sj.constant.OrderType.Limit
            }
            price_type_map = {
                "day": sj.constant.TimeInForce.Day,
                "fok": sj.constant.TimeInForce.FOK,
                "ioc": sj.constant.TimeInForce.IOC,
                "rod": sj.constant.TimeInForce.ROD
            }
            
            # 轉換成API需要的格式
            action_code = action_map.get(action.lower())
            order_type_code = order_type_map.get(order_type.lower())
            price_type_code = price_type_map.get(price_type.lower())
            
            if not action_code:
                print(f"不支援的交易方向: {action}")
                return None
            if not order_type_code:
                print(f"不支援的委託類型: {order_type}")
                return None
            if not price_type_code:
                print(f"不支援的價格類型: {price_type}")
                return None
            
            # 下單
            order = self.api.Order(
                price=price,
                quantity=quantity,
                action=action_code,
                order_type=order_type_code,
                price_type=price_type_code,
                custom_id=custom_id
            )
            
            # 送出委託
            trade = self.api.place_order(contract, order, account)
            
            print(f"下單結果: {trade}")
            return trade
            
        except Exception as e:
            print(f"下單過程發生錯誤: {e}")
            return None
    
    def get_positions(self, account_type="stock"):
        """獲取持倉資訊"""
        if not self.logged_in:
            print("尚未登入，無法獲取持倉資訊")
            return None
        
        try:
            # 根據帳戶類型選擇帳戶
            if account_type.lower() == "stock":
                if not self.stock_account:
                    print("找不到股票帳戶")
                    return None
                positions = self.api.position_summary()
            elif account_type.lower() == "future":
                if not self.future_account:
                    print("找不到期貨帳戶")
                    return None
                positions = self.api.position_summary(self.future_account)
            else:
                print(f"不支援的帳戶類型: {account_type}")
                return None
            
            return positions
        except Exception as e:
            print(f"獲取持倉資訊失敗: {e}")
            return None
    
    def logout(self):
        """登出"""
        if not self.logged_in:
            print("尚未登入，無需登出")
            return True
        
        try:
            self.api.logout()
            self.logged_in = False
            print("登出成功")
            return True
        except Exception as e:
            print(f"登出過程發生錯誤: {e}")
            return False


def main():
    """主函數，展示如何使用 SinopacTrader 類別"""
    
    # 創建交易者實例
    trader = SinopacTrader()
    
    # 方法一：使用 API Key 和 Secret Key 登入
    '''
    login_success = trader.login(
        simulation=True,  # 使用模擬環境
        api_key=os.getenv('API_KEY'),
        secret_key=os.getenv('SECRET_KEY')
    )
    '''
    
    # 方法二：使用身分證號、密碼和憑證登入
    login_success = trader.login(
        simulation=True,  # 使用模擬環境
        person_id="您的身分證字號",
        password="您的密碼",
        cert_path=r"c:\ekey\551\F122263954\S\Sinopac.pfx",
        # cert_password 留空則使用身分證字號作為憑證密碼
    )
    
    if not login_success:
        print("登入失敗，程式結束")
        return
    
    try:
        # 獲取台積電的K線資料
        kbars = trader.get_kbars("2330", "2025-01-01")
        if kbars is not None:
            print("台積電K線資料:")
            print(kbars)
        
        # 獲取台積電的Tick資料
        ticks = trader.get_ticks("2330")
        if ticks is not None:
            print("台積電Tick資料:")
            print(ticks)
        
        # 獲取持倉資訊
        positions = trader.get_positions()
        if positions is not None:
            print("持倉資訊:")
            print(positions)
        
        # 模擬下單（注意：這是一個模擬的例子，不會實際下單）
        # 實際使用時請務必謹慎，確認價格和數量
        if input("是否進行下單測試？(y/n): ").lower() == 'y':
            trade = trader.place_order(
                contract_id="2330",  # 台積電
                price=500.0,         # 價格
                quantity=1,          # 數量
                action="Buy",        # 買入
                order_type="Limit",  # 限價單
                price_type="ROD",    # 當日有效
                account_type="stock" # 股票帳戶
            )
            if trade:
                print(f"下單結果: {trade}")
    
    finally:
        # 確保登出
        trader.logout()
        print("程式結束")


if __name__ == "__main__":
    main()
