# 实施文档入口

这是后续使用 Luna 实现 AI 私有知识库系统的入口页。不要一次把全部文档交给模型，也不要让模型自行选择整个项目的下一步。

## 开始执行

1. 先读 `EXECUTION_STATE.md`，只认其中的 `NEXT_TASK / 下一候选任务`。
2. 再读 `04_EXECUTION_PROTOCOL.md`。
3. 打开该任务所属的 `tasks/Pxx.md`，只执行对应 `Pxx-Txx` 小节。
4. 按任务卡“必读/冻结契约”读取 `02_ARCHITECTURE_AND_ADRS.md` 或 `03_API_DATA_CONTRACTS.md` 的相关部分。
5. 本轮只完成这一张卡；验证、状态和交接完成后再开下一轮。

本实施包生成完成时，动态状态文件给出的下一项是 `P01-T01`。以后始终以 `EXECUTION_STATE.md` 的当前内容为准，不要依赖本句。

## 文档地图

| 文件 | 用途 |
|---|---|
| `00_MASTER_PLAN.md` | 产品范围、固定技术基线、P00–P15 总路线 |
| `01_REQUIREMENTS_TRACEABILITY.md` | 61 个稳定需求 ID 与原始 17 部分映射 |
| `02_ARCHITECTURE_AND_ADRS.md` | 架构、依赖方向、Provider/存储和 ADR |
| `03_API_DATA_CONTRACTS.md` | 模型字段、状态机、环境变量、API、错误和 Citation |
| `04_EXECUTION_PROTOCOL.md` | Luna 每轮如何恢复、修改、验证、提交和交接 |
| `05_ACCEPTANCE_GATES.md` | P00–P15 静态验收命令与证据字段模板 |
| `tasks/P00.md`–`tasks/P15.md` | 97 张原子任务卡 |
| `EXECUTION_STATE.md` | 唯一动态状态和证据源 |
| `DECISIONS.md` | 执行期新决策 |
| `FAILURE_LOG.md` | 失败、尝试和阻塞升级 |
| `FINAL_REVIEW.md` | P15 独立审查模板 |

## 给 Luna 的最短提示词

直接复制 `04_EXECUTION_PROTOCOL.md` 最后一节的提示词。不要在同一轮追加“顺便继续下一步”或“持续做完整阶段”；较弱模型最稳定的工作单位是一张任务卡。

## 验收纪律

- 只有真实命令、退出码和行为证据才算完成。
- Demo、Mock 合约和真实 OpenAI-compatible/Ollama live 是三种不同证据。
- Docker 未安装、外部服务无 Key 等应准确记录 `BLOCKED/NOT_RUN`，不能推测为通过。
- 本地 checkpoint 不自动 push；只暂存当前任务相关文件。

