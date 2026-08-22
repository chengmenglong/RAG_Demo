# AI 私有知识库系统：架构冻结与 ADR

> 文档状态：Frozen for MVP v1
> 适用范围：当前仓库第一版可交付 MVP
> 修改规则：实现若要偏离本文件中的“必须”决策，应先修改本文并记录原因；不得在代码中静默改变架构。

## 1. 架构目标

本项目交付一个**单用户、单机优先、可通过 Docker Compose 演示**的私有知识库系统，必须真正完成以下闭环：

```text
创建知识库
→ 上传 PDF / DOCX / TXT / Markdown
→ 校验、解析、清洗、Chunk
→ Embedding
→ 向量写入与检索
→ LLM 基于检索上下文回答
→ 返回并持久化可追溯 Citation
```

MVP 既要支持没有真实 API Key 的 Demo 模式，也要能通过配置接入 OpenAI-compatible API 或 Ollama。代码应为后续客户项目保留清晰替换点，但第一版不提前实现多租户、分布式任务、微服务或复杂检索。

## 2. 范围边界

### 2.1 MVP 必须实现

- React Web UI：Dashboard、知识库、文档、Chat、Settings。
- 知识库 CRUD、文档上传/状态/删除/重新处理。
- PDF、DOCX、TXT、Markdown 文本提取。
- 可配置的字符级 `chunk_size` 与 `chunk_overlap`。
- Demo、OpenAI-compatible、Ollama Provider。
- Chroma 持久化向量检索。
- 会话历史、回答、引用快照持久化。
- SQLite 默认数据库和 Alembic 迁移。
- 本地 PowerShell 开发流程与 `docker compose up --build`。
- 后端、前端和核心闭环测试。

### 2.2 明确不在 MVP 中

- 注册、登录、RBAC、多租户。
- OCR、表格理解、图片理解、音视频解析。
- Redis、Celery/Dramatiq、独立 Worker。
- SSE/WebSocket 流式生成。
- Reranker、混合检索、知识图谱、联网搜索、Agent、MCP。
- S3/OSS 等对象存储。
- 横向扩容、多 Uvicorn worker、高可用部署。
- 面向公网的安全承诺。

这些能力只能作为后续替换或扩展点，不得用空接口冒充已实现功能。

## 3. 总体架构

```text
┌───────────────────────────────────────────────────────────────┐
│ Browser                                                       │
│ React + TypeScript + Vite + Ant Design                       │
└──────────────────────────────┬────────────────────────────────┘
                               │ JSON / multipart/form-data
                               ▼
┌───────────────────────────────────────────────────────────────┐
│ FastAPI                                                       │
│ API Router → Service → Repository / Pipeline                  │
│                                                               │
│ ┌──────────────┐  ┌─────────────────┐  ┌───────────────────┐ │
│ │ Domain CRUD  │  │ Document        │  │ RAG / Chat        │ │
│ │ Dashboard    │  │ Processing      │  │ Citation Resolver │ │
│ └──────┬───────┘  └───────┬─────────┘  └─────────┬─────────┘ │
│        │                  │                      │            │
│        ▼                  ▼                      ▼            │
│ SQLAlchemy         Local File Storage     Provider Abstraction│
│ + Alembic          Parser / Chunker       LLM / Embedding     │
└────────┬───────────────────┬──────────────────────┬────────────┘
         │                   │                      │
         ▼                   ▼                      ▼
      SQLite             data/uploads       Demo / OpenAI / Ollama
   PostgreSQL-ready          │
                             ▼
                    Chroma PersistentClient
```

开发环境由 Vite 在 `5173` 端口提供前端、FastAPI 在 `8000` 端口提供 API；Vite 将 `/api` 代理到后端。Docker 环境由 Nginx 提供静态前端并反向代理 `/api`，默认对外端口为 `3000`。

## 4. 技术栈冻结

### 4.1 前端

- React + TypeScript + Vite。
- Ant Design + `@ant-design/icons`：组件、表单、Modal、Drawer、Table、Toast、Skeleton、Empty、Result。
- React Router：页面路由。
- TanStack Query：服务端数据缓存、失效、轮询。
- Axios：API 请求和上传进度。
- React Dropzone：拖拽上传。
- React Markdown + remark-gfm：回答渲染；禁止启用原始 HTML。
- Vitest + React Testing Library + MSW：前端测试。

