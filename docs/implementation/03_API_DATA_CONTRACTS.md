# AI 私有知识库系统：API 与数据契约

> 文档状态：Frozen for MVP v1
> API 前缀：`/api/v1`
> 目标：让后端、前端、测试和后续模型依据同一组字段、状态与语义实现，不自行猜测。

## 1. 通用约定

### 1.1 数据格式

- 请求和响应默认使用 `application/json; charset=utf-8`。
- 文件上传使用 `multipart/form-data`，字段名固定为 `file`。
- ID 对外均为标准 UUID 字符串。
- 时间为 UTC RFC 3339 字符串，例如 `2026-08-22T01:23:45.123Z`。
- 所有名称在服务端去除首尾空白；纯空白按空值处理。
- 未知字段一律拒绝，Pydantic schema 使用 `extra="forbid"`。
- `null` 表示确实未知或不适用，不用空字符串代替。
- 列表接口默认 `page=1`、`page_size=20`，`page_size` 范围 `1..100`。
- 排序未特别说明时使用 `updated_at DESC, id DESC`，保证稳定。

### 1.2 页码与来源位置

- 所有 API、数据库与 UI 页码统一为 **1-based**。
- PDF parser 从底层 0-based index 提取后必须加 1。
- PDF Chunk 不跨页，`page_number` 必须是正整数。
- DOCX、TXT、Markdown 没有可靠页码时返回 `null`，不得估算页码。
- `section` 来自 Markdown 标题、DOCX Heading 或其他可验证结构；未知时为 `null`。
- UI 有页码时显示“第 N 页”，无页码时只显示章节或文档名。

### 1.3 分页响应

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

### 1.4 请求追踪

- 客户端可传 `X-Request-ID`；服务端只接受长度和字符合法的值，否则生成 UUID。
- 每个响应都返回 `X-Request-ID`。
- 错误体内的 `request_id` 与响应 header 相同。

## 2. 关系数据模型

实现使用 SQLAlchemy 2.x 和 Alembic。SQLite 默认，但字段和约束不得依赖 SQLite 专属 JSON 查询、触发器或隐式布尔行为。

### 2.1 `knowledge_bases`

| 字段 | 类型 | 约束与语义 |
|---|---|---|
| `id` | UUID | 主键 |
| `name` | varchar(120) | 非空；trim 后长度 `1..120` |
| `description` | text | 可空；最大 2000 字符 |
| `embedding_provider` | varchar(32) | 可空；绑定后为 `demo/openai_compatible/ollama` |
| `embedding_base_url` | varchar(500) | 可空；绑定 profile 的规范化快照，不得含 URL 凭据 |
| `embedding_model` | varchar(200) | 可空；绑定 profile 的模型快照 |
| `embedding_dimension` | integer | 可空；绑定后 `> 0` |
| `embedding_normalization` | varchar(16) | 可空；MVP 绑定后为 `l2` |
| `embedding_profile_version` | integer | 可空；MVP 绑定后为 `1` |
| `embedding_profile_hash` | char(64) | 可空；绑定 profile 规范化 JSON 的 SHA-256 |
| `created_at` | datetime UTC | 非空 |
| `updated_at` | datetime UTC | 非空 |

`embedding_profile_hash IS NULL` 表示知识库未绑定，可以使用当前有效 embedding 默认设置进行第一次索引。第一次 embedding 成功并确认实际维度后，在同一业务流程中写入全部 profile 字段。绑定后不得局部更新这些字段。

知识库名称在 MVP 中不要求全局唯一；UI 和 API 使用 UUID 定位。

### 2.2 `documents`

| 字段 | 类型 | 约束与语义 |
|---|---|---|
| `id` | UUID | 主键 |
| `knowledge_base_id` | UUID | FK → knowledge_bases；`ON DELETE CASCADE`；索引 |
| `original_filename` | varchar(255) | 安全清洗后的展示名，不作为存储路径 |
| `storage_key` | varchar(500) | 相对于上传根目录的内部键，不对前端返回绝对路径 |
| `extension` | varchar(16) | `.pdf/.docx/.txt/.md/.markdown` |
| `mime_type` | varchar(100) | 服务端校验后确定的逻辑 MIME |
| `size_bytes` | bigint | `> 0` |
| `sha256` | char(64) | 文件内容哈希；小写十六进制 |
| `status` | varchar(16) | `pending/processing/ready/failed` |
| `processing_stage` | varchar(24) | 见状态机 |
| `attempt_count` | integer | 默认 0；每次后台处理开始加 1 |
| `parser_name` | varchar(64) | 可空；成功选择 parser 后写入 |
| `chunk_size` | integer | 本次处理快照，范围 `200..4000` |
| `chunk_overlap` | integer | 本次处理快照，`0 <= overlap < chunk_size` |
| `embedding_profile_hash` | char(64) | 可空；成功索引后必须等于所属 KB profile |
| `extracted_char_count` | integer | 默认 0；`>= 0` |
| `chunk_count` | integer | 默认 0；`>= 0` |
| `last_error_code` | varchar(64) | 可空；机器可读错误码 |
| `last_error_message` | text | 可空；经过清洗的用户可读消息，最大 2000 字符 |
| `created_at` | datetime UTC | 非空 |
| `updated_at` | datetime UTC | 非空 |

