# LLM-as-Judge 验证方法论

> 来源：[AntoineF23/vasari](https://github.com/AntoineF23/vasari) — 本地 AI 输出人工评审工具  
> 评估日期：2026-07-12  
> 决策：参考保留（分层萃取），萃取 7 步评估循环 + Cohen's Kappa 验证方法论

## 场景

你用自动化系统（LLM-as-Judge / 规则门禁 / Rubrics 评分）来评估 AI 输出质量。但你从未验证过：**这个自动化 judge 的判断，跟真人的判断，到底有几分一致？**

## 核心理念

> "Shipping an AI feature and eyeballing a few outputs (the 'vibe check') does not tell you if it is good, how it fails, or whether it is improving. Real evaluation is a loop."

Vasari 的 7 步评估循环：

```
1. Load traces   → 加载 AI 系统输出（对话/tool call/RAG 结果）
2. Label         → 人工标注 Pass/Fail
3. Open code     → 在失败样本上打错误标签（如"幻觉数字""忽略约束"）
4. Axial code    → 聚类标签为失败分类体系
5. Build judge   → 每类构建 LLM-as-Judge → 调 prompt
6. Validate      → 对比 judge 判断 vs 人工标注 → 混淆矩阵 + Kappa
7. Ship & iterate → 导出 judge 接入生产，持续迭代
```

## Cohen's Kappa：验证 LLM-as-Judge 的核心指标

问题：两个标注者可能"随机蒙对"很多次。Cohen's Kappa 修正了随机一致性。

```
po (observed agreement)   = Accuracy
pe (chance agreement)     = ((TP+FN)*(TP+FP) + (FN+TN)*(FP+TN)) / N²
kappa                     = (po - pe) / (1 - pe)
```

解读：
- `< 0.4` — 弱一致性，judge 不可信
- `0.4-0.6` — 中等，勉强可用
- `0.6-0.8` — 强一致性，judge 可作为人类替代
- `> 0.8` — 近乎完美

**关键要求**：
- 必须用 **held-out test split**（训练集上调 prompt，测试集上看 Kappa）
- 改变 prompt 后必须**重新验证**（stale metrics = 虚假信心）
- "Fully coded" 复选框标记——未完整标注的负样本不可信

## 为什么 Accuracy 不够

两个标注者对 100 条样本的判断：

|  | Judge YES | Judge NO |
|--|-----------|----------|
| Human YES | 80 | 5 |
| Human NO | 10 | 5 |

Accuracy = 85/100 = 85%。看起来很好。

但：
- pe = (85×90 + 15×10) / 10000 = 0.78
- Kappa = (0.85 - 0.78) / (1 - 0.78) = **0.32**（弱一致性！）

结论：85% 准确率 ≠ 85% 一致性。大部分"正确"是随机蒙对的。

## 何时用

- 你的自动化质量系统（gate/verifier/Rubrics）已经跑了一段时间，但**从未用 human ground truth 验证过**
- 你怀疑某些自动化检查可能误判（假阳性过高 / 假阴性漏过）
- 你在调 LLM-as-Judge 的 prompt，想知道"调对了吗"

## 与 Hermes 现有体系的映射

| Hermes 自动化层 | 被评估者 | Vasari 的角色 |
|---|---|---|
| output-integrity-gate | AI 输出的显性错误 | 验证 gate 规则的假阳性/假阴性率 |
| red-team-verifier | AI 输出的隐性错误 | 验证 verifier 判断与人类判断的一致性 |
| Rubrics 八维评分 | AI 输出的多维质量 | 验证单一维度评分的人类校准 |

## 已知陷阱

- **负样本信任问题**：如果标注者只标注了"有问题"的样本，没标注的默认当"没问题"——这是不可靠的。"Fully coded"标记是必要条件：没打勾的负样本不参与 Kappa 计算
- **Kappa 的边界条件**：当几乎所有样本都是同一类别时（如 99% Pass），pe 接近 1，Kappa 趋近 0——此时不适合用 Kappa
- **迭代中 stale metrics**：改了 prompt 但没重新验证，旧 Kappa 不再有效

## 与 engineering-patterns 其他模式的关联

- 与 `output-integrity-gate` 互补——gate 是规则层，Kappa 验证是元评估层
- 与 `trajectory-recorder` 互补——trajectory 记录预测质量，Kappa 验证自动化评估系统的质量
