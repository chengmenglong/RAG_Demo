# AI 私有知识库系统：需求追踪矩阵

> 文档状态：规划基线，尚未执行验收
> 基线日期：2026-08-22
> 适用范围：当前仓库的可交付 MVP
> 上游来源：用户给出的 17 部分原始需求
> 下游用途：P00–P15 执行计划、任务卡、测试、验收、Code Review 和最终交付

## 1. 使用规则

1. 本文是需求事实源。任务卡、代码、测试、README 和验收记录都必须引用本文的稳定 ID。
2. 已发布的 ID 不重排、不复用、不静默删除。需求变化时新增 ID；废弃项保留并标记原因。
3. 本文只定义“必须实现什么”和“如何证明”，不把尚未运行的命令或尚未观察的 UI 写成通过。
4. 本文是静态契约，不在此维护动态状态。动态状态和已执行证据只写入 `EXECUTION_STATE.md`；在其中出现有效证据前，需求均视为 `NOT_VERIFIED`。
5. 任务状态只在 `EXECUTION_STATE.md` 使用 `NOT_STARTED/READY/IN_PROGRESS/BLOCKED/DONE/SKIPPED`；验收记录只使用 `NOT_RUN/PASS/FAIL/BLOCKED`，两套状态不得混用。
6. “存在文件”“存在接口”“测试文件已编写”“Mock 返回固定字符串”都不能单独作为 `VERIFIED` 证据。
7. 外部 OpenAI-compatible 服务、Ollama 或真实模型不可用时，只能验证适配器契约和 Mock 闭环；真实调用必须标记 `BLOCKED` 或 `NOT_RUN`，不能冒充成功。

## 2. 优先级定义

| 级别 | 含义 |
|---|---|
| MUST | MVP 验收必需；未满足时不能发布 |
| SHOULD | 原文明确为“如果合理可加入”或重要增强；可延期，但必须说明 |
| CONDITIONAL | 仅在采用相应功能或现场具备外部条件时必须验证 |

## 3. P00–P15 阶段目录

| 阶段 | 名称 | 主要产出 |
|---|---|---|
| P00 | 基线与契约冻结 | 目录盘点、范围、决策、API/数据/错误契约、证据规则 |
| P01 | 可运行骨架 | 后端和前端骨架、依赖锁定、健康检查、最小启动链路 |
| P02 | 配置/数据库/迁移基础 | Settings 配置基础、SQLAlchemy、Alembic、持久目录 |
| P03 | 知识库与 Dashboard 后端 | 知识库 CRUD、统计、最近数据 API |
| P04 | 文档存储与上传生命周期 | 文件验证、安全存储、去重、状态机、删除和重试入口 |
| P05 | 文本解析/清洗/Chunk | 四种格式解析、来源元数据、清洗、可配置分块 |
| P06 | Settings 与 Provider | Settings API、密钥边界、Embedding/LLM Provider |
| P07 | 向量写入与检索 | 向量持久化、隔离、幂等、阈值与 Top-K |
| P08 | RAG/Citation/Chat 后端 | Prompt、拒答、结构化引用、会话和消息 API |
| P09 | 后端安全稳定性与日志 | 异常、超时、资源、恢复、结构化日志和脱敏 |
| P10 | 前端基础/Dashboard/知识库 | SaaS Shell、Dashboard、知识库列表与详情 |
| P11 | 文档管理前端 | 拖拽上传、进度、状态、失败重试、删除 |
| P12 | Chat/Citation/Settings 前端 | Chat、历史、引用交互、Settings、主要 UX 状态 |
| P13 | Demo/Docker/README | 无 Key Demo、种子数据、容器、部署和二开文档 |
| P14 | 综合验收 | 全量测试、构建、真实启动、核心流程、持久性和视觉检查 |
| P15 | 独立 Review/修复/发布审查 | 严格 Review、重要问题修复、全量回归、发布结论 |

## 4. 原始 17 部分覆盖映射

