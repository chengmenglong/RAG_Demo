# AI 私有知识库系统：实施总纲

> 文档版本：1.0
> 冻结日期：2026-08-22
> 适用仓库：`RAG_Demo`
> 目标执行模型：Codex Luna（一次只执行一个原子任务）

## 1. 文档目的

本目录不是概念性方案，而是后续实现工作的唯一执行基线。它把原始需求拆成可恢复、可验证、可交接的任务，尽量减少较弱模型在长周期开发中的以下风险：

- 每轮重新选技术栈，导致前后实现不兼容；
- 一次修改过多模块，失败后无法定位；
- 只创建接口或测试文件，却把功能写成“已完成”；
- 用 Mock 结果冒充真实 Provider 已验证；
- 忘记引用、异常路径、删除清理、重处理幂等和密钥边界；
- 聊天上下文丢失后凭记忆猜测进度；
- 未实际运行命令就报告测试、构建或 Docker 已通过。

所有后续代理必须以仓库文件、实际命令退出码和可复核证据为准，不以聊天记忆为准。

## 2. 已确认的仓库基线

2026-08-22 已完成只读盘点：

| 项目 | 已确认事实 | 影响 |
|---|---|---|
| Git | `main` 跟踪 `origin/main`，初始提交为 `66827ca` | 从现有初始仓库继续，不重建 Git 历史 |
| 工作树 | 盘点时无已跟踪修改 | 后续仍须每次重新检查，不能据此假设一直干净 |
| 文件 | 仅有内容为 `# RAG_Demo` 的 `README.md` | 可按全新项目设计，但不能覆盖后来出现的用户改动 |
| Python | 当前命令返回 Python 3.13.5 | 先尝试当前版本；若锁定依赖明确不兼容，再单独记录环境阻塞或改用 3.12 |
| Node/npm | Node 22.19.0、npm 10.9.3 | 前端统一使用 npm 与 `package-lock.json` |
| Docker | 当前未发现 Docker CLI | 不得把 Docker 验收写成已完成；P13 前需安装 Docker Desktop 或获得可运行环境 |
| Windows Python Launcher | 当前未发现 `py` 命令 | PowerShell 文档使用 `python` 或虚拟环境解释器，不依赖 `py -3.x` |
| Git 警告 | 读取用户级 ignore 时出现权限警告 | 目前不阻塞；必须依赖仓库自己的 `.gitignore` |

这些事实只代表上述日期的快照。每个任务开始时仍需执行当前状态检查。

## 3. 最终交付结果

交付物是一个可本地运行、可 Docker 部署、可离线演示、可替换真实模型 Provider 的单用户 Web 应用。最终必须真实跑通：

```text
创建知识库
  → 上传 PDF / DOCX / TXT / Markdown
  → 安全落盘并创建文档记录
  → 提取带页码或章节的文本
  → 清洗与可配置 Chunk
  → 生成 Embedding
  → 写入持久化向量库
  → 在指定知识库内检索
  → 构造受约束 Prompt
  → LLM 或明确标识的 Demo Provider 生成回答
  → 返回并保存可反查的 Citation
  → 前端展示回答、来源和原文片段
```

“真实闭环”允许在没有外部 API Key 时使用确定性 Demo Provider，但 Demo 必须经过正式解析、Chunk、Embedding、向量检索和 Citation 映射，不能用固定问答字典绕过链路。

## 4. MVP 范围与明确非目标

### 4.1 本次必须完成

- Dashboard、知识库、文档、Chat、Settings 五类产品页面；
- 知识库 CRUD、文档四格式上传、状态、失败、重处理、删除；
- 独立文档处理流水线和可配置字符 Chunk；
- 持久化 SQLite、Chroma、本地文件存储；
- Demo、OpenAI-compatible、Ollama Provider；
- Top-K、阈值、资料不足拒答、结构化 Citation；
- 会话历史和 Citation 快照；
- 结构化日志、统一错误、安全校验和补偿清理；
- 后端单元/集成测试、前端测试和生产构建、核心 E2E；
- Dockerfile、Compose、`.env.example`、Demo 数据和完整 README；
- 独立 Code Review、重要问题修复和全量回归。

### 4.2 本次不实现

- 登录、用户系统、RBAC、多租户和第三方登录；
- OCR、扫描 PDF 识别和更多文件格式；
- Redis、Celery/Dramatiq、分布式任务和多 worker 写入；
- SSE/流式回答、Agent、MCP、联网搜索；
- reranker、混合检索、知识图谱；
- 对象存储、PostgreSQL/pgvector 的生产适配器；
- 移动端精细适配、品牌定制和复杂动画。

