# 最终 Code Review 记录

> 本文件在 P15 使用。P15 前保持模板状态，不应预填“无问题”。

## 1. 审查元数据

| 项目 | 值 |
|---|---|
| 审查日期 | NOT_RUN |
| 审查提交 | NOT_RUN |
| 审查者/模型 | NOT_RUN |
| 基线测试 | NOT_RUN |
| Docker 证据 | NOT_RUN |

## 2. 审查范围

- [ ] 架构与依赖方向
- [ ] API 与错误契约
- [ ] SQLAlchemy、迁移、事务与级联
- [ ] 文件验证、解析、Chunk 和安全
- [ ] Embedding Profile、Chroma 和跨存储一致性
- [ ] RAG、Prompt、拒答和 Citation
- [ ] Provider timeout/retry/资源释放/密钥
- [ ] 前端类型、状态、轮询、缓存和 UX
- [ ] Docker、配置、volume、反向代理
- [ ] 测试完整性、README 和复用边界

## 3. 发现清单

| ID | 严重度（P0/P1/P2/P3） | 状态 | 文件/位置 | 影响与复现 | 修复任务 | 验证证据 |
|---|---|---|---|---|---|---|
| — | — | NOT_RUN | — | P15 执行时填写 | — | — |

状态只允许：`OPEN`、`FIXING`、`CLOSED`、`ACCEPTED_RISK`、`FALSE_POSITIVE`。

## 4. 审查维度记录

### 4.1 架构/API/数据库

`NOT_RUN`

### 4.2 文档处理/安全/资源一致性

`NOT_RUN`

### 4.3 Provider/RAG/Prompt/Citation

`NOT_RUN`

### 4.4 前端状态/类型/可访问性/UX

`NOT_RUN`

### 4.5 Docker/配置/README/复用性

`NOT_RUN`

### 4.6 测试遗漏与声明准确性

`NOT_RUN`

## 5. 修复后全量回归

| 验证项 | 命令或步骤 | 退出码/结果 | 证据位置 |
|---|---|---|---|
| 后端 | NOT_RUN | NOT_RUN | — |
| 前端 | NOT_RUN | NOT_RUN | — |
| E2E | NOT_RUN | NOT_RUN | — |
| Docker | NOT_RUN | NOT_RUN | — |
| 持久性 | NOT_RUN | NOT_RUN | — |
| 密钥扫描 | NOT_RUN | NOT_RUN | — |
| 需求追踪 | NOT_RUN | NOT_RUN | — |

## 6. 发布结论

`NOT_RUN`。只有 P15-T06 的全部发布门满足后，才能改为 `PASS`；否则必须写 `FAIL` 或 `BLOCKED` 及准确原因。
