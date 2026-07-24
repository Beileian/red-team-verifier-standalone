# Cron IMA 入库标题污染（跨上下文串扰）

## 问题

cron job 中通过 LLM 调用 `import_doc` 写入 IMA 知识库时，title 由 LLM 自行推断。当 LLM 的上下文窗口中出现其他报告的标题（如"AI进化论日报"），会将该标题错误地套用到当前文章上——导致 BTC 交易报告的 title 变成"AI进化论日报"，入库到错误的文件夹。

## 根因

LLM 在生成 title 时没有硬约束，会从上下文中提取"看起来像标题"的字符串。两个 cron 的 prompt 都没有显式指定 title 格式。

## 实例

| 日期 | 污染方向 | 表现 |
|------|---------|------|
| 2026-07-15 | AI进化论日报标题 → BTC 报告 | BTC 交易报告在 IMA 中以"AI进化论日报 · 2026-07-15"为标题存储 |
| 更早 | 同上 | 用户报告同样问题 |

## 修复模式

在 cron prompt 的 `import_doc` 调用前加**死约束**：

```
⛔ 标题死约束（不可违反）：
- import_doc 的 title 必须为 "XXX报告 · YYYY-MM-DD"
- 禁止使用任何其他标题
- 禁止从上下文推断标题——此标题是硬编码常量
```

## 防御优先级

1. **脚本硬编码**（最安全）：title 在 Python/Bash 脚本中写死，不经过 LLM
2. **prompt 死约束**（次选）：LLM 调用 import_doc 时，prompt 中显式指定 title 格式 + 禁止推断
3. **去重容错**（兜底）：import 脚本的去重逻辑识别错放文件夹（如 `import_daily_digest_to_ima.py` 第 50 行的 folder 检查）

## 受影响的 cron

| Cron ID | 名称 | 修复状态 |
|------|------|:--:|
| 78c08a885914 | BTC虚拟量化系统 | ✅ 2026-07-15 加 title 死约束 |
| 9951941a58a6 + 9f4f6f4cf22f | AI进化论日报 | ✅ 脚本硬编码 title（第78行） |

## 通用检查清单

新建任何含 `import_doc → add_knowledge` 步骤的 cron 时：
- [ ] title 是脚本硬编码还是 LLM 推断？
- [ ] 如果 LLM 推断 → prompt 是否有死约束？
- [ ] 是否有其他 cron 的标题可能出现在当前上下文窗口中？
- [ ] 去重逻辑是否检查了 folder/路径匹配？