| 原始部分 | 主题 | 需求 ID | 主阶段 |
|---|---|---|---|
| §1 | 工作方式 | GOV-01、GOV-02、REVIEW-01、FINAL-01 | P00、P14、P15 |
| §2 | 产品目标 | GOV-02、DOC-06、DOC-10、RAG-01、RAG-03、CIT-01、UI-01 | P04–P12 |
| §3 | 推荐技术栈 | ARC-01、ARC-02、CFG-01、DB-01、STORE-01、PROV-01、PROV-02 | P00–P07 |
| §4 | 核心功能 | DASH-01、KB-01–03、DOC-01–13、RAG-01–05、CIT-01–03、CHAT-01–03 | P03–P12 |
| §5 | 系统设置 | CFG-02、SET-01–03 | P02、P06、P12 |
| §6 | 工程要求 | ARC-01、ARC-02、DB-02、STORE-01 | P00–P02 |
| §7 | 安全和稳定性 | DOC-03、DOC-11–13、PROV-03、SEC-01、SEC-02 | P04、P07、P09 |
| §8 | 日志 | LOG-01 | P09 |
| §9 | 测试 | TEST-01–05 | 增量执行，P14 汇总 |
| §10 | Docker | DOCKER-01、DOCKER-02 | P13、P14 |
| §11 | Demo 模式 | DEMO-01、DEMO-02 | P13、P14 |
| §12 | README | README-01 | P13、P15 |
| §13 | 接单复用能力 | ARC-02、CFG-01、STORE-01、DB-01 | P00–P02、P15 |
| §14 | UI 要求 | UI-01–03 | P10–P12、P14 |
| §15 | 最终验收 | TEST-04、TEST-05、FINAL-01 | P14 |
| §16 | Code Review | REVIEW-01 | P15 |
| §17 | 最终输出 | FINAL-01 | P15 |

覆盖结论：17 个原始部分均有稳定 ID 和执行阶段；后续若新增需求，只能追加，不能改写本表以掩盖范围变化。

## 5. 详细需求追踪矩阵

### 5.1 治理、架构、配置与持久化

| ID | 来源 | 级别 | 阶段 | 必须实现 | 验收证据 | 依赖/明确化 |
|---|---|---|---|---|---|---|
| GOV-01 | §1 | MUST | P00 | 修改前盘点目录、隐藏配置、已有代码、依赖、Git 状态和可运行性；保留合理设计与用户改动 | 基线文件树、Git 状态、既有启动/测试命令及结果 | 禁止覆盖或清理不明改动 |
| GOV-02 | §1、§2、§17 | MUST | P00–P14 | 交付真实闭环：建库→上传→解析→Chunk→Embedding→Retrieval→LLM Answer→Citation | 自动化集成测试加真实运行记录；每阶段有产物 | 空接口和固定答案不算 |
| ARC-01 | §3、§6 | MUST | P00–P01 | 后端按 api/services/models/schemas/repositories/rag/providers/document_processing/config/utils/tests 分层；前端按 components/pages/services/hooks/types 分层 | 文件树与依赖 Review；逻辑不集中在入口文件 | 目录存在但为空不算 |
| ARC-02 | §6、§13 | MUST | P00、P15 | Provider、Vector Store、Document Parser、File Storage 使用清晰替换边界；不硬编码客户、Logo、厂商、数据库、知识库名 | 接口及生产、Demo/测试适配器；Review 无客户耦合 | 未来功能只列扩展点，不做空壳 |
| CFG-01 | §3、§10、§13 | MUST | P00–P02 | 数据库、存储路径、Provider、Base URL、模型、超时、大小限制通过环境配置，提供无密钥的 .env.example | 配置测试；默认值/单位文档；仓库和镜像无真实 Key | 逐项说明必填条件 |
| CFG-02 | §3、§5 | MUST | P00、P02、P06 | 冻结环境变量、数据库 Settings 和运行时配置优先级 | 冲突值测试证明固定优先级 | 建议 Key 仅环境；非敏感 DB 设置覆盖环境默认 |
| DB-01 | §3、§9、§13 | MUST | P02 | SQLite 默认持久化；SQLAlchemy 和 DATABASE_URL 保留 PostgreSQL 能力；使用可复现迁移 | Alembic upgrade；重启数据仍在；无核心 SQLite 专用 SQL | 时间统一 UTC；建议 UUID 主键 |
| DB-02 | §4、§5、§6 | MUST | P03–P08 | 随功能阶段建模 KnowledgeBase、Document、Chunk、ChatSession、ChatMessage、MessageCitation、AppSettings 及索引关系 | ER 图、各阶段迁移、关系和级联测试 | P02 只建立迁移框架；引用快照避免历史失效 |
| STORE-01 | §3、§10、§13 | MUST | P02、P04、P07 | 原文件与向量索引使用可配置持久目录和替换式适配边界 | 重启仍可下载/检索；Docker 卷；路径无散落硬编码 | 为对象存储和其他向量库留边界 |