唯一约束：`UNIQUE(knowledge_base_id, sha256)`。同一内容可进入不同知识库，同一知识库不可重复上传。文件名相同但内容不同可以上传。

### 2.3 `chunks`

| 字段 | 类型 | 约束与语义 |
|---|---|---|
| `id` | UUID | 主键；同时作为默认 vector ID |
| `knowledge_base_id` | UUID | FK → knowledge_bases；`ON DELETE CASCADE`；索引 |
| `document_id` | UUID | FK → documents；`ON DELETE CASCADE`；索引 |
| `ordinal` | integer | 文档内从 0 开始；`>= 0` |
| `content` | text | 非空，trim 后至少 1 字符 |
| `page_number` | integer | 可空；有值时 `>= 1` |
| `section` | varchar(500) | 可空 |
| `segment_ordinal` | integer | 原提取 segment 序号，从 0 开始 |
| `char_start` | integer | 相对原 segment 的 0-based 起点；`>= 0` |
| `char_end` | integer | 右开区间；`> char_start` |
| `character_count` | integer | 等于内容字符计数 |
| `vector_id` | varchar(64) | 非空；MVP 等于 `str(id)`；唯一 |
| `embedding_profile_hash` | char(64) | 非空；必须等于 KB profile |
| `created_at` | datetime UTC | 非空 |

唯一约束：`UNIQUE(document_id, ordinal)`。Chunk 不存 embedding 数组；向量只存 Chroma。

### 2.4 `chat_sessions`

| 字段 | 类型 | 约束与语义 |
|---|---|---|
| `id` | UUID | 主键 |
| `knowledge_base_id` | UUID | FK → knowledge_bases；`ON DELETE CASCADE`；索引 |
| `title` | varchar(120) | 非空；默认“新会话”，首个问题后可自动截取更新 |
| `created_at` | datetime UTC | 非空 |
| `updated_at` | datetime UTC | 非空 |

### 2.5 `chat_messages`

| 字段 | 类型 | 约束与语义 |
|---|---|---|
| `id` | UUID | 主键 |
| `session_id` | UUID | FK → chat_sessions；`ON DELETE CASCADE`；索引 |
| `role` | varchar(16) | `user/assistant` |
| `status` | varchar(16) | `pending/completed/failed` |
| `content` | text | completed 时非空；用户问题最大 4000 字符 |
| `provider` | varchar(32) | assistant 可空；实际 LLM provider 快照 |
| `model` | varchar(200) | assistant 可空；实际模型快照 |
| `error_code` | varchar(64) | 可空 |
| `error_message` | text | 可空；经过清洗 |
| `created_at` | datetime UTC | 非空 |

用户消息创建时直接为 `completed`。Assistant 消息先创建为 `pending`，成功后改为 `completed`，Provider 失败则改为 `failed`。

### 2.6 `message_citations`

| 字段 | 类型 | 约束与语义 |
|---|---|---|
| `id` | UUID | 主键 |
| `message_id` | UUID | FK → chat_messages；`ON DELETE CASCADE`；索引 |
| `chunk_id` | UUID | 可空；FK → chunks；`ON DELETE SET NULL` |
| `document_id` | UUID | 可空；FK → documents；`ON DELETE SET NULL` |
| `label` | varchar(16) | `S1`、`S2`…；对单条消息唯一 |
| `rank` | integer | 从 1 开始 |
| `score` | float | cosine similarity，范围 `[-1, 1]` |
| `document_name_snapshot` | varchar(255) | 非空 |
| `page_number_snapshot` | integer | 可空；有值时 `>= 1` |
| `section_snapshot` | varchar(500) | 可空 |
| `excerpt_snapshot` | text | 非空；最大 1200 字符 |
| `created_at` | datetime UTC | 非空 |

唯一约束：`UNIQUE(message_id, label)` 和 `UNIQUE(message_id, rank)`。删除或重新处理 Document 不改写历史快照。

### 2.7 `app_settings`

MVP 使用单例行 `id=1`，字段均可空；`null` 表示“没有数据库覆盖，继续使用环境变量或内置默认值”。

| 字段 | 类型 | 合法范围 |
|---|---|---|
| `id` | integer | 固定 1 |
| `llm_provider` | varchar(32) | `demo/openai_compatible/ollama` |
| `llm_base_url` | varchar(500) | 可空；`http/https`；不得含 URL 凭据 |
| `llm_model` | varchar(200) | 可空 |
| `temperature` | float | `0..2` |
| `embedding_provider` | varchar(32) | `demo/openai_compatible/ollama` |
| `embedding_base_url` | varchar(500) | 可空；同上 |
| `embedding_model` | varchar(200) | 可空 |
| `top_k` | integer | `1..20` |
| `similarity_threshold` | float | `-1..1` |
| `chunk_size` | integer | `200..4000` |
| `chunk_overlap` | integer | `0..1000` 且 `< chunk_size` |
| `updated_at` | datetime UTC | 非空 |

