# Self-hosted AI starter kit (由 n8n 團隊提供)

**Self-hosted AI Starter Kit** 是一個開放的 Docker Compose 模板，可以快速啟動一個功能齊全的本地 AI 和低代碼開發環境，其中包括 Open WebUI，作為與您的 N8N 代理互動的介面。


以下是我參考Cole's version的版本，進行了一些改進。
Cole's version 新增 Open WebUI、Flowwise！
此板新增FlashRss，主要用於資料匯入。

[原始 Local AI Starter Kit](https://github.com/n8n-io/self-hosted-ai-starter-kit)
[Cole's version](https://github.com/coleam00/ai-agents-masterclass/tree/main/local-ai-packaged)

建議可以參考它的安裝教學！講得非常詳細。

![n8n.io - 螢幕截圖](https://raw.githubusercontent.com/n8n-io/self-hosted-ai-starter-kit/main/assets/n8n-demo.gif)


### 包含內容

✅ [**Self-hosted n8n**](https://n8n.io/) - 具有超過 400 個整合和高級 AI 組件的低代碼平台

✅ [**Ollama**](https://ollama.com/) - 跨平台 LLM 平台，用於安裝和運行最新的本地 LLM

✅ [**Open WebUI**](https://openwebui.com/) - 類似 ChatGPT 的介面，可與您的本地模型和 N8N 代理私下互動

✅ [**Flowise**](https://flowiseai.com/) - 無/低代碼 AI 代理構建器，與 n8n 非常搭配

✅ [**Qdrant**](https://qdrant.tech/) - 具有全面 API 的開源、高性能向量儲存

✅ [**PostgreSQL**](https://www.postgresql.org/) - 數據工程領域的主力，安全地處理大量數據。

✅ [**FreshRSS**](https://freshrss.org/index.html) -  免費、開源且自託管的 RSS 聚合器，蒐集各式具RSS網站內容。

## 安裝

### 適用於 Nvidia GPU 用戶

```
git clone https://github.com/coleam00/ai-agents-masterclass.git
cd ai-agents-masterclass/local-ai-packaged
docker compose --profile gpu-nvidia up
```

> [!NOTE]
> 如果您之前沒有將 Nvidia GPU 與 Docker 一起使用，請按照
> [Ollama Docker instructions](https://github.com/ollama/ollama/blob/main/docs/docker.md)。

### 適用於 Mac / Apple Silicon 用戶

如果您使用的是配備 M1 或更新處理器的 Mac，則很遺憾，您無法將 GPU 暴露給 Docker 實例。在這種情況下，有兩個選項：

1. 像下面的「適用於其他所有人」部分一樣，完全在 CPU 上運行啟動器套件
2. 在您的 Mac 上運行 Ollama 以獲得更快的推論，並從 n8n 實例連接到該推論

如果您想在 Mac 上運行 Ollama，請查看
[Ollama homepage](https://ollama.com/)
以獲取安裝說明，並按如下方式運行啟動器套件：

```
git clone https://github.com/coleam00/ai-agents-masterclass.git
cd ai-agents-masterclass/local-ai-packaged
docker compose up
```

在您按照下面的快速入門設定進行操作後，請使用 `http://host.docker.internal:11434/` 作為主機來更改 Ollama 憑證。

### 適用於其他所有人

```
git clone https://github.com/coleam00/ai-agents-masterclass.git
cd ai-agents-masterclass/local-ai-packaged
docker compose --profile cpu up
```

## ⚡️ 快速入門和使用

自託管 AI 啟動器套件的主要組件是一個 Docker Compose 檔案，該檔案已預先配置了網路和磁碟，因此您不需要安裝太多其他內容。完成上述安裝步驟後，請按照以下步驟開始。

1. 在您的瀏覽器中打開 <http://localhost:5678/> 以設定 n8n。您只需執行一次此操作。您不是在此設定中建立 n8n 帳戶，它只是您實例的本地帳戶！
2. 打開包含的工作流程：
   <http://localhost:5678/workflow/vTN9y2dLXqTiDfPT>
3. 為每個服務建立憑證：

   Ollama URL: http://ollama:11434

   Postgres: 使用來自 .env 的 DB、使用者名稱和密碼。主機是 postgres

   Qdrant URL: http://qdrant:6333 (API 金鑰可以是任何內容，因為它在本地運行)

   Google Drive: 按照 [this guide from n8n](https://docs.n8n.io/integrations/builtin/credentials/google/) 中的說明進行操作。
   不要對重新導向 URI 使用 localhost，只需使用您擁有的另一個網域即可，它仍然可以工作！
   或者，您可以設定 [local file triggers](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.localfiletrigger/)。
4. 選擇 **Test workflow** 以開始運行工作流程。
5. 如果這是您第一次運行工作流程，您可能需要等待
   直到 Ollama 完成下載 Llama3.1。您可以檢查 Docker
   控制台日誌以檢查進度。
6. 確保將工作流程切換為活動狀態，並複製「生產」Webhook URL！
7. 在您的瀏覽器中打開 <http://localhost:3000/> 以設定 Open WebUI。
您只需執行一次此操作。您不是在此設定中建立 Open WebUI 帳戶，它只是您實例的本地帳戶！
8. 轉到 Workspace -> Functions -> Add Function -> 給予名稱 + 描述，然後貼上
來自 `n8n_pipe.py` 的程式碼

   該函數也 [published here on Open WebUI's site](https://openwebui.com/f/coleam/n8n_pipe/)。

9. 點擊齒輪圖示，並將 n8n_url 設定為您在上一步中複製的 Webhook 的生產 URL。
10. 開啟該功能，現在它將在左上角的模型下拉選單中可用！

要隨時打開 n8n，請在您的瀏覽器中訪問 <http://localhost:5678/>。
要隨時打開 Open WebUI，請訪問 <http://localhost:3000/>。

透過您的 n8n 實例，您將可以訪問超過 400 個整合和一套基本和高級 AI 節點，例如
[AI Agent](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)、
[Text classifier](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.text-classifier/) 和
[Information Extractor](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.information-extractor/)
節點。為了保持所有內容都在本地，只需記住對您的
語言模型使用 Ollama 節點，並使用 Qdrant 作為您的向量儲存。

> [!NOTE]
> 此啟動器套件旨在幫助您開始使用自託管 AI
> 工作流程。雖然它並未針對生產環境進行完全優化，但它
> 結合了可以很好地協同工作的強大組件，以用於概念驗證
> 專案。您可以自訂它以滿足您的特定需求

## 映像檔案更新/升級

### 適用於 Nvidia GPU 用戶

```
docker compose --profile gpu-nvidia pull
docker compose create && docker compose --profile gpu-nvidia up
```

### 適用於 Mac / Apple Silicon 用戶

```
docker compose pull
docker compose create && docker compose up
```

### 適用於其他所有人

```
docker compose --profile cpu pull
docker compose create && docker compose --profile cpu up
```

## 👓 推薦閱讀

n8n 包含大量有用的內容，可讓您快速開始使用其 AI 概念
和節點。如果您遇到問題，請轉到 [support](#support)。

- [AI agents for developers: from theory to practice with n8n](https://blog.n8n.io/ai-agents/)
- [Tutorial: Build an AI workflow in n8n](https://docs.n8n.io/advanced-ai/intro-tutorial/)
- [Langchain Concepts in n8n](https://docs.n8n.io/advanced-ai/langchain/langchain-n8n/)
- [Demonstration of key differences between agents and chains](https://docs.n8n.io/advanced-ai/examples/agent-chain-comparison/)
- [What are vector databases?](https://docs.n8n.io/advanced-ai/examples/understand-vector-databases/)