以上均保留清晰替换边界，但禁止为它们创建大量无实现空壳。由于 MVP 没有认证，它只适合本机或受控内网演示，不能宣称可直接暴露到公网。

## 5. 冻结技术基线

| 层 | 决策 | 理由与边界 |
|---|---|---|
| 前端 | React + TypeScript + Vite + Ant Design | 组件成熟，适合专业 SaaS Demo，避免重复造基础 UI |
| 前端数据 | TanStack Query + Axios | 服务端状态、缓存、轮询和上传进度职责清晰 |
| 路由 | React Router | 页面和深链接明确 |
| 后端 | Python 3.12 基线 + FastAPI + Pydantic Settings | Docker/发布以 3.12 为基线；当前本机 3.13 必须实际验证兼容性 |
| ORM | SQLAlchemy 2 同步模式 + Alembic | 降低异步数据库复杂度，同时保留 PostgreSQL URL 迁移能力 |
| 关系库 | SQLite 默认 | 零外部服务；启用 foreign keys、WAL、busy timeout |
| 向量库 | Chroma `PersistentClient` | 本地持久化、低维护；只允许单进程写入，接口隔离便于后续替换 |
| 文件存储 | 本地持久目录 + `FileStorage` 抽象 | UUID 存储名、相对 storage key，不信任客户端路径 |
| 后台处理 | FastAPI `BackgroundTasks` | 适合单机 MVP；重启恢复能力有限，启动时处理僵尸状态并允许 retry |
| RAG | 自研透明小流水线 | 不引入 LangChain/LlamaIndex，减少隐式行为和供应商绑定 |
| Provider | Demo / OpenAI-compatible / Ollama | 无 Key 可演示，真实服务可配置，协议不暴露厂商 SDK 类型 |
| 测试 | pytest + Vitest/RTL + 最小 Playwright | 覆盖服务、UI 和真实浏览器闭环 |
| 容器 | FastAPI 容器 + Nginx 前端容器 | `/api` 反向代理，持久卷保存 SQLite、uploads、Chroma |

详细决策和禁止变更规则见 `02_ARCHITECTURE_AND_ADRS.md`；接口和数据结构见 `03_API_DATA_CONTRACTS.md`。核心技术决策如需变化，必须先新增 ADR，说明原因、迁移影响和验证计划，不能在业务任务中静默替换。

## 6. 文档导航与唯一信息源

| 文件 | 唯一职责 |
|---|---|
| `README.md` | 实施包入口和最短使用方式 |
| `00_MASTER_PLAN.md` | 范围、阶段顺序、总完成标准 |
| `01_REQUIREMENTS_TRACEABILITY.md` | 原始需求 ID、阶段映射和验收证据 |
| `02_ARCHITECTURE_AND_ADRS.md` | 固定架构、依赖方向、技术取舍 |
| `03_API_DATA_CONTRACTS.md` | 数据模型、状态机、API、错误、Citation 契约 |
| `04_EXECUTION_PROTOCOL.md` | Luna 每轮开始、实现、验证、失败和交接方式 |
| `05_ACCEPTANCE_GATES.md` | 任务门、阶段门、核心闭环门、发布门 |
| `tasks/Pxx.md` | 当前阶段内的原子任务卡；只读当前任务卡即可执行 |
| `EXECUTION_STATE.md` | **唯一任务状态源**，只允许一个 `IN_PROGRESS` |
| `DECISIONS.md` | 执行期新增决定；不得替代正式 ADR |
| `FAILURE_LOG.md` | 阻塞、原始错误、已尝试方案和解除条件 |

如果多个文档表述冲突，优先级为：

1. 用户最新明确指令；
2. `03_API_DATA_CONTRACTS.md` 中的冻结契约；
3. `02_ARCHITECTURE_AND_ADRS.md` 中已接受 ADR；
4. `01_REQUIREMENTS_TRACEABILITY.md`；
5. 当前任务卡；
6. 其他说明性文字。

发现冲突时不得自行挑选方便的版本。先记录到 `DECISIONS.md`，创建修正文档任务；如果会改变产品行为或扩大权限，再请求用户决定。

## 7. 阶段路线图