前端不引入 Redux/Zustand。MVP 的全局业务状态由 URL、TanStack Query 和少量 React Context 管理。

### 4.2 后端

- Python 3.12 作为 Docker、发布和依赖锁定基线；当前开发机的 Python 3.13 必须实际验证兼容性，失败时记录环境阻塞，不得静默换依赖。
- FastAPI + Pydantic Settings。
- SQLAlchemy 2.x **同步模式**。
- Alembic 数据库迁移。
- SQLite 默认，保留 PostgreSQL URL 与通用模型兼容性。
- Chroma `PersistentClient`，由本应用提供预计算 embedding。
- `pypdf`、`python-docx`、`charset-normalizer`。
- OpenAI Python SDK 用于 OpenAI-compatible API；`httpx` 用于 Ollama。
- Tenacity 仅重试超时、429 和明确的 5xx；认证失败、请求校验失败不重试。
- 标准 logging + JSON formatter，配合 request ID 和结构化字段。

后端不引入 LangChain、LlamaIndex。Provider、Chunk、Prompt、Retrieval 与 Citation 必须保持可读、可单测。

### 4.3 数据与存储

- 关系数据：`data/app.db`。
- 上传原文件：`data/uploads/{knowledge_base_id}/{document_id}{extension}`。
- 上传临时文件：同目录下 `{document_id}{extension}.part`，验证成功后原子改名。
- Chroma：`data/chroma/`。
- Docker：上述目录统一放入一个 named volume。
- `data/`、真实 `.env`、临时文件不得提交到 Git。

## 5. 后端分层与依赖方向

依赖只能由外向内：

```text
API → Service → Repository / Domain Pipeline → Infrastructure Adapter
```

- `api`：HTTP 参数、状态码、依赖注入、响应 schema；不放业务流程。
- `services`：用例编排和事务边界。
- `repositories`：SQLAlchemy 查询和持久化，不调用 LLM 或解析器。
- `document_processing`：验证、提取、清洗、Chunk、处理状态推进。
- `rag`：检索、Prompt、回答、引用解析。
- `providers`：Embedding/LLM 协议、工厂和厂商适配器。
- `vectorstores`：向量库协议和 Chroma 适配器。
- `storage`：文件存储协议和本地实现。
- `models`：SQLAlchemy ORM。
- `schemas`：Pydantic 输入输出。
- `config`：Pydantic Settings 与日志配置。
- `core`：统一错误、中间件和应用级装配。
- `utils`：无业务状态的文件名、时间等小型工具；不得成为杂物仓库。

API router 不得直接创建 OpenAI/Ollama/Chroma client，也不得直接读写文件。

## 6. 推荐目录

```text
RAG_Demo/
├─ README.md
├─ .env.example
├─ .gitignore
├─ .gitattributes
├─ docker-compose.yml
├─ docs/implementation/
├─ scripts/
│  ├─ bootstrap.ps1
│  ├─ start-dev.ps1
│  ├─ stop-dev.ps1
│  ├─ test-backend.ps1
│  ├─ test-frontend.ps1
│  ├─ seed-demo.ps1
│  ├─ smoke-core.ps1
│  ├─ smoke-provider.ps1
│  └─ acceptance.ps1
├─ backend/
│  ├─ pyproject.toml
│  ├─ Dockerfile
│  ├─ alembic.ini
│  ├─ alembic/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ api/deps.py
│  │  ├─ api/v1/
│  │  │  ├─ router.py
│  │  │  ├─ health.py
│  │  │  ├─ dashboard.py
│  │  │  ├─ knowledge_bases.py
│  │  │  ├─ documents.py
│  │  │  ├─ chat.py
│  │  │  └─ settings.py
│  │  ├─ config/
│  │  │  ├─ settings.py
│  │  │  └─ logging.py
│  │  ├─ core/
│  │  │  ├─ errors.py
│  │  │  └─ middleware.py
│  │  ├─ db/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ repositories/
│  │  ├─ services/
│  │  ├─ storage/
│  │  ├─ document_processing/
│  │  ├─ providers/
│  │  ├─ vectorstores/
│  │  ├─ rag/
│  │  ├─ utils/
│  │  └─ scripts/seed_demo.py
│  └─ tests/
│     ├─ unit/
│     ├─ integration/
│     └─ fixtures/
└─ frontend/
   ├─ package.json
   ├─ package-lock.json
   ├─ Dockerfile
   ├─ nginx.conf
   ├─ vite.config.ts
   └─ src/
      ├─ app/
      ├─ components/
      ├─ hooks/
      ├─ layouts/
      ├─ pages/
      ├─ services/
      ├─ types/
      └─ styles/
```

