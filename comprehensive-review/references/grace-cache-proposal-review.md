# 跨 Agent 技术提案评审实例 — Grace 缓存优化方案

> 2026-07-08 | 评审对象：Grace（OpenClaw agent）的 DeepSeek V4-Pro 缓存命中率优化提案

## 背景

- 用户使用 DeepSeek V4-Pro，日费 ~¥30-33
- Grace 运行在 OpenClaw 框架，配置了 `compaction.mode` 参数
- 用户将 Grace 的提案转发给隐序做独立评审

## 提案内容

- **方案 A**：`compaction.mode: default → auto` — 通过压缩早期对话为摘要，让前缀稳定从而提升缓存命中率
- **方案 B**（表面）：`contextTokens: 896K → 976K` — 增大上下文窗口
- **方案 B**（正文描述）：缓存失效降级 — 当命中率连续 3 轮 < 40% 时，自动切 V4-Flash

## 评审关键发现

### 发现 1：提案摘要与正文不一致（方案 B 二义性）

用户转述的方案 B 是 `contextTokens` 调整，但 Grace 正文中详细解释的方案 B 是"缓存失效降级切 Flash"。两个版本完全不同——评审者不知道哪个是真实提案。

**评审动作**：在 Rubrics 评分中标记为"格式合规性 6 分"——因为方案结构不匹配。

### 发现 2：框架层参数被当作 API 层参数

Grace 将 `compaction.mode` 当作影响 DeepSeek API 缓存的参数来讨论，但 DeepSeek 官方 API 文档（api-docs.deepseek.com/guides/kv_cache）中没有 `compaction.mode`。这应该是 OpenClaw 框架层面的上下文管理参数。

**影响**：Grace 的缓存命中率分析忽略了 DeepSeek API 层的自救机制——"固定 token 间隔持久化"（系统自动在长输入中按固定间隔创建 cache prefix unit）。如果 API 层已经对 system prompt 等稳定前缀做了间隔缓存，那框架层 compaction 的边际收益可能小于预期。

**评审动作**：红队将其标记为致命疑点 #1，反事实追问"如果 OpenClaw 的 compaction 压缩了本该被 API 层间隔持久化捕获的稳定段落，会不会反而降低缓存效率？"

### 发现 3：contextTokens 增大与 compaction 目标自相矛盾

- 方案 A 目标：通过 compaction 让前缀稳定 → 提高命中率
- contextTokens 增大 → 推迟 compaction 触发时机 → 前缀漂移更长 → 降低命中率

两个改动方向相反，Grace 未解释如何协同。

**评审动作**：红队标记为致命疑点 #2。

### 发现 4：费效比缺量化

Grace 用 ¥33/天作为"不改会恶化"的证据，但未给出：
- ¥33 对应多少 token 量
- 命中率恢复到 90% 后预期日费
- compaction 本身的 token 消耗

**评审动作**：蓝队 P1 建议——改配置前先跑一天 `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens` 采集。

## 通用评审模式提炼

### 跨 Agent 提案评审特别检查项

当评审来自另一个 AI agent（而非人类工程师）的技术提案时，额外检查：

1. **提案摘要 vs 正文一致性**：顶部列出的方案和正文详细解释是否一致？AI agent 可能在生成过程中漂移了方案定义
2. **参数层级归属**：提案中的参数属于哪个层（框架/API/OS）？AI agent 可能将框架层参数当作 API 参数讨论
3. **API 层自救机制覆盖**：提案的分析是否考虑了目标 API/系统自身的优化机制？AI agent 可能只分析了框架层可见的变量
4. **方案间矛盾检测**：多个方案是否在同一个维度上朝相反方向用力？

### 验证用数据源

- DeepSeek API 缓存机制：`api-docs.deepseek.com/guides/kv_cache`
- DeepSeek V4 定价：`aipricing.guru/deepseek-pricing`（2026-06 基准）
- 缓存命中率从 API response `usage.prompt_cache_hit_tokens` / `usage.prompt_cache_miss_tokens` 获取

## 评审结论

- **Rubrics 总分**：5.5/10
- **可信度评级**：🟠 C — 方案 A 方向对但需要补充分析后落地；方案 B 需先澄清到底是哪个
- **建议**：只落地方案 A（compaction.mode auto），先验证效果再追加其他改动