| 阶段 | 名称 | 核心产物 | 进入条件 | 阶段出口 |
|---|---|---|---|---|
| P00 | 基线与契约冻结 | 本实施包 | 已读取原始需求和仓库 | 文档互相一致，下一任务明确 |
| P01 | 可运行骨架 | FastAPI health、Vite 壳、基本脚本 | P00 通过 | 前后端均能独立启动/构建 |
| P02 | 配置/数据库/迁移基础 | Settings、日志、错误、SQLAlchemy、Alembic、测试 fixture | P01 通过 | 空库迁移和基础测试通过 |
| P03 | 知识库与 Dashboard 后端 | KB CRUD、统计 API | P02 通过 | 成功与负向 API 测试通过 |
| P04 | 文档存储与上传生命周期 | 安全上传、Document 状态、重复检测 | P03 通过 | 四类合法文件可安全排队，非法文件被拒绝 |
| P05 | 文本解析/清洗/Chunk | Parser、Segment、Cleaner、Chunker、Chunk 模型 | P04 通过 | 四类 fixture 生成带来源的稳定 Chunk |
| P06 | Settings 与 Provider | 非敏感设置、三类 Provider、超时映射 | P05 通过 | Demo 可离线，真实适配器合约测试通过 |
| P07 | 向量写入与检索 | Chroma adapter、索引、检索、幂等处理 | P06 通过 | 跨库隔离、阈值、重试与删除一致性通过 |
| P08 | RAG/Citation/Chat 后端 | Prompt、拒答、引用、历史会话 | P07 通过 | 后端无 Key 核心闭环通过 |
| P09 | 后端安全稳定性与日志 | 清理、脱敏、恢复、异常和资源审计 | P08 通过 | 安全负向与全后端回归通过 |
| P10 | 前端基础/Dashboard/知识库 | Layout、API client、Dashboard、KB UI | P09 通过 | 浏览器可管理知识库，状态齐全 |
| P11 | 文档管理前端 | 拖拽、进度、轮询、失败、重新处理、删除 | P10 通过 | 浏览器上传后能看到准确终态 |
| P12 | Chat/Citation/Settings 前端 | Chat 历史、来源 Drawer、设置表单 | P11 通过 | UI 核心闭环和引用点击通过 |
| P13 | Demo/Docker/README | Seed、样本文档、容器、部署文档 | P12 通过 | 无 Key 演示和 Docker 均有实际证据；准确阻塞是诚实状态但不等于 Gate 通过 |
| P14 | 综合验收 | 全量命令、E2E、重启持久性、追踪补证 | P13 通过 | 所有 Must 需求 PASS 或准确 BLOCKED |
| P15 | 独立 Review/修复/发布审查 | 审查清单、修复提交、最终回归、交付摘要 | P14 通过 | 重要问题已修且全量门再次通过 |

阶段严格顺序推进。阶段内任务可按任务卡依赖顺序执行；只有明确标为可并行的任务才能并行。

## 8. 阶段依赖图

```text
P00 契约
  ↓
P01 骨架 → P02 配置与 DB → P03 KB API → P04 上传
                                           ↓
P05 解析与 Chunk → P06 Provider → P07 向量与检索
                                      ↓
                          P08 RAG、引用、Chat
                                      ↓
                              P09 后端硬化
                                      ↓
                   P10 基础 UI → P11 文档 UI → P12 Chat/设置 UI
                                                        ↓
                                       P13 Demo、Docker、README
                                                        ↓
                                          P14 综合验收 → P15 Review
```

引用不是最后补上的 UI 功能。页码/章节必须从 P05 开始保留，向量 metadata 在 P07 保留，RAG 和历史快照在 P08 固化，P12 只负责忠实展示。

## 9. 全局业务不变量

任何任务都不得破坏以下规则：

1. 同一知识库只使用一个锁定的 Embedding Profile；模型或维度不同的向量不得混查。
2. Citation 的文档名、页码/章节、Chunk ID、原文和分数都来自实际检索结果，而不是让 LLM 猜。
3. PDF 页码对用户始终是 1-based；无可靠页码的格式返回 `null`，不能伪造。
4. 无达到阈值的结果时，不调用真实 LLM，返回固定资料不足响应和空 sources。
5. 同一知识库按 SHA-256 去重；跨知识库允许相同内容。
6. 重处理不得累加旧 Chunk/向量；失败不得留下可被检索的半成品。
7. 删除文档清理文件、当前 Chunk 和向量；历史 Citation 使用快照继续显示并标记源已删除。
8. 删除知识库级联清理当前业务数据与存储，但不得通过不安全的宽路径递归删除。
9. BackgroundTask 只接收 ID，并创建自己的数据库 session；不得复用请求 session。
10. API Key 只从环境变量读取；Settings API 只返回是否已配置，日志和错误不得泄露 Key 或 Authorization。
11. Demo Provider 必须明确标识 Demo，Embedding 跨进程确定性，不能冒充真实语义模型。
12. 上传进度与后台解析进度是两个不同状态，UI 不得混为一条百分比。
13. SQLite + embedded Chroma 只运行一个 Uvicorn worker。
14. 任何完成声明都必须有实际运行证据；Mock/合约测试与 live smoke 分开报告。