只在阶段任务实际使用时创建模块，不要预先生成几十个空文件。

## 7. Provider 与 VectorStore 抽象

以下是语义契约，不要求逐字照抄类型名：

```python
class EmbeddingProvider(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...
    def describe_profile(self) -> EmbeddingProfile: ...

class LLMProvider(Protocol):
    def chat(
        self,
        messages: list[ProviderMessage],
        *,
        temperature: float,
        timeout_seconds: float,
    ) -> str: ...

class VectorStore(Protocol):
    def upsert(self, records: list[VectorRecord]) -> None: ...
    def search(self, query: VectorQuery) -> list[VectorHit]: ...
    def delete(self, vector_ids: list[str]) -> None: ...
```

### 7.1 Provider 实现

- `DemoEmbeddingProvider`：固定模型标识 `stable-hash-v1`，固定 384 维，使用稳定的 BLAKE2 字符/词 n-gram 哈希并 L2 归一化。禁止使用 Python 内置 `hash()`。
- `DemoLLMProvider`：只从检索片段抽取简短答案，并引用 `[S1]` 等来源；页面显示“演示模式”。它不宣称具有真实语义推理能力。
- `OpenAICompatibleEmbeddingProvider` 与 `OpenAICompatibleLLMProvider`：SDK `base_url` 可配置，密钥来自环境变量。
- `OllamaEmbeddingProvider`：调用 `/api/embed`。
- `OllamaLLMProvider`：调用 `/api/chat`，MVP 使用 `stream=false`。

Provider factory 只接受白名单标识：`demo`、`openai_compatible`、`ollama`。不做动态模块发现。

### 7.2 Embedding Profile

同一向量集合中的索引和查询必须使用完全相同的 embedding profile。Profile 至少包含：

- `provider`
- 规范化后的 `base_url`，Demo 为 `null`
- `model`
- `dimension`
- `normalization`，MVP 固定为 `l2`
- `profile_version`，MVP 固定为 `1`

`embedding_profile_hash` 是上述规范化 JSON 的 SHA-256，小写十六进制 64 字符。Base URL 禁止包含用户名、密码或敏感 query 参数。

知识库创建时 profile 为未绑定；第一次成功生成文档 embedding 时，根据实际向量维度原子绑定。绑定后：

- 上传、重新处理和查询都使用知识库快照，而不是当前全局 embedding 默认值。
- 不允许把不同 profile 的 Chunk 写入同一知识库。
- MVP 不提供在线 profile 迁移；用户应新建知识库并重新上传。不得悄悄以新模型查询旧向量。

### 7.3 Chroma 规则

- 使用 `PersistentClient`。
- 应用提供 `embeddings` 和 `query_embeddings`；不得让 Chroma 默认下载模型。
- Collection 名为 `emb_<profile_hash 前 16 位>`。
- 距离空间固定为 cosine。
- Vector ID 固定使用 Chunk UUID 字符串。
- metadata 至少包含 `knowledge_base_id`、`document_id`、`page_number`（有值时）和 `section`（有值时）。
- 检索必须用 `knowledge_base_id` 过滤，并在关系库中再次确认 Document 为 `ready`。
- cosine similarity 按 `1 - distance` 转换；对外 score 范围按 `[-1, 1]` 校验。

## 8. 文档处理架构

### 8.1 上传前校验

- 默认最大 25 MiB，以流式复制时累计字节为准，不能信任 `Content-Length`。
- 原文件名只用于显示；拒绝路径分隔符、控制字符、空名称和过长名称。
- 存储文件名由 Document UUID 和白名单扩展名生成。
- PDF 同时检查 `.pdf` 和 `%PDF-` 头。
- DOCX 检查 ZIP 结构及 `word/document.xml`，限制 ZIP 条目数、解压总大小和压缩比。
- TXT/Markdown 拒绝 NUL 和明显二进制内容。
- 空文件和不支持格式在创建后台任务前失败。
- 在同一知识库内按 SHA-256 去重。

