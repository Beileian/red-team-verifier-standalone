# Dual-Source 数据验证框架

> 来源：2026-07-31 四板块盘前管道全面评审 + 科创50 close_last 数据错误追查
> 状态：已落地 `data_verifier.py` + 四板块 premarket 接入

## 背景

科创50 trajectory 的 `close_last=1.776` 实际应为 1.669。根因：凌晨 04:30 时 qt 的 `field[4]`（昨收）还停留在前日的 1.776，而 K 线已正确更新为 1.669。脚本的验证逻辑是"偏差>2%则以 qt 为准"——恰好信了滞后的数据。

## 框架设计

```
primary (K线) + fallback (qt) 双源比较
  │
  ├── 偏差 < tolerance → HIGH, 取 primary
  │
  ├── 偏差 > tolerance → 等 5 秒 → 二次采样 primary
  │     ├── 一致 → RETRY_CONFIRMED / HIGH（fallback 舍去）
  │     └── 不一致 → RETRY_FAILED / LOW（数据在变动中）
  │
  └── 仅 primary → MEDIUM (SINGLE_SOURCE)
      仅 fallback → LOW (FALLBACK_ONLY)
      都不在 → NONE (UNAVAILABLE)
```

## 关键发现：数据源优先级不应基于"语义明确度"

之前的逻辑是"qt 语义更明确（昨收字段），所以优先信任"。但实际情况是：
- qt 的昨收字段在凌晨窗口期间**滞后未更新**
- K 线已包含当日结算数据，更可靠
- 正确的逻辑应该基于"更新时效性"而非"语义明确度"

## 涉及板块

| 板块 | 双源字段 | tolerance |
|------|------|:--:|
| 科创50 | close_last, sox_change_pct | 1%, 2pp |
| 银行 | close_last (×4 银行) | 1% |
| 国电 | close_last | 1% |
| 机器人 | close_last | 1% |

## 相关文件

- `data_verifier.py` — 共享验证模块
- `wcr_search.py` — WeChat2RSS 本地搜索（Firecrawl/ddgs/Jina 全部不可用时的替代方案）
- `kechuang50_premarket.py` v1.10.0 — K 线优先于 qt quote
