# Local AI Automation Package

local AI Automation Package 是一個開放的 Docker Compose 模板，可以快速啟動一個功能齊全的本地 AI 和低代碼開發環境，其中包括 Open WebUI、qdrant、n8n、Ollama 和 PostgreSQL。

此docker compose內容，主要folk from coleam00 version。
並將持續新增實用項目，包含：
1. FreshRSS，作為接收外部訊息來源。
2. Markitdown MCP severvice，作為將資源轉換為 Markdown 格式的服務，通過 n8n 工作流程與 AI Agent 集成，提供強大的內容處理能力。

[原始 Local AI Starter Kit](https://github.com/n8n-io/self-hosted-ai-starter-kit)

[Cole's version](https://github.com/coleam00/ai-agents-masterclass/tree/main/local-ai-packaged)

建議可以參考Cole's 的[安裝教學影片](https://www.youtube.com/watch?v=V_0dNE-H2gw)，不過如果你也需要FreshRSS，就使用這邊的FreshRSS。

![n8n.io - 螢幕截圖](https://raw.githubusercontent.com/n8n-io/self-hosted-ai-starter-kit/main/assets/n8n-demo.gif)


### 包含內容

✅ [**Self-hosted n8n**](https://n8n.io/) - 具有超過 400 個整合和高級 AI 組件的Low-Code平台

✅ [**Ollama**](https://ollama.com/) - 跨平台 LLM 平台，用於安裝和運行最新的本地 LLM

✅ [**Open WebUI**](https://openwebui.com/) - 類似 ChatGPT 的介面，可與您的本地模型和 N8N 代理私下互動

✅ [**Flowise**](https://flowiseai.com/) - 無/低代碼 AI 代理構建器，與 n8n 非常搭配。

✅ [**Qdrant**](https://qdrant.tech/) - 具有全面 API 的開源，非常實用的向量儲存軟體。

✅ [**PostgreSQL**](https://www.postgresql.org/) - 數據工程領域的主力，安全地處理大量數據 (用於存取n8n資料)。

✅ [**FreshRSS**](https://freshrss.org/index.html) -  免費、開源的 RSS 聚合器，蒐集各式具RSS網站內容。

## 2025.04.23 更新:新增 Markitdown MCP 服務

✅ [**Markitdown MCP**](https://github.com/markitdown/markitdown-mcp) - 一個用於將資源轉換為 Markdown 格式的服務，通過 n8n 工作流程與 AI Agent 集成，提供強大的內容處理能力。Markitdown MCP 服務通過 SSE (Server-Sent Events) 端點與 n8n 進行通信，允許 AI Agent 使用其工具來處理內容轉換任務。


## 安裝

雖然這邊是使用docker指令裝，但對於新手而言，非常建議各位下載[docker desktop](https://www.docker.com/products/docker-desktop/)，將docker服務呈現於桌面，比較易懂。

> 貼心提宿：如果「顯卡」不夠強的話，建議可以直接不裝Ollama，否則會跑到天荒底老，使用者體驗大幅降低。


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
git clone https://github.com/StevenWang82/local-ai-automation-pakage.git
cd local-ai-packaged
docker compose up 
```

在您按照下面的快速入門設定進行操作後，請使用 `http://host.docker.internal:11434/` 作為主機來更改 Ollama 憑證。

### 適用於其他所有人

```
git clone https://github.com/coleam00/ai-agents-masterclass.git
cd local-ai-packaged
docker compose --profile cpu up
```

## ⚡️ 快速入門設定

自託管 AI 啟動器套件的主要組件是一個 Docker Compose 檔案，該檔案已預先配置了網路和磁碟，因此您不需要安裝太多其他內容。完成上述安裝步驟後，請按照以下步驟開始。

1. 在您的瀏覽器中打開 <http://localhost:5678/> 以設定 n8n，依照指示完成帳號註冊(該帳號只在你的本地端有用，與n8n線上產品無關)
2. 在您的瀏覽器中打開 <http://localhost:3000/> 以設定 Open WebUI。

要隨時打開 n8n，請在您的瀏覽器中訪問 <http://localhost:5678/>。
要隨時打開 Open WebUI，請訪問 <http://localhost:3000/>。

--- 


> [!NOTE]
> 此啟動器套件旨在幫助您開始使用自託管 AI
> 工作流程。雖然它並未針對生產環境進行完全優化，但它
> 結合了可以很好地協同工作的強大組件，以用於概念驗證
> 專案。您可以自訂它以滿足您的特定需求

## 「映像檔案/軟體軟體」更新/升級

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