API Key 不属于此表。

## 3. Document 状态机

### 3.1 合法组合

| `status` | `processing_stage` | 含义 |
|---|---|---|
| `pending` | `queued` | 文件已安全保存，等待后台任务 |
| `processing` | `extracting` | 提取文本和来源元数据 |
| `processing` | `cleaning` | 文本清洗 |
| `processing` | `chunking` | 创建 Chunk 候选 |
| `processing` | `embedding` | 批量生成 embedding |
| `processing` | `indexing` | 写 SQL 与 Chroma |
| `ready` | `completed` | SQL 与 Chroma 均成功，可参与检索 |
| `failed` | `failed` | 处理失败，可重新处理或删除 |

禁止出现 `ready/indexing`、`failed/completed` 等组合。

### 3.2 转移

```text
上传成功 → pending/queued
pending/queued → processing/extracting
processing/extracting → cleaning → chunking → embedding → indexing
processing/indexing → ready/completed
pending 或 processing 任一阶段 → failed/failed
failed/failed → pending/queued（重新处理）
ready/completed → pending/queued（显式重新处理）
```

- `pending` 或 `processing` 时再次重处理返回 `409 DOCUMENT_BUSY`。
- 服务启动时遗留的 `pending/processing` 统一改为 `failed/failed`，错误码 `PROCESS_INTERRUPTED`。
- 进入新处理任务时 `attempt_count += 1`。
- 成功后清空 `last_error_code/last_error_message`。
- `ready` 是参与检索的唯一状态。

### 3.3 重新处理语义

`POST /documents/{document_id}/reprocess` 是**显式破坏性重建索引**：

1. 只允许 `failed` 或 `ready`。
2. 原始上传文件保留并重新读取。
3. 使用当前有效 `chunk_size/chunk_overlap` 快照。
4. 已绑定知识库仍使用其 embedding profile，不使用当前全局 embedding 默认值。
5. 任务开始后删除该文档旧 Chroma vectors 与 SQL chunks；历史 Citation 快照不变。
6. 重建期间文档不可参与检索。
7. 重建失败后状态为 `failed`，旧索引不自动恢复；用户可再次重处理。
8. 删除向量时“目标不存在”视为成功，使操作可幂等重试。

UI 对 `ready` 文档触发重新处理前必须提示“现有索引会被替换，失败后需再次处理”。

## 4. 配置优先级与生效范围

### 4.1 非敏感配置优先级

普通有效设置按以下顺序解析，前者优先：

```text
数据库 app_settings 非 null 覆盖
→ 环境变量
→ 内置安全默认值
```

Embedding 存在额外规则：

```text
已绑定 KnowledgeBase 的 embedding profile 快照
→（仅对未绑定 KB）普通有效 embedding 设置
```

因此：

- 修改 LLM provider/model/base URL/temperature：下一次 Chat 请求立即生效。
- 修改 top-k/threshold：下一次检索立即生效。
- 修改 chunk 参数：只影响新上传和显式重新处理，不改旧 Chunk。
- 修改 embedding 默认值：只影响未绑定知识库的第一次索引；已绑定 KB 不变。
- MVP 不提供修改已绑定 KB profile 的 API。

### 4.2 密钥

- `LLM_API_KEY` 与 `EMBEDDING_API_KEY` 只从环境变量读取。
- Demo 和本地 Ollama 可不配置 Key；OpenAI-compatible 必须配置对应 Key。
- API、数据库、日志和前端不得保存或回显 Key。
- Settings 响应只返回 `llm_api_key_configured`、`embedding_api_key_configured` 布尔值。
- Settings 更新体出现 `api_key`、`token`、`secret` 等未定义字段时返回 422，不静默忽略。

### 4.3 内置默认值

| 配置 | 默认值 |
|---|---|
| LLM provider | `demo` |
| LLM model | `extractive-demo-v1` |
| Embedding provider | `demo` |
| Embedding model | `stable-hash-v1` |
| Demo embedding dimension | `384` |
| Temperature | `0.2` |
| Top-K | `5` |
| Similarity threshold | `0.20` |
| Chunk size | `1000` 字符 |
| Chunk overlap | `150` 字符 |
| 最大上传 | `25 MiB` |
| RAG 最大上下文 | `12000` 字符；只读环境变量 `RAG_MAX_CONTEXT_CHARS`，不进入 Settings API |

### 4.4 环境变量名称契约

后续代码、`.env.example`、Docker Compose、README 和测试只能使用下表名称；重命名必须先更新本契约。`可被 DB 覆盖` 表示 `app_settings` 对应非 null 字段优先，环境变量只是默认层。