### 5.2 知识库和 Dashboard

| ID | 来源 | 级别 | 阶段 | 必须实现 | 验收证据 | 依赖/明确化 |
|---|---|---|---|---|---|---|
| KB-01 | §4.2 | MUST | P03、P10 | 创建、查询、编辑名称/描述、删除知识库 | API 覆盖成功、404、非法名称；UI 完成同样操作 | P00 冻结重复、长度、空白规则 |
| KB-02 | §4.2 | MUST | P03 | 详情返回文档数、有效 Chunk 数、创建时间、更新时间 | 上传、失败、删除、重处理后统计正确 | 固定文档与 active Chunk 统计口径 |
| KB-03 | §4.2、§7 | MUST | P03–P09 | 删除知识库时一致清理 SQL、向量、文件、会话及其 Citation；只有单独删除 Document 时保留历史 Citation 快照 | 删除后 API 404、搜索无命中、无文件和孤儿行 | 依赖 STORE-01、DOC-12、CHAT-01 |
| DASH-01 | §4.1 | MUST | P03、P10 | 返回并展示知识库数、文档数、Chunk 数、最近知识库、最近上传和快速问答入口 | 固定数据集下数量/排序断言；空数据 Empty State | 冻结“最近”的字段和条数 |

### 5.3 文档上传、解析与 Chunk

| ID | 来源 | 级别 | 阶段 | 必须实现 | 验收证据 | 依赖/明确化 |
|---|---|---|---|---|---|---|
| DOC-01 | §2、§4.3 | MUST | P04–P05 | PDF、DOCX、TXT、Markdown 均能上传并提取有效文本 | 四种真实夹具均形成可检索 Chunk | OCR 不在 MVP；无文本必须失败 |
| DOC-02 | §4.3 | MUST | P04、P11 | 拖拽、上传字节进度、解析状态、失败、重处理和删除 | 浏览器实测；慢上传与慢处理状态可区分 | 两类进度不得混淆 |
| DOC-03 | §4.3、§7 | MUST | P04、P09 | 服务端验证扩展名、签名/容器、大小、空文件、文件名和路径 | 覆盖空、伪扩展、超限、非法路径、不支持格式 | 默认 25 MiB，可配置 |
| DOC-04 | §4.3 | MUST | P04 | 用 SHA-256 内容哈希识别重复 | 同库同内容返回 409 和已有 ID；跨库允许上传 | 同一知识库内去重 |
| DOC-05 | §4.3、§4.4 | MUST | P04 | 至少有 pending/processing/ready/failed 状态，并保留当前阶段和安全错误摘要 | API/UI 状态变化；失败可重试 | stage 使用 queued/extracting/cleaning/chunking/embedding/indexing/completed/failed 合法组合 |
| DOC-06 | §4.4、§8 | MUST | P05、P07 | 独立 Pipeline 执行验证、提取、清洗、Chunk、Embedding、向量写入，逐阶段处理异常 | 注入故障后状态、阶段、日志和清理正确 | 不长期阻塞上传请求 |
| DOC-07 | §4.5、§4.7 | MUST | P05 | Chunk 保存 document_id、显示名、页码、章节、chunk_id 和顺序 | PDF 引用页码与原页一致；无页码为 null | 页码在提取时保留 |
| DOC-08 | §4.4 | MUST | P05 | 清洗空白但保留段落、页码和章节；无有效文本进入 failed | 空 PDF/DOCX、空白 TXT 不生成 Chunk | 清洗不能破坏来源映射 |
| DOC-09 | §4.5、§5 | MUST | P05、P06 | chunk_size/overlap 可配置，保证 0≤overlap<size，Chunk 稳定关联原文 | 长度、重叠、顺序、稳定 ID 单测 | 单位固定为字符，除非 P00 另有记录 |
| DOC-10 | §2、§4.4 | MUST | P07 | 批量生成向量并持久化，metadata 可过滤知识库和文档 | 重启仍可搜；A 库不命中 B 库 | 记录 provider/model/dimension/profile_version/profile_hash |
| DOC-11 | §4.4、§7 | MUST | P07、P09 | 单次处理失败不暴露本次半成品；重复重试不产生重复 Chunk/向量 | 故障后本次 SQL/Chroma 写入被补偿；重复重试仅一套索引 | 使用确定性 ID、顺序写入和补偿清理 |
| DOC-12 | §4.3、§7 | MUST | P04、P07 | 删除清理原文件、Chunk、向量；重处理按冻结契约破坏性重建旧索引 | 删除后无残留；重处理后无重复、统计正确；失败为 failed 且可再次重试 | 重处理开始即清旧索引，UI 必须事前警告；历史 Citation 快照不变 |
| DOC-13 | §4.3、§7 | MUST | P09 | 重启后不存在永久 processing 僵尸任务；可恢复或标记失败重试 | 处理中重启测试后状态可解释且能继续 | 记录进程内任务限制 |

