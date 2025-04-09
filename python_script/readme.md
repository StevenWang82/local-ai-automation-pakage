# n8n YouTube 影片資訊與字幕擷取

此存儲庫包含兩個專為 n8n 工作流程設計的 Python 腳本，用於從 YouTube 影片中擷取資訊與字幕。這些腳本可整合進您的 n8n 流程中，自動化影片分析、內容創作等任務，協助您強化 n8n 工作流程，發揮 YouTube 數據的強大效用。

## 腳本總覽

### 1. `yt_json_download.py` >> YouTube_Learning_Note_Agents

此腳本可根據 YouTube 影片網址下載影片資訊與字幕。它利用 `yt-dlp` 函式庫，實現穩定的影片資訊擷取與字幕處理。

**主要功能：**

* **下載字幕：** 自動下載指定 YouTube 影片的可用字幕，優先順序為腳本中設定的語言（預設：繁體中文 zh-Hant、zh-TW，簡體中文 zh-CN、zh，英文 en，日文 ja，韓文 ko，泰文 th，越南文 vi）。若無正式字幕，則嘗試下載自動產生字幕。
* **擷取影片中繼資料：** 取得影片標題、描述、章節（若有）及網址。
* **清理與標準化字幕：** 移除多餘的字幕檔案，優先保留英文字幕，並將選定的字幕重新命名為 `subtitle.vtt`，方便存取。
* **錯誤處理：** 具備完善的錯誤處理機制，若下載或處理過程中發生問題，會透過 `stderr` 提供詳細訊息。即使出錯，也會回傳有效的 JSON 物件，確保在 n8n 中行為可預期。
* **JSON 輸出：** 將所有擷取的資料（包含字幕檔案路徑）以 JSON 格式輸出，並列印至 `stdout`，方便整合進 n8n 流程。
* **清空下載資料夾：** 每次執行前會清空下載資料夾，避免檔案衝突，確保只處理最新字幕。
* **自訂日誌紀錄器：** 使用自訂 logger，將警告與錯誤導向 `stderr`，方便 n8n 偵錯。
* **命令列參數：** 透過命令列參數接收 YouTube 影片網址。

**在 n8n 中的使用方式：**

1. **安裝 `yt-dlp`：** 確認您的 n8n 環境已安裝 `yt-dlp`，可使用 `pip install yt-dlp` 進行安裝。
2. **建立 n8n 的「執行命令」節點：** 在 n8n 工作流程中新增「Execute Command」節點。
3. **設定命令：**
   * **命令：** 指定 `yt_json_download.py` 腳本的路徑，並附上 YouTube 影片網址作為參數。例如：`python /path/to/yt_json_download.py https://www.youtube.com/watch?v=YOUR_VIDEO_ID`，請將 `/path/to/yt_json_download.py` 替換為實際腳本路徑。
   * **輸出設定：** 設定捕捉 `stdout` 與 `stderr`。
4. **解析 JSON 輸出：** 將「Function」節點連接至「Execute Command」節點，在 Function 節點中使用 `JSON.parse($input.all()[0].json)` 解析 `stdout` 中的 JSON 輸出，取得影片資訊。如有需要，也可處理 `stderr` 中的錯誤訊息。
5. **存取影片資訊：** 解析後的 JSON 物件中，即可取得影片標題、描述、章節與字幕檔案路徑，供後續流程使用。

### 2. `vtt_to_json.py` >> YouTube_Learning_Note_Agents

此腳本將 VTT（WebVTT）字幕檔轉換為 JSON 格式。支援解析簡單與複雜的 VTT 格式，並移除重複字幕，輸出更乾淨的結果。

**主要功能：**

* **VTT 解析：** 解析 VTT 字幕檔，擷取時間戳與字幕文字。
* **支援複雜 VTT 格式：** 處理含有內嵌時間戳與標籤（如 `<c>`）的複雜 VTT 格式。
* **去除重複字幕：** 移除連續重複的字幕內容，避免冗餘。
* **時間戳轉換：** 將 HH:MM:SS.毫秒 格式的時間戳轉換為秒數（浮點數）。
* **錯誤處理：** 若找不到 VTT 檔案或解析失敗，會將錯誤訊息輸出至 `stderr`，並在失敗時回傳 None。
* **JSON 輸出：** 將字幕內容（含每段字幕的起始與結束時間）以 JSON 格式輸出，並列印至 `stdout`。
* **自動刪除：** 成功轉換為 JSON 後，自動刪除原始 VTT 檔案。如有需要，可調整此行為。