| 环境变量 | 类型/默认值 | 敏感 | 生效范围 |
|---|---|---|---|
| `APP_ENV` | `development`；可选 `development/test/production` | 否 | 只读基础配置 |
| `DATABASE_URL` | `sqlite:///./data/app.db` | 否 | 只读基础配置 |
| `DATA_DIR` | `./data` | 否 | 只读文件数据根 |
| `CHROMA_PATH` | `./data/chroma` | 否 | 只读向量持久目录 |
| `CORS_ORIGINS` | JSON 数组，开发默认 localhost/127.0.0.1:5173 | 否 | 只读安全配置 |
| `LOG_LEVEL` | `INFO` | 否 | 只读日志配置 |
| `LOG_JSON` | `true` | 否 | 只读日志配置 |
| `MAX_UPLOAD_MIB` | `25`，范围 `1..200` | 否 | 只读上传限制 |
| `DOCX_MAX_ENTRIES` | `2000` | 否 | 只读 ZIP 防护 |
| `DOCX_MAX_UNCOMPRESSED_MIB` | `100` | 否 | 只读 ZIP 防护 |
| `DOCX_MAX_COMPRESSION_RATIO` | `100` | 否 | 只读 ZIP 防护 |
| `LLM_PROVIDER` | `demo` | 否 | 可被 DB 覆盖 |
| `LLM_BASE_URL` | 空；选非 Demo 时按 Provider 校验 | 否 | 可被 DB 覆盖；拒绝 URL 凭据 |
| `LLM_MODEL` | `extractive-demo-v1` | 否 | 可被 DB 覆盖 |
| `LLM_API_KEY` | 空 | **是** | 仅环境；Secret 类型；永不序列化 |
| `LLM_TIMEOUT_SECONDS` | `60`，范围 `1..300` | 否 | 只读 Provider 策略 |
| `LLM_MAX_RETRIES` | `2`，范围 `0..5` | 否 | 只读 Provider 策略 |
| `EMBEDDING_PROVIDER` | `demo` | 否 | 可被 DB 覆盖 |
| `EMBEDDING_BASE_URL` | 空；选非 Demo 时按 Provider 校验 | 否 | 可被 DB 覆盖；拒绝 URL 凭据 |
| `EMBEDDING_MODEL` | `stable-hash-v1` | 否 | 可被 DB 覆盖 |
| `EMBEDDING_API_KEY` | 空 | **是** | 仅环境；Secret 类型；永不序列化 |
| `EMBEDDING_TIMEOUT_SECONDS` | `60`，范围 `1..300` | 否 | 只读 Provider 策略 |
| `EMBEDDING_MAX_RETRIES` | `2`，范围 `0..5` | 否 | 只读 Provider 策略 |
| `EMBEDDING_BATCH_SIZE` | `32`，范围 `1..256` | 否 | 只读处理策略 |
| `TEMPERATURE` | `0.2` | 否 | 可被 DB 覆盖 |
| `RAG_TOP_K` | `5` | 否 | 可被 DB 覆盖 |
| `RAG_SIMILARITY_THRESHOLD` | `0.20` | 否 | 可被 DB 覆盖 |
| `RAG_MAX_CONTEXT_CHARS` | `12000`，范围 `1000..100000` | 否 | 只读 Prompt 安全预算 |
| `CHAT_HISTORY_MESSAGES` | `6`，范围 `0..20` | 否 | 只读 Chat 策略 |
| `CHAT_HISTORY_MAX_CHARS` | `6000`，范围 `0..50000` | 否 | 只读 Chat 策略 |
| `CHUNK_SIZE` | `1000` | 否 | 可被 DB 覆盖 |
| `CHUNK_OVERLAP` | `150` | 否 | 可被 DB 覆盖 |

约束：

- `CORS_ORIGINS` 在 production 不得使用 `*`；Docker 同源反代不需要宽泛 CORS。
- `DATA_DIR`、`CHROMA_PATH` 和 SQLite 相对路径由配置层规范化；业务代码不得自行读取当前工作目录拼接。
- `CHROMA_PATH` 必须位于受控持久目录；Chroma 客户端显式关闭匿名遥测。
- 环境值与数据库值冲突时，必须按 4.1 节解析并在 `GET /settings.sources` 中说明来源。
- `.env.example` 只放 Demo 默认与空 Key；真实 `.env` 不进入 Git 或镜像上下文。

## 5. 公共响应对象

### 5.1 KnowledgeBaseSummary

```json
{
  "id": "4f7ea764-3f98-4cf3-919c-b0a5102cb483",
  "name": "产品资料",
  "description": "内部产品与交付文档",
  "document_count": 3,
  "ready_document_count": 2,
  "chunk_count": 84,
  "embedding_profile": {
    "bound": true,
    "provider": "demo",
    "base_url": null,
    "model": "stable-hash-v1",
    "dimension": 384,
    "profile_hash": "64-character-lowercase-sha256"
  },
  "created_at": "2026-08-22T01:00:00Z",
  "updated_at": "2026-08-22T01:20:00Z"
}
```

未绑定时 `bound=false`，其余 profile 字段为 `null`。

### 5.2 DocumentResource

