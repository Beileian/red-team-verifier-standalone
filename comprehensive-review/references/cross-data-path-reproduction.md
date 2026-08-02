# 跨数据路径复现陷阱 — 蜂群日报 P1-2 score=0 误判案例

> 2026-08-01 · comprehensive-review 已知陷阱「跨数据路径复现陷阱」的完整实例。
> 评审 cron「蜂群之智每日侦察」(27ea509a21f4) 的「建议动作」段时的误判与纠正。

## 背景

蜂群日报 01:20 运行输出「建议动作」段，其中 P1-2 声称：
> "Sphere 评估显示 `score=0`（stars=44234），Scout 报告显示 13.5——疑似陷阱#27 双行写入的延续"

## 我的误判

第一轮评审时我读 `~/.hermes/cron/output/borg_report_2026-07-31.json`：
- `unimatrix_01_items[0].score = 13.5`（顶层已组装好）
- 结论：「score=0 vs 13.5 无法从现有数据复现——可能来自旧版本或另一条路径」
- 红队判定 P1-2「诊断依据不实需降级为计数审计」❌

## 真相（理解债清理时发现）

读 `borg_sphere.py:457`：
```python
score = candidate.get("score", 0)   # 读顶层字段
```
但 scout 传给 sphere 的候选 dict 结构：
```python
{
    "name": ..., "url": ..., "source": ...,
    "_ass": {"score": 13.5, ...}      # score 在内层 _ass！
}
```
→ `candidate.get("score", 0)` 必然返回 **0**。

**复现验证**（monkeypatch `_quick_assimilate` 捕获传参）：
```
评估: agent-evaluation (score=0, stars=44240)   ← score 实传 0
```
日报诊断完全正确。我第一轮的"无法复现"是因为**验证路径与消费路径不同**。

## 计数不一致的另一个真发现

`borg_scout.py:1152`：`"unimatrix_01_items": [ ... for i in u01[:10] ]` ——JSON 只存 top10。
`borg_scout.py:1123`：`"unimatrix_01": len(u01)` ——summary 用全量。
→ 23 vs 10 是**设计截断**，不是 bug。日报归因为"陷阱#27 双行写入"也偏了，但 score=0 的核心判断是对的。

## 教训（编码到 SKILL.md）

1. 评审"无法复现"结论前：确认评审者的验证路径 = 被审对象的消费路径
   - 展示层（组装好的报告 JSON）≠ 消费层（下游脚本读取的原始 dict）
2. 直接读被审对象消费代码的字段读取逻辑——`.get("score", 0)` 读哪层、默认值是什么
3. monkeypatch/探针实测复现，再下结论
4. cron 日报的诊断基于真实运行数据路径，可能比评审者的静态复现更准——被审对象说"有 bug"时先认真查，不要急于否定

## 修复

```python
# borg_sphere.py:457 修复方案
score = candidate.get("_ass", {}).get("score", candidate.get("score", 0))
```
