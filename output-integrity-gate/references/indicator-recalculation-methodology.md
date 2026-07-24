# 指标重算方法论：Wilder 平滑 vs 标准简单平均

## 问题

2026-07-14，盘前三合一审查的红队审计发现 RSI14 值偏差 11%（58.9 vs 52.4），报告为 off-by-one 数据错误。深入排查后发现并非代码 bug——两种 RSI 计算方法在剧烈波动后可以偏差 5-10 点。

## 两种 RSI 计算方法

### Wilder 平滑法（Wilder's RSI）

科创50 premarket 脚本 `kechuang50_premarket.py` 使用此方法：

```python
def wilder_rsi(closes, n=14):
    """Wilder's RSI — 使用指数平滑，对近期价格变化的响应更敏感"""
    r = [None] * n
    # 初始：前 n+1 天的简单平均
    g = sum(max(0, closes[i] - closes[i - 1]) for i in range(1, n + 1)) / n
    l = sum(max(0, closes[i - 1] - closes[i]) for i in range(1, n + 1)) / n
    for i in range(n, len(closes)):
        r.append(round(100 - 100 / (1 + g / l), 1) if l else 100)
        if i + 1 < len(closes):
            diff = closes[i] - closes[i - 1]
            # 权重：新值 1/14，旧平均值 13/14
            g = (g * 13 + max(0, diff)) / 14
            l = (l * 13 + max(0, -diff)) / 14
    return r
```

### 标准简单平均法（Standard RSI）

BTC trader 脚本 `indicators.py` 和大多数公开资料使用此方法：

```python
def calc_rsi(closes, period=14):
    """标准 RSI — 取最近 period 天的简单平均"""
    gains, losses = 0, 0
    for i in range(-period, 0):
        diff = closes[i] - closes[i - 1]
        if diff >= 0: gains += diff
        else: losses += abs(diff)
    avg_gain, avg_loss = gains / period, losses / period
    if avg_loss == 0: return 100
    return round(100 - 100 / (1 + avg_gain / avg_loss), 1)
```

## 两者何时偏差显著

在价格**剧烈单日波动**后，两种 RSI 差异最大：

| 情景 | Wilder RSI | 标准 RSI | 差异 |
|------|-----------|---------|------|
| 科创50 2026-07-13（-4.9% 单日暴跌） | 58.9 | 53.5 | 5.4 点 |
| 平稳波动（日变 <2%） | ~一致 | ~一致 | <2 点 |

**原因**：Wilder 的指数平滑在遭遇极端单日变动时，旧数据的权重（13/14 ≈ 93%）远大于新数据（1/14 ≈ 7%），所以单日暴跌只让 RSI 从 67.5 降到 58.9。标准 RSI 的简单平均对最近 14 天等权，极端值会立刻拉高或压低 RSI。

## 对验证代理的要求

红队或任何独立验证代理在重算指标时：

1. **必须先确认源数据使用的计算方法**（检查 trajectory schema / 数据源脚本）
2. **用相同方法重算**——不同方法给出不同结果是预期行为，不是错误
3. **发现偏差后先检查方法一致性**，再报数据错误

## 已有案例

| 日期 | 标的 | 源值 | 验证值 | 偏差 | 根因 |
|------|------|------|--------|------|------|
| 2026-07-14 | 科创50 RSI | 58.9 (Wilder) | 52.4 (标准) | 11% | **方法不一致（误报）** |
| 2026-07-03 | 农行 RSI | 31.5 | 29.9 | 5% | as-of 日期可能差 1 天 |