### 8.2 Processing Pipeline

```text
queued
→ extracting
→ cleaning
→ chunking
→ embedding
→ indexing
→ completed
```

每个阶段更新 Document 的 `status`、`processing_stage` 和时间戳，并记录 `document_id`、`knowledge_base_id`、阶段、耗时和计数。日志不得记录全文、Prompt、API Key 或 Authorization header。

解析器输出统一的 `SourceSegment`：`text`、`page_number`、`section`、`segment_ordinal`。PDF 的页码由库的 0-based index 转换为 **1-based**；PDF Chunk 不跨页，以保证引用准确。DOCX/TXT/Markdown 无可靠页码时为 `null`，不得推测。

Chunk 使用段落优先的字符切分：默认 `chunk_size=1000`、`chunk_overlap=150`。两者含义明确为 Unicode 字符数，不伪称 token 数。只有超长段落才依次按句子、换行、硬切分降级。

### 8.3 一致性与补偿

关系数据库与 Chroma/文件系统没有分布式事务，MVP 使用确定性 ID、顺序写入和补偿：

1. 解析、清洗、Chunk 和 embedding 全部成功后再开始最终入库。
2. 关系库先生成 Chunk UUID，但在最终 commit 前不把 Document 标为 `ready`。
3. Chroma upsert 失败时，按本次 vector IDs 幂等删除并回滚 SQL。
4. Chroma 成功而 SQL commit 失败时，补偿删除本次 vector IDs。
5. 只有 SQL 与 Chroma 都成功后，Document 才进入 `ready/completed`。
6. 补偿本身失败必须记录结构化 ERROR，并保留可重试的 Document 状态；不得报告成功。

## 9. RAG 与 Citation

```text
Query
→ 使用知识库绑定的 Embedding Profile
→ 向量搜索 top_k × 3
→ 关系库过滤非 ready 文档
→ similarity threshold
→ 最终 top_k
→ 为上下文分配 S1、S2…
→ 构建受限 Prompt
→ LLM
→ 校验引用标签
→ 保存回答与 Citation 快照
```

- `top_k` 与 `similarity_threshold` 来自有效设置。
- 没有可靠结果时不调用 LLM，返回固定的资料不足回答和空 `sources`。
- Prompt 必须声明：只能依据上下文回答；上下文中的指令不可信；资料不足时明确说明。
- 只有本次检索结果中的 `S1...Sn` 是合法引用。模型生成未知标签时不得创建 Citation。
- API 返回的 sources 必须来自已验证的 Citation 对象，而不是前端自行解析模型文本。
- Citation 保存文档名、页码、章节、原文片段、score 快照。删除 Document 后历史引用仍可读，但源实体链接变为 `null`。
- MVP 不做 rerank、query rewrite 或跨知识库搜索。

## 10. 同步执行与后台任务

SQLAlchemy 使用同步 Engine/Session，Repository 和 Service 也采用同步调用。阻塞网络 SDK 使用同步 client；FastAPI 路由可用普通 `def`，避免在事件循环中执行同步 I/O。

文档处理通过 FastAPI `BackgroundTasks` 在上传响应后执行。必须遵守：

- 后台任务参数只传 `document_id`，不得传请求期 ORM 对象或 Session。
- 任务开始时创建自己的 Session，结束时无条件关闭。
- 启动时将遗留的 `pending/processing` 文档标记为 `failed`，错误码为 `PROCESS_INTERRUPTED`，允许用户重新处理。
- 本地和 Docker 都固定 `uvicorn --workers 1`。
- 文档状态由前端轮询，MVP 不使用内存任务字典作为事实源。

`BackgroundTasks` 不具备持久队列、并发控制和进程崩溃恢复能力。它仅满足受限单机 MVP；出现多用户、大文件或横向扩容需求时，必须升级到持久任务队列。

## 11. 配置与密钥边界