```json
{
  "id": "a0a932ff-3d36-4bcf-aa11-f22210bfa7cd",
  "knowledge_base_id": "4f7ea764-3f98-4cf3-919c-b0a5102cb483",
  "original_filename": "project_report.pdf",
  "extension": ".pdf",
  "mime_type": "application/pdf",
  "size_bytes": 248331,
  "sha256": "64-character-lowercase-sha256",
  "status": "processing",
  "processing_stage": "embedding",
  "attempt_count": 1,
  "chunk_size": 1000,
  "chunk_overlap": 150,
  "extracted_char_count": 32781,
  "chunk_count": 0,
  "last_error": null,
  "retryable": false,
  "created_at": "2026-08-22T01:10:00Z",
  "updated_at": "2026-08-22T01:10:08Z"
}
```

失败时：

```json
"last_error": {
  "code": "NO_EXTRACTABLE_TEXT",
  "message": "文档中没有可提取的文本；扫描版 PDF 需要 OCR。"
}
```

`retryable` 为派生字段，仅 `failed/ready` 为 true。

### 5.3 ChatMessageResource

```json
{
  "id": "4ce97d87-6c10-4765-8fe9-b04e9067d621",
  "session_id": "62e26421-3ff9-4f97-8acd-5385c13d455d",
  "role": "assistant",
  "status": "completed",
  "content": "项目验收日期为 2026 年 7 月 31 日。[S1]",
  "provider": "demo",
  "model": "extractive-demo-v1",
  "error": null,
  "created_at": "2026-08-22T01:30:00Z"
}
```

### 5.4 CitationResource

```json
{
  "id": "c3dc0166-d002-42cc-9733-b1473fc921fb",
  "label": "S1",
  "rank": 1,
  "score": 0.8123,
  "chunk_id": "7a15cc5b-e04a-4e37-8f71-b5d8b878e436",
  "document_id": "a0a932ff-3d36-4bcf-aa11-f22210bfa7cd",
  "document_name": "project_report.pdf",
  "page_number": 12,
  "section": null,
  "excerpt": "……项目计划于 2026 年 7 月 31 日完成验收……",
  "source_available": true
}
```

Document 删除后 `chunk_id/document_id=null`、`source_available=false`，其余快照保持。

## 6. API 端点

### 6.1 Health

#### `GET /health`

不访问外部 LLM，返回进程和本地依赖状态。

```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": "ok",
  "vector_store": "ok",
  "demo_mode": true
}
```

数据库或 Chroma 不可用时返回 503，`status="degraded"`。

### 6.2 Dashboard

#### `GET /dashboard`

返回：

```json
{
  "knowledge_base_count": 2,
  "document_count": 8,
  "ready_document_count": 7,
  "chunk_count": 214,
  "recent_knowledge_bases": [],
  "recent_documents": []
}
```

`recent_*` 最多各 5 条，使用对应 Summary/Resource 的精简字段。

### 6.3 Knowledge Bases

#### `GET /knowledge-bases?page=1&page_size=20&query=`

- `query` 可空，最大 120 字符，对名称和描述做简单包含匹配。
- 返回 `KnowledgeBaseSummary` 分页列表。

#### `POST /knowledge-bases`

请求：

```json
{
  "name": "产品资料",
  "description": "内部产品与交付文档"
}
```

响应：`201 Created` + `KnowledgeBaseSummary`。创建时 embedding profile 未绑定。

#### `GET /knowledge-bases/{knowledge_base_id}`

响应：`200` + `KnowledgeBaseSummary`，可额外包含最近文档和最近会话各最多 5 条。

#### `PATCH /knowledge-bases/{knowledge_base_id}`

只允许：

```json
{
  "name": "新的名称",
  "description": "新的描述或 null"
}
```

至少提供一个字段。不得通过此接口修改 embedding profile。响应 `200`。

#### `DELETE /knowledge-bases/{knowledge_base_id}`

响应：`204 No Content`。删除该 KB 的原文件、Chroma vectors，并数据库级联删除 Documents、Chunks、Sessions、Messages 和 Citations。若任一文档为 `pending/processing`，返回 `409 DOCUMENT_BUSY`，details 给出 busy count；不得与后台任务竞态删除。详见删除语义。

### 6.4 Documents

#### `GET /knowledge-bases/{knowledge_base_id}/documents`

Query：

- `page/page_size`
- `status` 可选：`pending/processing/ready/failed`
- `query` 可选：按文件名包含匹配

返回 `DocumentResource` 分页列表。

#### `POST /knowledge-bases/{knowledge_base_id}/documents`

请求：`multipart/form-data`，单个 `file`。前端多文件拖拽时逐个调用，分别显示进度和结果。

成功响应：`202 Accepted` + `DocumentResource`，此时必须为 `pending/queued`。

同步上传阶段完成：

- 流式大小限制。
- 文件名、扩展名、签名/结构校验。
- SHA-256 计算与同 KB 去重。
- `.part` 原子改名。
- 创建 Document 和提交后台任务。

典型同步错误：413、415、422、409。解析失败不会把本次上传改成 HTTP 失败，而是在后续轮询中显示 Document `failed`。

