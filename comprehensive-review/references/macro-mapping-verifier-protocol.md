# 宏观映射检验员协议（v1.0 · 2026-07-15）

> 来源：机器人ETF cron `6ea67978ab73`（🌐宏观映射检验）首轮执行总结。Cron 角色由 comprehensive-review 的三路并行架构 §v1.18.0 定义，具体子协议在本文件落地。

## 角色定位

| 维度 | 红队（Flash） | 反共识（Pro） | **宏观映射（M3）** |
|------|------|------|------|
| 关注点 | 数字精确性、区间可复现、归属正确性 | 死因假设、反证、聪明钱方向 | **宏观引用一致性、映射合理性** |
| 数据源 | trajectory + K线重算 | trajectory + 行业搜索 | **trajectory + 宏观数据源（PMI/进出口/产业政策）** |
| 失败模式 | 漏抓数字错误 | 过度发散 | **漏抓宏观信号，引用覆盖率低** |

## 输入契约

读 `~/.hermes/trajectories/{标的}_{YYYYMMDD}.json`，期望字段：

```json
{
  "subject": {"symbol": "562500", "name": "..."},
  "sector": "robotics | semiconductor | banking | power | ...",
  "indicators": {"close_last": ..., "sma5/10/20": ..., "rsi14": ..., "kdj_j": ..., "atr14": ..., "avg_vol_10d": ...},
  "quote": {...}
}
```

## ⛔ 已知陷阱（2026-07-15 · 首轮发现）

**Trajectory 文件通常仅含技术指标，无宏观字段。**

- robot_etf_20260715.json 的实际结构 = `indicators + quote`，无 `macro`、`policy`、`industry`、`external_data` 字段
- 引用覆盖率在 trajectory 维度**理论上是 0%**，因为没有任何宏观可被引用
- 这意味着：宏观映射检验员必须**独立从外部数据源填补宏观拼图**，不能依赖 trajectory 内的"引用"

**不是 bug 而是设计约束**：三路审查的语义分工——红队管数字、反共识管逻辑、宏观管外部一致性。trajectory 不存宏观 = 各司其职。

但这导致**任务定义上的歧义**：用户/cron prompt 说"检查 trajectory 中的宏观判断"，实际上"判断"不在 trajectory 里，而是在三路审查的合成器输出或 IMA 归档里。

## 协议流程（v1.0）

### Step 1 · 读 trajectory，确认 sector
读取 sector 字段（如 "robotics"），决定后续搜索词映射。

### Step 2 · 行业搜索词映射
参见 `parallel-review-architecture.md` 的「行业特定搜索词映射」表。

| sector | 行业搜索 1 | 行业搜索 2 |
|--------|-----------|-----------|
| robotics | 日本机器人企业（发那科/安川）隔夜表现 | 中国工业机器人产量+出口（海关总署/统计局） |

### Step 3 · 必查宏观信号清单（robotics 行业）

按以下顺序从前向后搜索，能填几个填几个：

1. **中国制造业 PMI**（最新月度，国家统计局/财新）
2. **高技术制造业 PMI** / **装备制造业 PMI**（subsector 直接相关）
3. **中国工业机器人产量**（统计局，月度产量与累计同比）
4. **工业自动化核心部件**（机器人减速器、工控系统、伺服电机产量）
5. **机器人进出口数据**（海关总署，月度出口量与同比）
6. **日本制造业 PMI**（au Jibun Bank 终值，关注扩张/收缩方向）
7. **产业政策信号**（工信部/国资委 人形机器人专项、行业标准制定）

### Step 4 · 输出格式（8 行以内）

```\n🌐 {标的}宏观检验 · {YYYY-MM-DD}\n引用一致性: trajectory仅含{技术字段列表},无宏观字段 → 覆盖率0% [引用不足]\n遗漏信号: ①②③④...（逐条标 macro signal + [URL未引]或URL+[一手/转载/观点]）\n综合: 宏观面{强/弱/中}支持{方向}，与trajectory技术面{RSI/均线/ATR判断}{背离/一致}\n【关键URL{类型}】{url} ({数据描述})\n...\n```

硬约束：
- 8 行以内（含分隔结构）
- 任何 PMI/进出口/产业政策数据必须附 URL + [一手]/[转载]/[观点] 标签
- 无 URL 的断言标 [URL未找到]
- 引用覆盖率 <50% → 标"引用不足"

## 与其他 cron 的协同

| 时间 | 事件 | 输出 |
|------|------|------|
| 09:10 | robot_etf_premarket.py → trajectory JSON | trajectory |
| 09:20 | 红队（Flash）独立审计 trajectory | cron output `83d02c135849` |
| 09:20 | 反共识（Pro）压力测试 | cron output `a6d534dc1740` |
| 09:20 | **宏观映射（M3）行业外部一致性** | **cron output `6ea67978ab73`** |
| 09:30 | 合成器三路汇总 | IMA 归档 + 微信推送 |

**关键约束**：宏观映射的输出**必须独立于红队和反共识**——不能在主进程上下文共享推理链。这是三路并行正交性的核心。

## 已发现的盲区（v1.0 待办）

- ☐ trajectory schema 是否应增加 `macro_context` 字段？（需要 P0 vs P1 决策——若加，影响 trajectory-recorder v1.6.0 schema）
- ☐ 行业搜索词映射表是否够用？（目前仅覆盖 4 个 sector，需扩展）
- ☐ 引用覆盖率 <50% 标"引用不足"是软警告还是硬拦截？（与 output-integrity-gate §5 格式标注完整性协调）
- ☐ 宏观映射的输出该不该参与合成器"方向概率"计算？（当前合成器用三路定性结论加权——宏观信号若数字化该用什么权重？）

## 参考链接

- comprehensive-review v1.19.0 · 三路并行审查架构
- output-integrity-gate v1.12.0 · §5 格式标注 + §16 提案底盘检查
- trajectory-recorder v1.5.0 · execution_summary 协议
- comprehensive-review v1.20.0 · 对话场景三路模拟的免责声明格式
