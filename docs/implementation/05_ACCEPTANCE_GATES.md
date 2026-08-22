# AI 私有知识库系统：P00–P15 验收门

> 文档状态：静态命令与证据模板；不得在本文维护动态状态
> 基线日期：2026-08-22
> 需求来源：`docs/implementation/01_REQUIREMENTS_TRACEABILITY.md`
> 当前实际状态与已执行证据：只查看 `EXECUTION_STATE.md`

## 1. 验收纪律

1. Gate 是进入下一阶段的硬条件，不是开发进度说明。
2. 只有实际执行命令、检查退出码、核对产物并填写证据后，才能把 Gate 改为 `PASS`。
3. 命令未运行写 `NOT_RUN`；外部服务不可用写 `BLOCKED`；命令失败或观察不符合写 `FAIL`。
4. 不允许用“预计通过”“代码看起来正确”“已创建测试”“Mock 通过所以真实 Provider 通过”等表述代替证据。
5. 测试收集数为 0、关键测试被 skip、前端只启动未 build、Docker 只做 config 未 up，都不能通过相应 Gate。
6. 修复任何影响核心闭环、安全、数据一致性、配置或部署的问题后，必须重新执行受影响 Gate；P15 修复后必须重跑 P14 全套。
7. 验收日志、截图和导出数据不得包含 API Key、Authorization Header、整篇私有文档或其他敏感信息。
8. 本文中的命令是目标命令契约。若 P00 冻结了不同包管理器或目录结构，必须先同步修改本文和 README，不能在执行时临时换一套且不留记录。

## 2. 状态和证据格式

### 2.1 Gate 状态

| 状态 | 含义 | 能否进入下一阶段 |
|---|---|---|
| NOT_RUN | 尚未实际执行 | 否 |
| RUNNING | 正在执行，结果未定 | 否 |
| PASS | 全部必需项有证据且通过 | 是 |
| FAIL | 已执行但至少一项不满足 | 否 |
| BLOCKED | 外部条件阻止执行，已记录原始错误和恢复条件 | 否；仅 CONDITIONAL 项可作为带限制发布 |

### 2.2 每个 Gate 的证据目录

统一使用 `artifacts/acceptance/Pxx/`，建议该目录加入 Git 忽略，但在最终验收摘要中链接必要的脱敏证据。

开始与结束命令：

~~~powershell
New-Item -ItemType Directory -Force -Path "artifacts\acceptance\Pxx" | Out-Null
Start-Transcript -Path "artifacts\acceptance\Pxx\session.log" -Append
# 在此实际运行该 Gate 的命令
Stop-Transcript
~~~

不得提前创建伪造的成功输出。以下是登记字段模板；每个 Gate 执行后把实际值写入 `EXECUTION_STATE.md` 的证据区，**不要修改本文中的模板状态**：

~~~markdown
- 状态：NOT_RUN | RUNNING | PASS | FAIL | BLOCKED
- 执行人/模型：
- 开始时间：
- 结束时间：
- Git commit/工作树摘要：
- 命令与退出码：
- 测试收集数/通过数/失败数/跳过数：
- API 或数据证据：
- UI 截图/录屏：
- 日志脱敏检查：
- 已知限制：
- 阻塞原始错误与恢复条件：
- 关联需求 ID：
~~~

## 3. 目标命令契约

为减少弱模型在不同阶段随意改变命令，P01 起应提供以下脚本或等价的、已在本文同步记录的命令：