#### `GET /documents/{document_id}`

响应 `200` + `DocumentResource`。前端对 `pending/processing` 每 2 秒轮询一次；离开页面后停止轮询。

#### `GET /documents/{document_id}/chunks?page=1&page_size=20`

仅供知识库详情和证据检查。返回：

```json
{
  "items": [
    {
      "id": "...",
      "ordinal": 0,
      "content": "……",
      "page_number": 1,
      "section": null,
      "character_count": 721
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

Document 不存在返回 404；非 `ready` 时允许返回当前已提交 Chunk，但正常 pipeline 在 ready 前不应存在可见的正式 Chunk。

#### `POST /documents/{document_id}/reprocess`

无请求体。成功响应 `202 Accepted` + 更新后的 `DocumentResource`（`pending/queued`）。

- `failed/ready` 可调用。
- `pending/processing` 返回 `409 DOCUMENT_BUSY`。
- 原文件缺失返回 `409 SOURCE_FILE_MISSING` 并保持原状态。
- 使用当前 chunk 设置、已绑定 KB embedding profile。
- 语义以第 3.3 节为准。

#### `DELETE /documents/{document_id}`

响应 `204 No Content`。删除 vectors、物理文件和 Document/Chunks；历史 MessageCitation 仅将外键置 null，快照不变。`processing` 状态返回 `409 DOCUMENT_BUSY`；允许删除 `pending/failed/ready`。删除 pending 后，已经排队的 BackgroundTask 再按 document ID 查询时若资源不存在，必须安全退出且不得重建文件或记录。

### 6.5 Chat Sessions 与消息

#### `GET /knowledge-bases/{knowledge_base_id}/chat-sessions`

分页返回：

```json
{
  "items": [
    {
      "id": "...",
      "knowledge_base_id": "...",
      "title": "项目验收日期",
      "message_count": 4,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

#### `POST /knowledge-bases/{knowledge_base_id}/chat-sessions`

请求：

```json
{
  "title": "新会话"
}
```

`title` 可省略。响应 `201 Created`。

#### `GET /chat-sessions/{session_id}`

响应包含 session、按 `created_at ASC, id ASC` 排序的消息，以及每条 assistant 消息的 citations。MVP 单次最多返回最近 200 条消息；超过时返回 `messages_truncated=true`。

#### `DELETE /chat-sessions/{session_id}`

响应 `204`，数据库级联删除 Messages 与 Citations；不影响知识库文档。

#### `POST /chat-sessions/{session_id}/messages`

请求：

```json
{
  "content": "项目验收日期是什么时候？"
}
```

约束：trim 后 `1..4000` 字符。MVP 非流式，响应等待检索与完整 LLM 结果。

成功响应：`201 Created`

```json
{
  "user_message": {
    "id": "...",
    "role": "user",
    "status": "completed",
    "content": "项目验收日期是什么时候？",
    "created_at": "..."
  },
  "assistant_message": {
    "id": "...",
    "role": "assistant",
    "status": "completed",
    "content": "项目验收日期为 2026 年 7 月 31 日。[S1]",
    "provider": "demo",
    "model": "extractive-demo-v1",
    "created_at": "..."
  },
  "sources": [
    {
      "id": "c3dc0166-d002-42cc-9733-b1473fc921fb",
      "label": "S1",
      "rank": 1,
      "score": 0.8123,
      "chunk_id": "7a15cc5b-e04a-4e37-8f71-b5d8b878e436",
      "document_id": "a0a932ff-3d36-4bcf-aa11-f22210bfa7cd",
      "document_name": "project_report.pdf",
      "page_number": 12,
      "section": null,
      "excerpt": "……项目计划于 2026 年 7 月 31 日完成验收……",
      "source_available": true
    }
  ],
  "retrieval": {
    "top_k": 5,
    "similarity_threshold": 0.2,
    "matched_count": 1,
    "insufficient_context": false
  },
  "demo_mode": true
}
```

`sources` 是 `CitationResource[]`。

无可靠检索结果仍返回 `201`：

- assistant content 固定说明“当前知识库中没有足够信息回答该问题”。
- `sources=[]`。
- `insufficient_context=true`。
- 不调用 LLM Provider。

Provider 调用失败：

- 用户消息保留为 completed。
- Assistant 消息保留为 failed，写入清洗后的错误。
- API 返回统一的 502 或 504；`details` 可含 `assistant_message_id` 供前端刷新，但不含 Provider 原始响应或密钥。

### 6.6 Settings

#### `GET /settings`

```json
{
  "values": {
    "llm_provider": "demo",
    "llm_base_url": null,
    "llm_model": "extractive-demo-v1",
    "temperature": 0.2,
    "embedding_provider": "demo",
    "embedding_base_url": null,
    "embedding_model": "stable-hash-v1",
    "top_k": 5,
    "similarity_threshold": 0.2,
    "chunk_size": 1000,
    "chunk_overlap": 150
  },
  "sources": {
    "llm_provider": "default",
    "llm_model": "default",
    "top_k": "environment",
    "chunk_size": "database"
  },
  "secrets": {
    "llm_api_key_configured": false,
    "embedding_api_key_configured": false
  },
  "effects": {
    "embedding_changes_apply_to": "unbound_knowledge_bases_only",
    "chunk_changes_apply_to": "new_or_reprocessed_documents"
  }
}
```

`sources` 的值只允许 `database/environment/default`。

#### `PATCH /settings`

部分更新；省略字段表示不变，显式 `null` 表示清除数据库覆盖并回退到环境/默认值。

```json
{
  "llm_provider": "ollama",
  "llm_base_url": "http://localhost:11434",
  "llm_model": "configured-model-name",
  "temperature": 0.2,
  "top_k": 6
}
```

响应 `200`，格式与 GET 相同，并可附：

```json
{
  "warnings": [
    "Embedding 设置不会改变已经绑定 profile 的知识库。"
  ]
}
```

跨字段校验在应用最终有效值上进行。例如只更新 `chunk_overlap=1200`，但有效 `chunk_size=1000` 时必须返回 422。

## 7. 删除语义

MVP 使用硬删除，无回收站。

### 7.1 Document 删除

顺序：

1. 查询 Document、所有 vector IDs 和 storage key。
2. 幂等删除 Chroma vectors；Chroma 不可用时返回 `503 VECTOR_STORE_UNAVAILABLE`，数据库和文件保持。
3. 幂等删除物理文件；不存在视为成功，其他错误返回 `500 STORAGE_ERROR`。
4. 数据库事务删除 Document，级联 Chunks；Citation 外键 `SET NULL`，快照保留。
5. commit 后返回 204。

如果第 4 步数据库失败，API 返回 500；再次 DELETE 必须把已缺失的 vector/file 当作成功并继续删除数据库记录。

### 7.2 KnowledgeBase 删除

- 若存在 pending/processing 文档，先返回 `409 DOCUMENT_BUSY`，不执行任何删除。
- 删除该 KB 所有文档 vectors 和物理文件后，再数据库级联删除 KB 全部资源。
- 任一外部删除失败时不进入数据库删除阶段，并返回相应错误。
- KnowledgeBase 删除会删除其 Chat 和 Citation，不保留历史会话。

### 7.3 ChatSession 删除

仅数据库事务，级联 Messages 与 Citations，不触碰文档、文件或向量。

### 7.4 重复 DELETE

资源已不存在时返回 `404 RESOURCE_NOT_FOUND`。HTTP 操作的最终状态仍是幂等的，但客户端不得依赖第二次仍返回 204。

## 8. 错误格式与错误码

### 8.1 错误响应

```json
{
  "error": {
    "code": "DUPLICATE_DOCUMENT",
    "message": "该知识库中已存在相同内容的文档。",
    "details": {
      "existing_document_id": "a0a932ff-3d36-4bcf-aa11-f22210bfa7cd"
    },
    "request_id": "d7b3d8fb-a6b7-45bd-8608-64f5808b93c3"
  }
}
```

- `message` 可展示给用户，但不得含 traceback、内部绝对路径或 Provider 原始敏感内容。
- `details` 可空，只放安全、结构化、可操作的数据。
- Pydantic 校验错误也转换成同一外壳，不能返回另一套格式。

### 8.2 HTTP 与业务错误码

| HTTP | `code` | 场景 |
|---:|---|---|
| 400 | `BAD_REQUEST` | 无法解析或语义不完整的请求 |
| 404 | `RESOURCE_NOT_FOUND` | KB、Document、Session 等不存在 |
| 409 | `DUPLICATE_DOCUMENT` | 同 KB 已有相同 SHA-256 |
| 409 | `DOCUMENT_BUSY` | pending/processing 时重复重处理或冲突操作 |
| 409 | `SOURCE_FILE_MISSING` | 重新处理所需原文件缺失 |
| 409 | `EMBEDDING_PROFILE_MISMATCH` | 尝试把不同 profile 写入已绑定 KB |
| 413 | `FILE_TOO_LARGE` | 超过配置上限 |
| 415 | `UNSUPPORTED_FILE_TYPE` | 扩展名、签名或结构不支持 |
| 422 | `VALIDATION_ERROR` | 字段长度、范围、跨字段约束失败 |
| 422 | `EMPTY_FILE` | 0 字节或无有效内容的文本文件 |
| 500 | `DATABASE_ERROR` | 数据库未预期失败 |
| 500 | `STORAGE_ERROR` | 文件持久化/删除失败 |
| 502 | `PROVIDER_AUTH_FAILED` | 上游 Provider 拒绝认证；不回显上游正文 |
| 502 | `PROVIDER_ERROR` | 上游非超时失败 |
| 503 | `PROVIDER_NOT_CONFIGURED` | 选定 Provider 缺模型、Base URL 或必需 Key |
| 503 | `VECTOR_STORE_UNAVAILABLE` | Chroma 不可用 |
| 504 | `PROVIDER_TIMEOUT` | LLM/Embedding 超时 |

以下是 Document 后台处理错误，通常体现在 Document `failed`，不作为上传请求的 HTTP 状态：

| `last_error_code` | 含义 |
|---|---|
| `PROCESS_INTERRUPTED` | 进程重启导致任务中断 |
| `PARSE_FAILED` | parser 异常或文档损坏 |
| `ENCRYPTED_PDF` | PDF 加密且无法读取 |
| `NO_EXTRACTABLE_TEXT` | 扫描 PDF 或文档无可提取文本 |
| `CHUNKING_FAILED` | Chunk 过程失败或无有效 Chunk |
| `EMBEDDING_FAILED` | embedding 调用或向量校验失败 |
| `INDEXING_FAILED` | Chroma/SQL 最终写入失败 |
| `SOURCE_FILE_MISSING` | 后台任务启动时原文件不存在 |

## 9. 文件校验契约

| 格式 | 扩展名 | 逻辑 MIME | 必须校验 |
|---|---|---|---|
| PDF | `.pdf` | `application/pdf` | `%PDF-` 文件头、页数上限、加密状态 |
| DOCX | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | ZIP 头、`[Content_Types].xml`、`word/document.xml`、解压限制 |
| TXT | `.txt` | `text/plain` | 非空、无 NUL、可解码、二进制比例 |
| Markdown | `.md/.markdown` | `text/markdown` | 与 TXT 同类文本校验 |

- 客户端 MIME 只作提示，不能单独决定格式。
- 文件名含 `/`、`\`、NUL、控制字符或路径段 `..` 时拒绝。
- 原文件名最大 255 字符；内部存储名不使用原文件名。
- 默认最大 25 MiB；限制值由只读环境配置控制，不通过 Settings API 修改。
- DOCX 必须限制 ZIP entry 数、总解压大小和异常压缩比，防止 ZIP bomb。

## 10. 检索与回答契约

- 问题 embedding 使用 KB 绑定 profile。
- Chroma 初始候选数为 `min(top_k * 3, 60)`。
- 用 `knowledge_base_id` 做向量 metadata 过滤，再在 SQL 中校验 Document `ready` 和 profile hash。
- `similarity = 1 - cosine_distance`；先阈值过滤，再取最终 `top_k`。
- 候选按 `score DESC, chunk_id ASC` 稳定排序。
- 上下文标签按最终排序生成 `S1..Sn`。
- 每个上下文包含可信元数据和不可信文档正文边界。
- Prompt 明确禁止把文档正文当作系统指令。
- 模型输出中只有本次 `S1..Sn` 可映射为 Citation；未知标签不返回。
- 为便于用户检查，`sources` 返回实际参与回答的合法检索片段；不允许前端自行按文档名构造来源。
- 无可靠上下文不是错误响应，而是 completed assistant message、固定资料不足文本和空 sources。

## 11. 前后端联调约束

- 前端统一从一个 API client 读取成功/错误格式，不在页面中拼接 URL。
- 上传网络进度由 Axios `onUploadProgress` 展示；上传完成后切换为服务端 `processing_stage`。
- 轮询只针对 `pending/processing`，默认间隔 2 秒，页面不可见或资源终态时停止。
- Chat 发送期间禁用同一会话重复提交，但允许用户浏览其他会话。
- Citation 点击打开 Drawer，内容来自 `CitationResource` 快照；不得重新让 LLM 生成来源说明。
- `demo_mode=true` 时页面必须展示克制但清晰的“演示模式”标识。
- API Key 在 Settings 中只显示“已配置/未配置”，不提供回显输入框。

## 12. 契约验收用例

至少用自动化测试固定以下行为：

1. 创建 KB 后 profile 未绑定；首次成功上传后绑定为实际 provider/model/dimension。
2. 同 KB 重复内容返回 409 和 `existing_document_id`；不同 KB 可上传。
3. PDF 第一页返回 `page_number=1`，不是 0。
4. 无页码文档返回 `null`，不返回 0。
5. pending/processing 文档不参与检索。
6. 无命中时不调用 Mock LLM，返回资料不足和空 sources。
7. 模型返回 `[S99]` 时不产生假 Citation。
8. 删除 Document 后历史 Citation 快照仍存在，外键为空。
9. ready 文档重处理失败后为 failed，旧索引不参与检索。
10. 修改全局 embedding 默认值不改变已绑定 KB profile。
11. Settings 响应和日志中不存在 API Key。
12. OpenAI/Ollama timeout 映射 504；认证错误映射 502，且不回显原始敏感正文。
13. 后台处理进程中断后启动恢复将文档标为 `PROCESS_INTERRUPTED`。
14. KB 删除清理文件、vectors 和全部关系记录；任一外部清理失败时不报告 204。
15. Demo Provider 无 Key 时仍能完成上传 → ready → retrieval → answer → citation。

以上字段、状态、端点和语义是 MVP 的冻结契约。若实现发现契约不可行，应先更新本文和架构 ADR，再同步修改后端 schema、前端类型与测试，不能只改单侧代码。