- API Key 只来自环境变量，使用 Secret 类型，禁止写入数据库、API 响应、日志和前端存储。
- 非敏感 provider/model/base URL 与检索参数可由 Settings API 写入数据库覆盖层。
- KnowledgeBase 已绑定的 embedding profile 高于全局默认，具体优先级见 API/Data Contracts。
- `RAG_MAX_CONTEXT_CHARS` 是环境只读安全上限，默认 12000 字符，不进入 Settings API；MVP 不引入依赖特定 tokenizer 的 Token 预算。
- `.env.example` 只包含空值或 Demo 默认，镜像不得复制真实 `.env`。
- Base URL 必须是 `http/https`，拒绝 URL 内嵌凭据。
- CORS 只允许配置的前端 origin；Docker 同源反代时不需要宽泛 CORS。

## 12. 日志、错误和安全

每个请求生成或接收合法的 `X-Request-ID`，响应回写该 header。结构化日志至少包含：

- `timestamp`、`level`、`event`、`request_id`
- `knowledge_base_id`、`document_id`、`session_id`（适用时）
- `stage`、`duration_ms`、`count`（适用时）
- 异常类型和经过清洗的消息

安全基线：

- 严格文件类型、大小、压缩包和路径校验。
- Pydantic 输入长度与数值范围校验。
- ORM 参数绑定，禁止拼接 SQL。
- Provider 设置连接/读取总超时。
- Markdown 前端不渲染 raw HTML；引用片段按纯文本显示。
- 错误响应不返回 traceback、内部路径、密钥或 Provider 原始敏感响应。
- 单用户 MVP 默认只供本机或受控内网演示，不能直接暴露公网。

## 13. Windows 与 Docker 约束

- 本地文档必须提供 PowerShell 命令，不得要求 Make 或 Bash 才能开发。
- 所有路径使用 `pathlib.Path`，默认使用相对 `data/`，避免 Windows 盘符转义。
- `.gitattributes` 强制 shell 脚本 LF。
- SQLite 开启 foreign keys、WAL、busy timeout；连接配置 `check_same_thread=False`。
- Docker Compose 只需 `frontend` 与 `backend`；SQLite、uploads、Chroma 共用持久 volume。
- Nginx 设置与后端一致的上传上限并将 `/api` 代理到 backend。
- 本地 Ollama 默认地址为 `http://localhost:11434`；容器访问宿主 Ollama 使用 `http://host.docker.internal:11434`。
- Docker 和本地都只能运行一个后端 worker，避免 SQLite/embedded Chroma 多写者问题。
- 单 worker 仍可能有多个请求线程；Chroma Adapter 必须用进程内可重入锁串行化 upsert/delete/collection mutation。该锁不提供跨进程保证，因此不得移除单 worker 限制。

## 14. 测试边界

- 单元测试：校验器、parser、chunker、Demo embedding 稳定性、Provider factory、阈值、Prompt、Citation 白名单。
- 集成测试：临时 SQLite + 临时 Chroma + 临时 uploads，覆盖 CRUD、上传、重复、异常格式、retry、delete、Demo RAG、设置脱敏。
- Provider 测试：Mock OpenAI/Ollama 的成功、认证失败、429、5xx、timeout；测试不得要求真实 Key。
- 前端测试：Dashboard、CRUD、上传状态、Chat、Citation Drawer、Settings 脱敏。
- 最终 smoke：创建知识库 → 上传 Markdown → 等待 ready → 提问 → 断言答案及 Citation 文档名/章节正确。

## 15. 架构决策记录（ADR）

### ADR-001：单体前后端分离，而非微服务

**决定**：React SPA + 一个 FastAPI 服务。
**原因**：第一版需要可运行闭环和低部署成本，不需要跨服务事务与运维。
**后果**：模块通过 Python 边界解耦，但共享一个进程和数据库。只有出现独立扩容或团队边界时才拆服务。

### ADR-002：SQLAlchemy 同步模式

**决定**：使用同步 Engine、Session、Repository 与 Provider client。
**原因**：SQLite、文件解析和多数 SDK 本身同步；可显著降低错误的 async/session 生命周期复杂度。
**后果**：单机 MVP 性能足够；后续如改异步必须整体迁移事务和测试，不允许在同一用例中混用同步/异步 Session。

### ADR-003：SQLite 默认，Alembic 保证 PostgreSQL 迁移路径

**决定**：本地/Compose 默认 SQLite，模型使用通用类型和显式外键。
**原因**：零额外服务，Windows 与客户演示启动简单。
**后果**：启用 WAL、busy timeout、单 worker；多用户并发是迁移 PostgreSQL 的触发条件。

### ADR-004：Chroma PersistentClient + VectorStore 抽象