| 命令 | 作用 |
|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/bootstrap.ps1` | 创建开发环境并安装锁定依赖 |
| `powershell -ExecutionPolicy Bypass -File scripts/start-dev.ps1` | 启动前后端开发服务 |
| `powershell -ExecutionPolicy Bypass -File scripts/stop-dev.ps1` | 停止由 start-dev 启动的进程 |
| `powershell -ExecutionPolicy Bypass -File scripts/test-backend.ps1` | 运行完整后端测试 |
| `powershell -ExecutionPolicy Bypass -File scripts/test-frontend.ps1` | 运行 lint、类型、单测和 build |
| `powershell -ExecutionPolicy Bypass -File scripts/seed-demo.ps1` | 幂等写入 Demo 数据 |
| `powershell -ExecutionPolicy Bypass -File scripts/smoke-core.ps1 -Provider demo` | 运行无外部 Key 的核心 API 闭环 |
| `powershell -ExecutionPolicy Bypass -File scripts/smoke-provider.ps1 -Provider <name>` | 条件性 live Provider smoke |
| `powershell -ExecutionPolicy Bypass -File scripts/acceptance.ps1` | 顺序执行 P14 可自动化验收 |

若项目不创建包装脚本，则 P00 必须在本文记录逐条等价命令，并保证 README 使用同一套命令。

## 4. Gate 依赖

~~~text
P00 → P01 → P02 → P03 → P04 → P05 → P06 → P07
  → P08 → P09 → P10 → P11 → P12 → P13 → P14 → P15
~~~

阶段间可以存在逻辑上独立的工作，但 Luna 仍须串行执行原子任务，任意时刻最多一个 `IN_PROGRESS`；Gate 不能越级标记 PASS。P10 只能在 P09 后连接稳定 API 并通过验收。

---

## P00 Gate：基线与契约冻结

关联需求：GOV-01、GOV-02、ARC-01、ARC-02、CFG-02、DOC-04、DOC-09、DOC-13、RAG-02、CIT-03、CHAT-02、FINAL-01。

### 必须执行

~~~powershell
Get-Location
Get-ChildItem -Force
git status --short --branch
git log -1 --oneline
rg --files
rg --files -g "AGENTS.md" -g ".env*" -g "docker-compose*.yml" -g "compose*.yml"
~~~

### 必须核对

- 保存基线文件树、已有代码/文档、已有启动和测试结果。
- 冻结目录、API 前缀、错误响应、ID/时间、配置优先级和 P00 决策表。
- 明确单用户受控环境、OCR 等非目标、重复规则、Chunk 单位、引用快照、重处理与无结果策略。
- 不修改或清理不属于本任务的已有用户改动。
- 17 个原始部分均映射到稳定需求 ID 和 P00–P15。

### PASS 条件

所有上项有文字证据；不再存在会改变数据模型、Provider 边界、索引 metadata 或引用链的未决问题。

### 证据登记

- 状态：`NOT_RUN`
- 命令/退出码：
- 基线树与 Git 状态：
- 决策记录：
- 未决项/阻塞：

---

## P01 Gate：可运行骨架

关联需求：ARC-01、ARC-02、CFG-01。

### 必须执行

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/bootstrap.ps1
powershell -ExecutionPolicy Bypass -File scripts/start-dev.ps1
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/health"
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:5173/"
powershell -ExecutionPolicy Bypass -File scripts/stop-dev.ps1
~~~

### 必须核对

- 后端入口只负责装配，不堆叠业务逻辑。
- 前端路由和 API Client 有最小可运行骨架。
- Python 和 Node 依赖有锁定文件；重复 bootstrap 可安全执行。
- health 返回稳定 JSON，前端首页返回 2xx。

### PASS 条件

全新开发环境按 bootstrap 安装成功；前后端实际启动；health 与首页可访问；停止脚本仅停止本项目进程。

### 证据登记

- 状态：`NOT_RUN`
- bootstrap 退出码：
- 后端 health 响应：
- 前端 HTTP 状态：
- 启停日志：
- 阻塞：

---

## P02 Gate：配置/数据库/迁移基础

关联需求：ARC-01、CFG-01、CFG-02、DB-01、STORE-01、LOG-01、SEC-01、SET-02、SET-03、TEST-01、TEST-02、DOCKER-01。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
.\.venv\Scripts\python.exe -m alembic -c backend\alembic.ini current
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P02\pytest.xml
~~~

### 必须核对

- 空数据库可一次迁移到 head，第二次执行幂等。
- Alembic 框架、baseline revision、数据库连接、外键启用和 UTC helper 符合冻结契约；业务表会在 P03–P08 随功能 revision 建立。
- SQLite 数据库、上传目录、向量目录均来自配置。
- .env.example 无真实密钥；普通配置序列化不含 Key。
- 使用 DATABASE_URL，不在业务逻辑写 SQLite 专用 SQL。

### PASS 条件

迁移命令退出码 0；目标测试收集数大于 0 且全部通过；重启后测试数据可读取。

### 证据登记

- 状态：`NOT_RUN`
- Alembic head/current：
- pytest 收集/通过/失败：
- 表和索引摘要：
- 配置/密钥检查：
- 阻塞：

---

## P03 Gate：知识库与 Dashboard 后端

关联需求：KB-01、KB-02、KB-03、DASH-01。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P03\pytest.xml
powershell -ExecutionPolicy Bypass -File scripts/start-dev.ps1
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/health"
powershell -ExecutionPolicy Bypass -File scripts/stop-dev.ps1
~~~

### 必须核对

- CRUD 覆盖成功、404、空白/超长名称和更新时间。
- Dashboard 数量、最近排序和空数据口径固定。
- 此阶段先验证 SQL 级联；文件和向量清理在 P07/P09 完整复验。
- API 响应类型和错误结构与 P00 契约一致。

### PASS 条件

目标测试全部通过，收集数不为 0；同一固定数据集的 API 统计与数据库事实一致。

### 证据登记

- 状态：`NOT_RUN`
- pytest 统计：
- CRUD 样例响应：
- Dashboard 样例响应：
- 级联结果：
- 阻塞：

---

## P04 Gate：文档存储与上传生命周期

关联需求：DOC-01–05、DOC-12、SEC-02、STORE-01。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P04\pytest.xml
~~~

### 必须核对

- PDF/DOCX/TXT/Markdown 接受；未知格式、空文件、伪扩展、超限返回固定错误。
- 文件保存名由服务端生成，显示名单独保存；`..\`、绝对路径、Unicode 名均不能越界。
- 同库同内容返回 409 和已有 ID；跨库允许。
- 上传后状态机合法；失败原因可读但无堆栈/路径/密钥。
- 删除同时处理数据库与原文件；向量清理在 P07 复验。

### PASS 条件

目标测试全部通过；存储根目录外没有写入；失败样例不进入 ready。

### 证据登记

- 状态：`NOT_RUN`
- pytest 统计：
- 四格式上传结果：
- 413/415/409 等错误证据：
- 路径边界检查：
- 阻塞：

---

## P05 Gate：文本解析/清洗/Chunk

关联需求：DOC-01、DOC-06–09、CIT-01 前置条件。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P05\pytest.xml
~~~

### 必须核对

- 四种真实夹具均提取文本；无文本扫描 PDF 明确失败，不伪装 OCR 成功。
- PDF 页码、Markdown/DOCX 章节、段落和文档名在清洗后仍正确。
- Chunk 长度、overlap、确定性边界和稳定 ordinal 满足冻结口径；重处理可生成新 Chunk UUID，不要求跨版本 ID 相同。
- `0 <= chunk_overlap < chunk_size`；非法配置返回 422 或配置错误。
- 不跨不必要的页边界生成无法解释的引用。

### PASS 条件

四格式、空文本、边界配置和来源对照测试全部通过；至少人工抽查一个 PDF 页码和一个章节来源。

### 证据登记

- 状态：`NOT_RUN`
- pytest 统计：
- PDF 页码抽查：
- 章节抽查：
- Chunk 边界样例：
- 阻塞：

---

## P06 Gate：Settings 与 Provider

关联需求：CFG-02、PROV-01–03、SET-01–03、SET-02、TEST-02。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P06\pytest.xml
~~~

### 必须核对

- OpenAI-compatible Embedding/LLM、Ollama Embedding/LLM 均有契约测试。
- Demo Embedding 跨进程确定，不使用 Python 随机化 hash。
- Settings 边界值、优先级、持久化和生效分类正确。
- API、异常和日志不返回明文 Key；只暴露 configured 状态。
- 超时、有限重试、4xx 不重试和客户端关闭可验证。

### 条件性 live smoke

仅在真实凭据/服务已具备时执行：

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke-provider.ps1 -Provider openai_compatible
powershell -ExecutionPolicy Bypass -File scripts/smoke-provider.ps1 -Provider ollama
~~~

没有条件时，两项分别记录 `NOT_RUN` 或 `BLOCKED`，不得写 PASS。

### PASS 条件

MUST 契约与安全测试全部通过。Live smoke 是条件项，发布说明必须准确记录其状态。

### 证据登记

- 状态：`NOT_RUN`
- pytest 统计：
- Settings 优先级证据：
- 密钥脱敏证据：
- OpenAI-compatible live：
- Ollama live：
- 阻塞：

---

## P07 Gate：向量写入与检索

关联需求：DOC-06、DOC-10–12、RAG-01、RAG-02、SET-03、TEST-02。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P07\pytest.xml
~~~

### 必须核对

- 写入、查询、删除、重启持久性和知识库 metadata 过滤正确。
- A 库的查询绝不命中 B 库。
- score 被统一为“越大越相似”，阈值边界无方向错误。
- 同一文档重试/重处理不产生重复 active 向量。
- Embedding provider/model/dimension/profile_version/profile_hash 与向量绑定；不混查不兼容索引。
- 故障注入后无可检索半成品；冻结策略为破坏性重建，旧索引在 reprocess 开始后删除，失败文档保持 failed 且不可检索。

### PASS 条件

目标测试全部通过；重启前后同一查询结果稳定；跨库命中为 0；重复处理后 active 计数正确。

### 证据登记

- 状态：`NOT_RUN`
- pytest 统计：
- 重启前后检索：
- 跨库隔离：
- 重处理向量计数：
- 分数/阈值样例：
- 阻塞：

---

## P08 Gate：RAG/Citation/Chat 后端

关联需求：GOV-02、RAG-03–05、CIT-01、CIT-03、CHAT-01、CHAT-02、TEST-02。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P08\pytest.xml
powershell -ExecutionPolicy Bypass -File scripts/smoke-core.ps1 -Provider demo
~~~

### 必须核对

- Query→Embedding→Search→Top-K→Prompt→LLM→Answer→Sources 是同一请求链。
- Mock/Demo LLM 实际收到命中 Chunk，不是固定问答字典。
- 无命中时不调用 LLM，返回固定资料不足且 sources 为空。
- 每个答案 `[S1]...[Sn]` 映射唯一结构化 source，页码/excerpt 与 Chunk 一致。
- 会话绑定知识库，消息与引用快照重启后存在。
- 上下文预算和有限历史轮次按冻结口径执行。

### PASS 条件

目标测试和 Demo 核心 smoke 全部通过；至少一条有来源回答和一条拒答有完整证据。

### 证据登记

- 状态：`NOT_RUN`
- pytest 统计：
- smoke 退出码：
- 有来源回答/JSON：
- 拒答/LLM 未调用证据：
- 历史引用证据：
- 阻塞：

---

## P09 Gate：后端安全稳定性与日志

关联需求：DOC-03、DOC-11–13、PROV-03、SEC-01、SEC-02、SET-02、LOG-01、KB-03。

### 必须执行

~~~powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --junitxml=artifacts\acceptance\P09\pytest.xml
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m mypy backend\app
~~~

### 必须核对

- 400/404/409/413/415/422/502/504 与统一错误体准确。
- 异常响应无堆栈、绝对路径、Key；日志无 Authorization 和整篇正文。
- 日志包含 event、request_id、kb_id/document_id、duration、status。
- HTTP 客户端、文件流、DB Session 正确关闭；CPU/阻塞解析不长期占用事件循环。
- 处理中重启后任务可恢复或安全失败并可重试。
- 知识库/文档删除对 SQL、文件、向量执行一致清理。

### PASS 条件

安全/恢复/日志测试、ruff、mypy 全部退出 0；脱敏抽查无敏感值；无 P0/P1 后端问题。

### 证据登记

- 状态：`NOT_RUN`
- pytest/ruff/mypy：
- 错误响应样例：
- 日志字段样例：
- 脱敏搜索：
- 重启恢复：
- 阻塞：

---

## P10 Gate：前端基础/Dashboard/知识库

关联需求：DASH-01、KB-01、KB-02、UI-01–03、TEST-03。

### 必须执行

~~~powershell
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test:unit
npm --prefix frontend run build
npm --prefix frontend run test:e2e -- --grep "@p10"
~~~

### 必须核对

- Sidebar、路由、Dashboard、知识库列表/详情、创建/编辑/删除正常。
- Empty、Loading、Error、Toast、确认 Modal 均可触发。
- 统计和最近列表与 API 一致；刷新深链接不 404。
- 1440×900 与 1366×768 无横向溢出、遮挡、廉价渐变、超大标题或大量 Emoji。
- 浏览器 Console 无未处理异常；Network 无循环/重复请求。

### PASS 条件

五类命令全部退出 0；E2E 收集数大于 0；两种分辨率有脱敏截图；无明显视觉/控制台错误。

### 证据登记

- 状态：`NOT_RUN`
- lint/typecheck/unit/build/e2e：
- 1440×900 截图：
- 1366×768 截图：
- Console/Network：
- 阻塞：

---

## P11 Gate：文档管理前端

关联需求：DOC-02、DOC-05、DOC-12、UI-01–03、TEST-03。

### 必须执行

~~~powershell
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test:unit
npm --prefix frontend run build
npm --prefix frontend run test:e2e -- --grep "@p11"
~~~

### 必须核对

- 拖拽和文件选择均可上传，上传字节进度与解析阶段状态分开显示。
- ready/failed/processing 状态视觉明确；失败原因可读且可重处理。
- 重复、空、超限、不支持格式有准确 Toast/页面错误，不静默失败。
- 删除有确认并刷新文档数/Chunk 数；轮询在完成、失败和离开页面时停止。
- 无定时器泄漏、重复提交或组件卸载后的状态更新错误。

### PASS 条件

命令全部退出 0；E2E 覆盖成功上传、失败、重试、重复和删除；UI 与后端事实一致。

### 证据登记

- 状态：`NOT_RUN`
- 自动化命令：
- 上传进度/解析状态截图：
- 失败与重试证据：
- 删除/统计证据：
- Console/Network：
- 阻塞：

---

## P12 Gate：Chat/Citation/Settings 前端

关联需求：CIT-01–03、CHAT-01–03、SET-01–03、UI-01–03、TEST-03。

### 必须执行

~~~powershell
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test:unit
npm --prefix frontend run build
npm --prefix frontend run test:e2e -- --grep "@p12"
~~~

### 必须核对

- 新会话、选择知识库、提问、Loading、回答、Error、历史切换和删除均可用。
- 点击 `[S1]...[Sn]` 后显示的名称、页码/章节、excerpt 与 API source 完全一致。
- 无可靠结果显示明确拒答且无虚假引用。
- Settings 校验、保存、刷新、生效分类和重建提示正确。
- 页面永不显示明文 API Key，只显示已配置状态。
- 若启用 Markdown，恶意 HTML/脚本不能执行。

### PASS 条件

命令全部退出 0；E2E 至少覆盖有引用回答、拒答、历史、删除和 Settings；引用做原文人工对照。

### 证据登记

- 状态：`NOT_RUN`
- 自动化命令：
- Chat 有来源回答：
- 引用点击/原文对照：
- 拒答：
- Settings/密钥边界：
- 阻塞：

---

## P13 Gate：Demo/Docker/README

关联需求：ARC-02、DEMO-01、DEMO-02、DOCKER-01、DOCKER-02、README-01。

### 必须执行

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/seed-demo.ps1
powershell -ExecutionPolicy Bypass -File scripts/seed-demo.ps1
powershell -ExecutionPolicy Bypass -File scripts/smoke-core.ps1 -Provider demo
docker compose config
docker compose build
docker compose up -d --wait
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:3000/api/v1/health"
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:3000/"
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:3000/knowledge-bases/example-deep-link"
docker compose restart backend
docker compose up -d --wait
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:3000/api/v1/health"
docker compose logs --no-color
docker compose down
docker compose up -d --wait
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:3000/api/v1/health"
docker compose down
~~~

### 必须核对

- 清除/不设置真实 API Key 后，Demo 仍能启动、建库、上传、解析、检索、回答和引用。
- 两次 seed 不重复；生产模式不自动 seed；样本无客户品牌和版权风险。
- compose 实际 build/up，不仅做语法检查；从公开前端 3000 端口验证首页、SPA 深链和 `/api/v1/health` 代理。
- SQLite、uploads、vector data 使用 volume，restart 以及不带 `-v` 的 down/up 后数据仍在。
- 镜像上下文不包含 .env、数据库、上传文件、向量数据和 Key。
- README 的全部命令、路径、变量与仓库事实一致；OpenAI-compatible、Ollama、Docker、开发、测试、FAQ、二开均完整。

### PASS 条件

Demo smoke、compose config/build/up/restart/health 全部成功；seed 幂等；README 从干净环境抽查可执行。`docker compose down -v` 不属于验收命令，禁止误删证据数据。

### 证据登记

- 状态：`NOT_RUN`
- seed 两次结果：
- Demo smoke：
- compose config/build/up/restart：
- 数据持久性：
- 镜像/密钥检查：
- README 抽查：
- 阻塞：

---

## P14 Gate：综合验收

关联需求：GOV-02、TEST-01–05、DOCKER-01、UI-03、FINAL-01，以及全部 MUST ID。

### 必须执行

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/bootstrap.ps1
powershell -ExecutionPolicy Bypass -File scripts/test-backend.ps1
powershell -ExecutionPolicy Bypass -File scripts/test-frontend.ps1
powershell -ExecutionPolicy Bypass -File scripts/smoke-core.ps1 -Provider demo
npm --prefix frontend run test:e2e
powershell -ExecutionPolicy Bypass -File scripts/acceptance.ps1
git diff --check
git status --short
~~~

另行实际执行并记录：

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts/start-dev.ps1
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/health"
# 完成建库、四格式上传、解析、Chunk、检索、回答、引用、历史、删除的浏览器验收
powershell -ExecutionPolicy Bypass -File scripts/stop-dev.ps1
~~~

### 必须核对

- 依赖可安装，前后端可启动，数据库可初始化和迁移。
- 四格式可上传/解析；Chunk/向量/检索真实产生；跨库隔离。
- Demo 模式完整闭环；外部 Provider 按现场条件分别标记 live 状态。
- 引用逐条关联正确文档、页码/章节和原文。
- 拒答、失败重试、删除级联、处理中重启、应用重启持久性均实测。
- 前端两种分辨率、Console、Network、Loading/Empty/Error 状态无明显问题。
- 后端全测、前端 lint/typecheck/unit/build/E2E、Docker 均有证据。
- README 与实际命令一致。

### PASS 条件

所有 MUST 项均有实际证据；所有必需命令退出 0；测试收集数大于 0 且无未解释 skip；没有 P0/P1 缺陷。任何核心项 `NOT_RUN`、`FAIL` 或 `BLOCKED` 时，P14 不能 PASS。

### 证据登记

- 状态：`NOT_RUN`
- 后端测试：
- 前端质量与 E2E：
- Demo 核心闭环：
- 浏览器完整闭环：
- 引用对照：
- 失败/拒答/重启：
- Docker：
- Git diff/status：
- 外部 Provider 条件项：
- 已知限制：

---

## P15 Gate：独立 Review/修复/发布审查

关联需求：REVIEW-01、FINAL-01、README-01，以及全部需求回归。

### Review 范围

- 架构边界、循环依赖、重复代码和未实现空壳；
- 明显 Bug、异常映射、输入验证、路径/密钥安全；
- SQL 事务、级联、N+1、SQLite/PostgreSQL 可迁移性；
- async 阻塞、HTTP/File/DB 资源泄漏、重启恢复；
- Embedding 维度、向量过滤、分数方向、索引版本、重处理原子性；
- Prompt 限定、无结果拒答、上下文预算、Prompt Injection；
- Citation 一致性、历史快照、Chat 状态和前端竞态；
- Loading/Empty/Error、可用性、视觉、控制台和网络错误；
- Docker 构建、volume、健康检查、运行时配置、镜像密钥；
- 测试遗漏、无断言测试、过度 Mock、skip 和不稳定测试；
- README、环境变量、命令和真实验证状态。

### 必须执行

~~~powershell
git diff --check
git status --short
git diff --stat
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m mypy backend\app
powershell -ExecutionPolicy Bypass -File scripts/test-backend.ps1
powershell -ExecutionPolicy Bypass -File scripts/test-frontend.ps1
npm --prefix frontend run test:e2e
powershell -ExecutionPolicy Bypass -File scripts/acceptance.ps1
docker compose config
~~~

### 必须产出

- 独立 Review 清单：编号、严重度 P0–P3、文件/行、问题、影响、修复或接受理由、复验命令。
- P0/P1 必须修复；P2 若延期必须记录风险、缓解和后续任务；P3 可列建议。
- 修复后重新执行 P14，不得复用修复前日志。
- 最终 10 项交付总结：
  1. 已完成功能；
  2. 目录结构；
  3. 技术架构；
  4. 启动方式；
  5. OpenAI-compatible 配置；
  6. Ollama 配置；
  7. 测试结果；
  8. 当前限制；
  9. 下一阶段最值得增加的功能；
  10. 可直接复用模块。

### PASS 条件

Review 有具体证据；P0/P1 为 0；修复后 P14 重新 PASS；最终总结不夸大 Mock、未运行或外部阻塞；发布结论明确。

### 证据登记

- 状态：`NOT_RUN`
- Review 报告：
- P0/P1/P2/P3 数量：
- 已修复项：
- 修复后 P14 证据：
- 全量命令结果：
- 最终限制和条件项：
- 发布结论：

## 5. 发布阻断条件

出现任一项即禁止发布为“可交付 MVP”：

1. 核心闭环任一阶段是接口空壳或固定答案；
2. 引用不能映射到实际 Chunk、文档和页码/章节；
3. 无结果仍生成无依据回答；
4. 跨知识库检索泄漏；
5. 删除/重处理留下可检索孤儿向量或文件；
6. 普通 API、日志、前端或镜像泄露明文 Key；
7. 四种必需格式存在未解释的未验证项；
8. 后端测试、前端 build/E2E 或 Docker 实启未运行；
9. 重启后数据或向量丢失；
10. P0/P1 Review 问题未修复；
11. README 命令与实际项目不一致；
12. 把 Mock、契约测试或推测写成真实 Provider 已验证。

## 6. 最终验收总表

本表是最终报告字段模板，不在本文维护动态值。P15 应把逐项实际状态和证据写入 `EXECUTION_STATE.md`，并据此生成最终交付摘要。

| 验收项 | 状态 | Gate | 证据链接/命令 | 限制 |
|---|---|---|---|---|
| 安装依赖 | NOT_RUN | P01/P14 |  |  |
| 启动后端 | NOT_RUN | P01/P14 |  |  |
| 启动前端 | NOT_RUN | P01/P14 |  |  |
| 初始化/迁移数据库 | NOT_RUN | P02/P14 |  |  |
| 知识库 CRUD | NOT_RUN | P03/P14 |  |  |
| 四格式上传与解析 | NOT_RUN | P04/P05/P14 |  |  |
| Chunk 与来源元数据 | NOT_RUN | P05/P14 |  |  |
| Embedding/向量持久化 | NOT_RUN | P07/P14 |  |  |
| Retrieval 与跨库隔离 | NOT_RUN | P07/P14 |  |  |
| Demo 完整 RAG | NOT_RUN | P08/P13/P14 |  |  |
| 无结果拒答 | NOT_RUN | P08/P14 |  |  |
| Citation 正确性 | NOT_RUN | P08/P12/P14 |  |  |
| Chat 历史与删除 | NOT_RUN | P08/P12/P14 |  |  |
| Settings 与密钥边界 | NOT_RUN | P06/P12/P14 |  |  |
| 前端视觉与状态 | NOT_RUN | P10–P12/P14 |  |  |
| 后端全量测试 | NOT_RUN | P14/P15 |  |  |
| 前端 lint/typecheck/unit/build/E2E | NOT_RUN | P14/P15 |  |  |
| Docker build/up/restart | NOT_RUN | P13/P14 |  |  |
| OpenAI-compatible live | NOT_RUN | P06/P14 |  | 外部条件项 |
| Ollama live | NOT_RUN | P06/P14 |  | 外部条件项 |
| README 干净环境复现 | NOT_RUN | P13/P15 |  |  |
| 独立 Review 与修复后回归 | NOT_RUN | P15 |  |  |
| 发布结论 | NOT_RUN | P15 |  |  |