### 5.4 Provider、检索和 RAG

| ID | 来源 | 级别 | 阶段 | 必须实现 | 验收证据 | 依赖/明确化 |
|---|---|---|---|---|---|---|
| PROV-01 | §3、§4.4 | MUST | P06 | 统一 Embedding 接口，至少有 OpenAI-compatible 与确定性 Demo/Mock 实现，可扩展本地模型 | embed_documents/embed_query 合约、批处理、错误测试 | Demo 不使用随机化 hash |
| PROV-02 | §3、§4.6 | MUST | P06 | 统一 LLM 接口，支持 OpenAI-compatible 和 Ollama | 两适配器契约测试；条件允许再做 live smoke | 无服务不能声明 live 通过 |
| PROV-03 | §7、§8 | MUST | P06、P09 | Provider 有超时、有限重试、清晰错误；客户端和流正确关闭；日志脱敏 | 超时映射 502/504；资源与密钥测试 | 不对不可重试 4xx 无限重试 |
| RAG-01 | §2、§4.6 | MUST | P07–P08 | Query Embedding 后只在所选知识库 Vector Search 和 Top-K Retrieval | 已知语料命中顺序、跨库隔离、空库测试 | 会话绑定 knowledge_base_id |
| RAG-02 | §4.6、§5 | MUST | P07 | Top-K 和 Similarity Threshold 可配置；统一为数值越大越相似 | 阈值边界；低分结果不进上下文 | 适配层统一 distance/similarity |
| RAG-03 | §4.6 | MUST | P08 | Prompt 规定只依据上下文、不足时说明、文档内指令不是系统指令 | Prompt 快照；Mock 验证上下文和规则 | 使用清晰分隔符 |
| RAG-04 | §4.6 | MUST | P08 | 无可靠结果时不调用 LLM，返回资料不足且 sources 为空 | 空库、无关问题、高阈值均拒答 | 在检索层拒答 |
| RAG-05 | §4.6、§7 | MUST | P08 | 限制 Top-K 和上下文预算，不发送全部文档 | 长文测试；日志记录候选/入选数和预算 | P00 冻结预算策略 |

### 5.5 引用和 Chat

| ID | 来源 | 级别 | 阶段 | 必须实现 | 验收证据 | 依赖/明确化 |
|---|---|---|---|---|---|---|
| CIT-01 | §2、§4.7 | MUST | P08 | 返回结构化 sources：标签、document_id、chunk_id、名称、页码/章节、excerpt、score | 每个 `[S1]...[Sn]` 映射唯一 source，且属于本次检索 | 来源不能从 LLM 文本猜 |
| CIT-02 | §4.7 | MUST | P12 | 点击引用显示名称、页码/章节和相关原文 | UI 内容与 API source 完全相同 | 无页码时不伪造 |
| CIT-03 | §4.7、§4.8 | MUST | P08 | 保存引用快照，使单独删除或重处理文档后历史消息来源仍可解释 | 重启、文档改名/删除后的历史引用测试 | 删除整个 KB 时会连同会话删除 |
| CHAT-01 | §4.8 | MUST | P08 | 新建、列出、查看、删除会话；持久化用户/AI 消息；会话绑定知识库 | API、重启、删除级联测试 | 与 KB-03 一致 |
| CHAT-02 | §4.8 | MUST | P08、P12 | 显示用户消息、回答、引用、Loading、Error、新会话、历史、删除 | 慢响应和失败实测，不重复提交 | 冻结历史进入 Prompt 的轮数 |
| CHAT-03 | §4.8、§7 | CONDITIONAL | P12 | 若实现 Markdown/代码块则安全渲染、防 XSS；复制答案可选 | 恶意 HTML 不执行；复制准确 | 不实现时明确范围外 |

### 5.6 Settings、UI、安全、日志与 Demo

