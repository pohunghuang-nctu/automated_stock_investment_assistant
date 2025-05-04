# 自動化股票投資助理專案進度記錄

## 截至2025-05-03的專案進度

1. 已建立「全自動股票投資助理」(automated_stock_investment_assistant)主題資料夾，用於記錄和實驗與自動化股票投資相關的 AI 輔助功能。
2. 已有 FinMind API 相關資訊，可用於取得台股、匯率、黃金等金融資料，包括股價日成交資訊、綜合損益表與股利政策表等。
3. 用戶使用 pohung.huang@gmail.com 已註冊 FinMind 帳號，密碼重設問題已解決。帳號密碼訊息已存放在 Google Keep 中。
4. 已建立永豐金證券的 API key 和 secret key，並已將金鑰資訊保存在 Google Keep 中，API key 名稱為「開發 AI 助手用」。
5. 初步建立了 code_examples 資料夾，其中包含 call_finMind.py 檔案。
6. 已成功安裝 FinMind 和 tqdm 套件，並將 .finMind 配置檔案移至用戶主目錄 ($HOME)。
7. 已完成 call_finMind.py 示例程式的開發與測試，成功從 FinMind 獲取台積電(2454)的股價資料。
8. 已創建 requirements.txt 文件，記錄了專案所需的 Python 套件及其版本，方便環境復原。
9. 已在用戶主目錄 ($HOME) 下創建並設定 .netrc 文件，為將專案推送到 GitHub 做準備。

## 待處理事項

1. ~~解決 FinMind 密碼重設問題~~ (已完成於 2025-05-03，在 Gmail 垃圾郵件資料夾中找到了密碼重設郵件)
2. ~~完成 call_finMind.py 檔案的內容開發~~ (已完成於 2025-05-03)
3. 使用永豐金證券 API 進行功能開發
4. 將資料夾上傳到 GitHub

最後更新時間：2025-05-03 16:15