**决定**：MVP 使用 embedded Chroma，业务层只依赖 `VectorStore`。
**原因**：本地持久化、metadata 过滤和低维护成本。
**后果**：仅支持单进程部署；生产扩容时可替换为服务化 Chroma、Qdrant 或 pgvector，而无需重写 RAG service。

### ADR-005：不使用 LangChain/LlamaIndex

**决定**：直接实现 parser、chunker、retriever、prompt、citation。
**原因**：MVP 流程有限，直接代码更易测试、审计和二次开发。
**后果**：需要自行维护少量 adapter，但避免框架升级和隐式 prompt/retrieval 行为。

### ADR-006：Provider 支持 Demo、OpenAI-compatible、Ollama

**决定**：LLM 与 Embedding 分别通过协议和工厂实例化。
**原因**：系统不能绑定单一厂商，同时必须无 Key 可演示。
**后果**：厂商异常映射为统一错误；Demo 结果必须明确标识，不得包装成真实模型能力。

### ADR-007：知识库绑定 Embedding Profile

**决定**：第一次成功索引时锁定 provider、base URL、model、dimension 和 hash。
**原因**：不同 embedding 模型或维度不可混用。
**后果**：全局设置变化不影响已绑定知识库；MVP 改模型需要新建知识库，不提供隐式迁移。

### ADR-008：BackgroundTasks 仅用于受限 MVP

**决定**：上传返回 `202`，同一 FastAPI 进程后台处理。
**原因**：满足状态 UI，又不引入 Redis/Worker。
**后果**：崩溃任务不自动恢复；启动时标失败并允许 retry。任务增长、并发和多 worker 是引入持久队列的触发条件。

### ADR-009：本地文件存储采用随机 ID

**决定**：文件路径由 KB/Document UUID 与白名单扩展组成。
**原因**：原文件名不可信，必须消除路径穿越和碰撞。
**后果**：下载/展示名来自数据库；未来对象存储只替换 `FileStorage` adapter。

### ADR-010：Citation 保存不可变快照

**决定**：回答时保存文档名、页码、章节、片段、score，而非只保存 Chunk 外键。
**原因**：文档删除或重新处理后仍需解释历史回答依据。
**后果**：快照会占用少量空间；删除文档后链接为空但证据文本仍保留。

### ADR-011：MVP 非流式 Chat

**决定**：Chat 请求同步等待完整回答。
**原因**：避免 SSE 的断线、部分消息、引用后处理和前端状态复杂度。
**后果**：必须有明确 loading、timeout 和 error UI；客户确需流式体验时再扩展独立端点。

### ADR-012：Settings 不管理密钥

**决定**：前端可编辑非敏感配置，API Key 仅通过环境变量注入。
**原因**：避免明文数据库、回显和浏览器泄漏。
**后果**：Settings 只显示 `*_api_key_configured` 布尔值；更新密钥需要修改运行环境并重启服务。

## 16. 已知风险与升级触发器

| 风险 | MVP 控制 | 明确升级触发器 |
|---|---|---|
| BackgroundTasks 不持久 | 中断标失败、幂等 retry | 多用户、并行任务、跨进程恢复 |
| SQLite/Chroma 单写者 | 单 worker、WAL、短事务 | 多实例或高并发 |
| SQL 与向量库非原子 | 确定性 ID、补偿删除、日志 | 大规模数据与严格一致性要求 |
| 扫描 PDF 无文本 | 明确 `NO_EXTRACTABLE_TEXT` | 客户要求扫描件时加入 OCR |
| Demo embedding 语义弱 | 显示 Demo badge | 真实评测/客户数据使用 Ollama 或远程模型 |
| 阈值跨模型不通用 | 每 KB 锁定 profile、阈值可配 | 建立标注集后做校准/rerank |
| 无认证和租户隔离 | 仅本机/受控内网 | 公网部署或多人使用前必须实现 Auth/RBAC |
| 恶意文档 | 大小、签名、ZIP、页数限制 | 不可信公网上传时加入沙箱/杀毒 |
| Citation 由模型漏写 | 后端 source 白名单与快照 | 需要严格句级归因时增加结构化输出/evaluator |

本架构的验收原则是：优先把单机核心闭环做真、做稳、做可验证；任何尚未实现的扩展能力必须如实标记为后续工作。