| ID | 来源 | 级别 | 阶段 | 必须实现 | 验收证据 | 依赖/明确化 |
|---|---|---|---|---|---|---|
| SET-01 | §5 | MUST | P06、P12 | 配置 LLM Provider/Base URL/Model、Embedding Provider/Model、Temperature、Top-K、Threshold、Chunk Size/Overlap | 加载、校验、保存、刷新和生效测试 | LLM/Embedding Base URL 建议分开 |
| SET-02 | §3、§5、§7 | MUST | P06、P09、P12 | 普通 API、日志、错误和前端状态不返回明文 API Key | 响应仅 configured 或掩码；自动断言无 Key | Key 最好只来自环境 |
| SET-03 | §5 | MUST | P06–P07、P12 | 区分即时生效、仅影响新文档和不可在线迁移的设置 | Top-K 下一请求生效；Chunk 变化提示 reprocess；Embedding 默认变化提示只影响未绑定 KB | 已绑定 KB 永远使用原 profile；改模型需新建 KB 并重新上传 |
| UI-01 | §2、§4、§14 | MUST | P10–P12 | Sidebar、Dashboard、知识库列表/详情、文档管理、Chat、Settings 路由完整 | 导航/刷新可达，控制台无明显错误 | 桌面端优先 |
| UI-02 | §4、§14 | MUST | P10–P12 | Cards、Tables、Modal、Toast、Loading、Empty、Error 齐全；危险删除确认 | 成功、空、慢、失败路径证据 | 不能只验成功路径 |
| UI-03 | §4.1、§14 | MUST | P10–P14 | 现代、专业、简洁 SaaS；避免大量渐变、动画、超大标题和 Emoji | 1440×900、1366×768 截图；无溢出/错位 | 组件库不等于视觉通过 |
| SEC-01 | §7 | MUST | P04、P09 | 处理异常 API、非法参数、数据库、上传、解析、Embedding、LLM 超时；生产响应无堆栈 | 400/404/409/413/415/422/502/503/504 测试 | 无认证时仅适合受控环境 |
| SEC-02 | §7 | MUST | P04、P09 | 服务端生成存储名，显示名分离；路径约束在根目录；限制 DOCX 解压风险 | 路径穿越、同名、Unicode、异常容器测试 | 依赖 DOC-03、STORE-01 |
| LOG-01 | §8 | MUST | P09 | 结构化记录 upload、parse、embedding、vector_write、rag_query、llm_call、exception | 含 event/request_id/kb_id/document_id/duration/status；无 Key/全文 | JSON 或稳定 key-value |
| DEMO-01 | §11 | MUST | P13 | 无 Key 时可启动、浏览、建库、上传和解析；Demo Provider 完成确定性 RAG/引用闭环 | LLM/Embedding 均配置为 `demo` 的离线端到端测试；页面标识 Demo | 固定问答字典不能替代检索 |
| DEMO-02 | §11、§13 | MUST | P13 | 提供无客户品牌的样本文档和幂等 seed 命令 | seed 两次不重复；有清理说明；生产不自动 seed | 依赖 DEMO-01 |

### 5.7 测试、Docker、文档、Review 与交付

| ID | 来源 | 级别 | 阶段 | 必须实现 | 验收证据 | 依赖/明确化 |
|---|---|---|---|---|---|---|
| TEST-01 | §9 | MUST | 增量、P14 | 后端覆盖知识库 CRUD、四格式上传、Chunk、Retrieval、Provider、异常输入，并补充引用、级联、去重、隔离、拒答 | 全量 pytest 记录测试数、耗时、退出码 | 写测试不等于运行 |
| TEST-02 | §9、§11 | MUST | P06–P08、P14 | Mock Provider 验证真实输入、上下文、错误、超时和引用 | 证明命中 Chunk 传给 Mock LLM，引用来自该 Chunk | 不替代 live 验证 |
| TEST-03 | §9、§14 | MUST | P10–P14 | 运行前端 lint、TypeScript 检查、单测和 production build | 四类命令退出码 0 | dev server 打开不够 |
| TEST-04 | §15 | MUST | P14 | 启动真实前后端，完成核心闭环和关键失败路径 | 自动 E2E 或逐步手工证据；控制台/网络无明显异常 | 含失败重试、拒答、引用点击 |
| TEST-05 | §15 | MUST | P14 | 服务/容器重启后知识库、文档、索引、会话仍可用 | 重启前后同查询仍命中、历史存在 | 依赖 DB-01、STORE-01 |
| DOCKER-01 | §10、§15 | MUST | P13–P14 | 提供 Dockerfile、docker-compose.yml、.env.example；docker compose up 可启动 | compose config/build/up、健康检查、浏览器和 smoke | 实测 API URL、CORS/代理 |
| DOCKER-02 | §10 | MUST | P13 | 数据使用 volume；密钥仅运行时注入；镜像上下文排除 .env/数据 | 重启数据仍在；镜像/仓库无 Key；.dockerignore 审查 | 禁止真实 Key 进入镜像层 |
| README-01 | §12、§17 | MUST | P13、P15 | README 覆盖介绍、功能、截图、架构、技术栈、目录、快速启动、环境变量、OpenAI-compatible、Ollama、Docker、开发、测试、FAQ、二开 | 干净环境按 README 启动；命令和文件存在 | 区分 Demo、Mock、契约和 live |
| REVIEW-01 | §1、§16 | MUST | P15 | 审查架构、重复、Bug、异常、安全、类型、数据库、异步、泄漏、RAG、Prompt、状态、UX、Docker、配置和测试 | 问题清单含严重度、文件、修复、验证；修复后回归 | “未发现”也要有证据 |
| FINAL-01 | §15、§17 | MUST | P14–P15 | 最终按原文 10 项总结；安装、启动、DB、闭环、引用、UI、API、测试、Docker、README 逐项判定 | 仅用 PASS/FAIL/BLOCKED/NOT_RUN，逐项附命令或截图 | 未运行不得写 PASS |

