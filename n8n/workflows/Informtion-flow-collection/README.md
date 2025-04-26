# n8n 自動化工作流：多來源資訊蒐集、分類與摘要 Agent (Information_collecit_and_summary_agent)

此 n8n 工作流程旨在自動化從多個來源（GNews API、RSS Feed、Gmail）蒐集資訊，利用 AI 模型進行分類、評分、摘要，並將結果整理儲存至 Google Sheets 的過程。

## 重要資源

*   [工作流程文件](./Information_collecit_and_summary_agent.json)
*   [Google Sheets 模板](https://drive.google.com/drive/folders/1XabN8iitvIj9reyP14dAVYylC8TPNwzw?usp=sharing)


## 工作流程概覽

本工作流程主要分為以下幾個階段：

1.  **觸發與初始化:**
    *   透過 **排程觸發 (Schedule Trigger)** 定期啟動。
    *   讀取上次執行的時間戳 (`/tmp/lastCheckFile`)，用於過濾新資訊。

2.  **資訊來源蒐集:**
    *   **來源一：GNews API (關鍵字新聞)**
        *   從 Google Sheet (`0_Web Search / RSS / subscription` -> `Web Search Keywords`) 讀取關鍵字。
        *   根據關鍵字和上次檢查時間，透過 GNews API 查詢美國 (us) 和台灣 (tw) 的新聞。
        *   將獲取的新聞（標題、描述、內容片段、發布時間、URL）暫存至 Google Sheet (`news_database` -> `web-search_temp_news`)，並標記為 `checked: No`。
    *   **來源二：RSS Feed (FreshRSS)**
        *   透過 HTTP Request 從自架的 FreshRSS 服務獲取指定時間範圍內的 RSS 項目。
        *   解析 XML 回應，提取文章資訊 (標題、連結、描述、發布日期、GUID)。
        *   過濾掉上次檢查時間之前的文章 (`Time Check Filter`)。
        *   使用正則表達式過濾標題和描述中包含特定 AI 相關關鍵字的文章 (`keyword filter`)。
        *   將文章描述從 HTML 轉換為 Markdown (`Markdown1`)。
        *   **迴圈處理每個 RSS 文章:**
            *   使用 **Google Gemini AI Agent (Categorization & Summerization)** 進行分類和摘要。
                *   輸入：文章標題、Markdown 格式的描述。
                *   任務：生成 Markdown 格式摘要，並分類文章主題、評估相關性分數 (`relevance_score`) 和重要性分數 (`importance`)。
                *   輸出：包含摘要、分類、分數的 JSON。
            *   解析 AI 輸出，整理欄位。
            *   過濾掉分類為 "Other" 的文章 (`If3`)。
            *   將處理後的文章資訊（含摘要、分類、分數）寫入 Google Sheet (`news_database` -> `news_database`)，標記 `status: 2 - Summarized`。
    *   **來源三：Gmail (訂閱信件)**
        *   讀取指定 Gmail 標籤 (`Label_8982256647532788657`) 中，上次檢查時間之後收到的郵件。
        *   提取郵件主旨、內文 (純文字)、日期、Thread ID。
        *   **迴圈處理每封郵件:**
            *   使用 **Google Gemini AI Agent (Categorization)** 進行分類和摘要。
                *   輸入：郵件主旨、內文。
                *   任務：同 RSS 處理，生成 Markdown 摘要並分類、評分。
                *   輸出：包含摘要、分類、分數的 JSON。
            *   解析 AI 輸出，整理欄位。
            *   過濾掉分類為 "Other" 的文章 (`If`)。
            *   將處理後的郵件資訊寫入 Google Sheet (`news_database` -> `news_database`)，標記 `status: 2 - Summarized`。

3.  **GNews 新聞處理 - 分類 (Step 2):**
    *   從 `web-search_temp_news` 讀取 `checked: No` 的新聞。
    *   **迴圈處理每則 GNews 新聞:**
        *   使用 **Google Gemini AI Agent (Categorization2)** 進行分類。
            *   輸入：新聞標題、描述、內容片段。
            *   任務：分類文章主題、評估相關性分數 (`relevance_score`) 和重要性分數 (`importance`)。
            *   輸出：包含分類和分數的 JSON。
        *   解析 AI 輸出。
        *   將分類結果（`category`, `relevance_score`, `importance`）更新回 `web-search_temp_news` 對應的列，並將狀態更新為 `checked: 2-Categorized`。

4.  **GNews 新聞處理 - 重要新聞摘要 (Step 3):**
    *   從 `web-search_temp_news` 讀取 `checked: 2-Categorized` 的新聞。
    *   過濾出 `importance` 分數大於 6 的新聞 (`Filter3`)。 「可自行設定」。
    *   **迴圈處理每個重要新聞:**
        *   使用 **Jina AI Reader API** (`HTTP - jina (get markdown)1`) 獲取新聞網頁的完整 Markdown 內容。
        *   使用 **Google Gemini AI Agent (Summerization (take away))** 進行摘要。
            *   輸入：新聞標題、描述、Jina 獲取的完整 Markdown 內容。
            *   任務：生成包含 "Takeaway" 和 "Detailed Summary" 的 Markdown 格式摘要。
            *   輸出：Markdown 摘要。
        *   解析 AI 輸出的 Markdown 摘要。
        *   整理欄位，包含原始分類、分數和新生成的摘要。
        *   將最終結果寫入 Google Sheet (`news_database` -> `news_database`)，標記 `status: 2 - Summarized`。
        *   更新 `web-search_temp_news` 中對應新聞的狀態為 `checked: 3-Final-Checked`。

5.  **最終處理與通知 (Final Step):**
    *   從 `news_database` 讀取所有已處理 (Summarized) 的文章。
    *   過濾出 `importance` >= 7 且 `relevance_score` >= 7 且發布日期在上次檢查時間之後的文章 (`Importance mail`)。
    *   將這些篩選出的重要文章附加到 Google Sheet (`news_database` -> `articles_to_publish`)。
    *   **迴圈處理每個待發布文章:**
        *   使用 **Google Gemini AI Agent (summary in zh-tw)** 將英文摘要翻譯成台灣慣用的繁體中文。
            *   輸入：英文 Markdown 摘要。
            *   任務：翻譯成繁中，保留 Markdown 格式，並在開頭加上一句話摘要。
            *   輸出：繁體中文 Markdown 摘要。
        *   將翻譯後的摘要更新回 `articles_to_publish` 表格的 `summary_tw` 欄位。
    *   發送 Email 通知使用者 (`Send email to remind me`)，提醒檢查 `articles_to_publish` 表格。
    *   更新 RSS 流程的上次檢查時間戳檔案 (`/tmp/lastCheckFile`)。

## 前置需求

*   **n8n 環境:** 建議使用自架 n8n 環境。
*   **API 憑證:**
    *   **Google Sheets API:** 需要啟用 Google Sheets API 並取得 OAuth2 憑證，用於讀寫 Google Sheets。
    *   **GNews API:** 需要註冊 GNews 並取得 API Key。 [官方文件](https://gnews.io/docs/v4#search-endpoint) Free API quota: - 100 request per day
    *   **Google Gemini API:** 需要擁有 Google Cloud Platform 帳號並啟用  API (Gemini 模型隸屬於此)，取得 API 金鑰。
    *   **Gmail API:** 需要啟用 Gmail API 並取得 OAuth2 憑證，用於讀取特定標籤的郵件。
    *   **Jina AI Reader API:** (免費額度) 用於獲取網頁 Markdown 內容。
*   **自架服務 (若使用):**
    *   **FreshRSS:** 如果使用 RSS 來源，需要自架 FreshRSS 服務，並確保 n8n 可以訪問其 API 端點 (`http://host.docker.internal:8080/i` 在此範例中)。
*   **Google Sheets 設定:**
    *   需要建立一個 Google Sheet 文件 (在此範例中 ID 為 `1zlrHwN8lU0VjVzM37yDzikZqFMYxnHDui-3sINUDaRw`)，包含以下工作表 (Sheet)：
        *   `web-search_temp_news`: 暫存 GNews API 獲取的新聞及分類結果。欄位包含 `title`, `description`, `content`, `pub_Date`, `url`, `checked`, `category`, `relevance_score`, `importance`。
        *   `news_database`: 儲存來自 RSS 和 Gmail 的處理結果，以及 GNews 的最終摘要結果。欄位包含 `reference_id`, `title`, `topic`, `pub_date`, `summary`, `url`, `status`, `relevance_score`, `importance`。
        *   `articles_to_publish`: 儲存篩選出的重要文章及其翻譯摘要。欄位包含 `reference_id`, `title`, `topic`, `pub_date`, `summary`, `summary_tw`, `Action`, `url`, `source`, `relevance_score`, `importance`。
    *   需要另一個 Google Sheet 文件 (在此範例中 ID 為 `1_31aY67d_dDU2AwV6hlJ95NgnbTsYHboKRTL2uBRyOk`)，包含以下工作表：
        *   `Web Search Keywords`: 存放 GNews API 搜尋用的關鍵字，至少包含 `Keywords` 欄位。
    *   本專案使用的Google Sheet模板，可見於此處[下載]()。
    
*   **Gmail 設定:**
    *   需要在 Gmail 中設定篩選器，將特定郵件加上標籤 (在此範例中 Label ID 為 `Label_8982256647532788657`)。
*   **檔案儲存:**
    *   n8n 需要有權限讀寫 `/tmp/lastCheckFile` 文件，用於儲存 RSS 流程的上次檢查時間。

## 如何使用

1.  **設定憑證:** 在 n8n 中設定好 Google Sheets, GNews, Google Gemini, Gmail 的 API 憑證。
2.  **設定 Google Sheets 節點:** 將工作流程中所有 Google Sheets 節點的 `Document ID` 和 `Sheet Name` 更新為您自己的 Google Sheets 文件 ID 和工作表名稱/ID。
3.  **設定 GNews API 節點:** 將 `GNews API2` 和 `GNews API3` 節點中的 `apikey` 更新為您自己的 GNews API Key。
4.  **設定 RSS 節點:** 如果使用 FreshRSS，請將 `RSS database1` 節點的 `url` 和 `token` 更新為您自己的 FreshRSS 服務位址和 API Token。
5.  **設定 Gmail 節點:** 將 `Gmail` 節點中的 `Label IDs` 更新為您要讀取的 Gmail 標籤 ID。將 `Send email to remind me` 節點的收件人 (`sendTo`) 更新為您的 Email 地址。
6.  **檢查檔案路徑:** 確保 `Read/Write Files from Disk`, `Extract from File`, `Convert to File1`, `Read/Write Files from Disk3` 節點使用的檔案路徑 (`/tmp/lastCheckFile`) 在您的 n8n 環境中是可讀寫的。
7.  **啟用工作流程:** 啟用此 n8n 工作流程。
8.  **觸發:** 工作流程將根據 `Schedule Trigger` 節點設定的排程自動執行。首次執行可能需要較長時間處理歷史資料。

工作流程執行完成後，相關資訊將被分類、摘要並儲存到指定的 Google Sheets 工作表中，重要文章會被篩選出來並翻譯摘要，最後會發送 Email 通知。