## 10. 每阶段统一质量动作

每个阶段至少执行：

1. 读取 `EXECUTION_STATE.md`，确认当前任务；
2. 执行任务卡前置检查；
3. 只实现当前卡，不提前实现后续范围；
4. 运行任务自动验证和一个负向验证；
5. 查看 `git diff --check` 和任务范围内 diff；
6. 更新唯一状态源和证据；
7. 只暂存任务相关文件，创建本地 checkpoint commit；
8. 不自动 push，不创建 PR；
9. 阶段末运行 `05_ACCEPTANCE_GATES.md` 对应 Gate；
10. Gate 失败则创建修复卡，不得把阶段标记完成。

## 11. 全局验证命令基线

以下是目标命令；只有相关文件真实存在后才执行。命令未运行或工具不存在时必须记录 `NOT_RUN` 或 `BLOCKED`，不能写 PASS。

```powershell
# 仓库检查
git status --short --branch
git diff --check

# 后端安装、迁移、测试与静态检查（从仓库根目录）
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
.\.venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
.\.venv\Scripts\python.exe -m pytest backend\tests -q
.\.venv\Scripts\python.exe -m ruff check backend

# 后端启动
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

# 前端
npm --prefix frontend ci
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test:unit
npm --prefix frontend run build

# Docker（当前环境未发现 Docker CLI）
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

如果依赖尚未建立，任务卡应给出该阶段可执行的更小命令，不得为了“看起来完整”运行不存在的命令。

## 12. 完成状态定义

| 状态 | 含义 |
|---|---|
| `NOT_STARTED` | 前置条件未满足或尚未开始 |
| `READY` | 前置条件满足，尚未开始 |
| `IN_PROGRESS` | 当前唯一正在执行的任务 |
| `BLOCKED` | 已记录准确阻塞、尝试和解除条件 |
| `DONE` | 代码、正向/负向验证、diff 检查和证据均完成 |
| `SKIPPED` | 仅用户明确同意移出范围后使用，并记录原因 |

`PARTIAL` 不是完成状态。部分通过的任务保留 `IN_PROGRESS` 或进入 `BLOCKED`。

## 13. 项目最终 Definition of Done

只有同时满足下列条件，项目才可宣布完成：

- P00–P15 的所有 Must 任务为 `DONE`，或有用户批准的 `SKIPPED`；
- 从空数据目录执行迁移成功；
- 后端全量测试和静态检查退出 0；
- 前端 lint、类型检查、测试和 production build 退出 0；
- Demo 模式在无网络、无真实 Key 下完成核心闭环；
- 无关问题返回资料不足且 sources 为空；
- 四种格式至少各有一个真实 fixture 通过解析；
- 重复上传、超限、伪造类型、路径穿越、空文本均有负向证据；
- 文档重处理两次不重复，删除后 SQL/文件/向量一致；
- 重启后 SQLite、原文件、Chroma 和 Chat 历史可用；
- OpenAI-compatible/Ollama 至少完成适配器合约测试；live smoke 若没有条件，明确标为未现场验证；
- 浏览器可完成 Dashboard、建库、上传、状态、问答、点击引用、历史和 Settings；
- Docker Compose 实际启动并 smoke；若当前机器仍无 Docker，只能报告外部环境 `BLOCKED`，不能宣布 Docker 验收完成；
- README 中的命令、端口、变量与实际实现一致；
- 独立 Review 发现的重要问题均有修复和回归证据；
- 最终报告明确已完成功能、结构、架构、启动、Provider 配置、测试结果、限制、下一阶段和可复用模块。

## 14. 下一步使用方式

1. 打开 `EXECUTION_STATE.md` 找到 `NEXT_TASK`；
2. 只把 `04_EXECUTION_PROTOCOL.md`、当前任务卡和该卡列出的冻结文档交给 Luna；
3. 要求 Luna 在修改前先复述目标、非目标、允许文件和完成门；
4. 本轮只完成一张任务卡；
5. 接受结果前检查实际命令、退出码、diff 和状态更新；
6. 然后再开启下一轮，不要让 Luna 一次“自主完成整个项目”。

可复制的启动提示词在 `04_EXECUTION_PROTOCOL.md` 中。具体任务从 `tasks/P01.md` 开始；P00 是本实施包本身的冻结和复核阶段。