## 6. P00 必须冻结的口径

| 决策 | 默认建议 | 关联 ID |
|---|---|---|
| 用户边界 | 单用户、无认证，仅本机或受控内网 | SEC-01、ARC-02 |
| 重复定义 | 同库按 SHA-256 内容去重，跨库允许重复 | DOC-04 |
| 文件大小 | 默认 25 MiB，可配置 | DOC-03、CFG-01 |
| Chunk | 字符；0≤overlap<size | DOC-09 |
| 状态 | pending/processing/ready/failed；stage 采用冻结的合法组合 | DOC-05 |
| 后台任务 | 可用进程内任务，但有重启僵尸恢复；服务边界可替换 | DOC-06、DOC-13 |
| 配置优先级 | Key 仅环境；非敏感 DB Settings 覆盖环境默认 | CFG-02、SET-02 |
| 相似度 | 适配层统一为值越大越相似，并注明范围 | RAG-02 |
| 索引版本 | 保存 provider/model/dimension/profile_version/profile_hash 与文档 Chunk 配置快照 | DOC-10、SET-03 |
| 重处理 | 显式破坏性重建：开始时清旧索引，期间不可检索；失败不恢复旧索引，可再次重试 | DOC-11、DOC-12 |
| 引用历史 | Assistant Message 保存名称、页码/章节、excerpt、chunk_id/document_id 快照 | CIT-03 |
| Chat 上下文 | 检索用当前问题；生成只带有限最近轮次 | CHAT-02、RAG-05 |
| 无结果 | 检索层拒答，不调用 LLM，sources 为空 | RAG-04 |
| Demo | 确定性 Demo Embedding 与基于检索片段的 Demo LLM | DEMO-01、TEST-02 |
| 非目标 | 不实现用户/RBAC/多租户/OCR/联网搜索/Agent/MCP/reranker/混合检索/图谱/第三方登录/对象存储/PostgreSQL/Redis 服务实例 | ARC-02 |

## 7. 数据关系与引用不可后补原则

~~~text
KnowledgeBase 1 ── N Document 1 ── N Chunk
KnowledgeBase 1 ── N Conversation 1 ── N Message
Assistant Message 1 ── N CitationSnapshot
Document/Chunk ── VectorStore metadata
AppSettings ── 全局非敏感运行设置
~~~

引用必须贯穿 P05 页码/章节、P05 Chunk metadata、P07 Vector metadata、P08 sources、P08 CitationSnapshot、P12 引用交互和 P14 对照验证。任何一环缺失都不能把 CIT-01 或 GOV-02 标为 `VERIFIED`。

## 8. 状态与证据引用规则

本文保持静态，不直接追加执行状态。每次任务开始、完成或阻塞时，应在 `EXECUTION_STATE.md` 的当前指针、任务行、阶段摘要和最近证据中原子更新；失败升级写入 `FAILURE_LOG.md`；影响契约的变更先写入 `DECISIONS.md`。

最近证据至少记录：Requirement ID、Gate、实际命令、退出码、测试数量、脱敏产物路径、结果摘要、阻塞和恢复条件。详细命令与证据占位见 `docs/implementation/05_ACCEPTANCE_GATES.md`。
