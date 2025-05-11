import os
import json
import logging
from pathlib import Path
import shioaji as sj
from shioaji.account import StockAccount, FutureAccount

# 設定記錄檔
# 創建 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 創建文件處理器
file_handler = logging.FileHandler("sino_trader.log")
file_handler.setLevel(logging.INFO)

# 創建控制台處理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 創建格式化器
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 控制台輸出使用更簡潔的格式
console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console_handler.setFormatter(console_formatter)

# 添加處理器到 logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 永豐金證券 API class
class SinopacTrader:
    def __init__(self, simulation=False):
        """
        初始化 SinopacTrader 類別並自動登入
        
        Args:
            simulation (bool): 是否使用模擬環境，預設為 False (使用正式環境)
        """
        self.api = None
        self.logged_in = False
        self.stock_account = None
        self.future_account = None
        self.simulation = simulation
        
        # 嘗試登入
        try:
            # 讀取 API key 設定檔
            config_path = os.path.join(os.path.expanduser("~"), ".sinorc")
            if not os.path.exists(config_path):
                logger.error(f"設定檔不存在：{config_path}")
                return
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # 檢查設定檔是否包含必要的資訊
            if 'api_key' not in config or 'secret_key' not in config:
                logger.error("設定檔缺少 api_key 或 secret_key")
                return
            
            # 初始化 API 物件
            self.api = sj.Shioaji(simulation=self.simulation)
            
            # 使用 API key 和 Secret key 登入
            accounts = self.api.login(
                api_key=config['api_key'],
                secret_key=config['secret_key']
            )
            
            # 檢查登入狀態
            if accounts:
                logger.info("登入成功")
                self.logged_in = True
                
                # 取得股票和期貨帳戶
                for account in accounts:
                    if isinstance(account, StockAccount):
                        self.stock_account = account
                        logger.info(f"股票帳戶: {account.account_id}, 簽署: {account.signed}")
                    elif isinstance(account, FutureAccount):
                        self.future_account = account
                        logger.info(f"期貨帳戶: {account.account_id}, 簽署: {account.signed}")
                
                # 檢查是否已簽署
                if self.stock_account and self.stock_account.signed:
                    logger.info("股票帳戶已簽署，可以下單")
                if self.future_account and self.future_account.signed:
                    logger.info("期貨帳戶已簽署，可以下單")
            else:
                logger.error("登入失敗")
                
        except Exception as e:
            logger.error(f"登入過程發生錯誤: {e}")
            self.logged_in = False
    
    def get_inventory(self, account_type="stock", detail=False):
        """
        顯示庫存（股票或期貨持倉）
        
        Args:
            account_type (str): 帳戶類型，可為 "stock" 或 "future"，預設為 "stock"
            detail (bool): 是否顯示詳細資訊，預設為 False
        
        Returns:
            pandas.DataFrame 或 None: 持倉資訊，若發生錯誤則返回 None
        """
        if not self.logged_in:
            logger.error("尚未登入，無法獲取庫存資訊")
            return None
        
        try:
            # 根據帳戶類型選擇帳戶
            if account_type.lower() == "stock":
                if not self.stock_account:
                    logger.error("找不到股票帳戶")
                    return None
                # 獲取股票庫存
                if detail:
                    inventory = self.api.list_positions(self.stock_account)
                else:
                    inventory = self.api.position_summary(self.stock_account)
            elif account_type.lower() == "future":
                if not self.future_account:
                    logger.error("找不到期貨帳戶")
                    return None
                # 獲取期貨庫存
                if detail:
                    inventory = self.api.list_positions(self.future_account)
                else:
                    inventory = self.api.position_summary(self.future_account)
            else:
                logger.error(f"不支援的帳戶類型: {account_type}")
                return None
            
            # 轉換為 DataFrame 並顯示
            if inventory is not None and len(inventory) > 0:
                if detail:
                    logger.info(f"詳細庫存資訊:\n{inventory}")
                else:
                    logger.info(f"庫存摘要:\n{inventory}")
                return inventory
            else:
                logger.info("沒有持倉")
                return None
        except Exception as e:
            logger.error(f"獲取庫存資訊失敗: {e}")
            return None

if __name__ == "__main__":
    sino = SinopacTrader()
    sino.get_inventory(detail=True)
    