# Multi-Response Extraction — 取最后一个 ## Response

来源: 2026-07-27 · IMA导入bug & 合成器审查bug
影响: import_sector_reviews_to_ima.py · synthesize_*.py (4个) · import_kechuang50_review_to_ima.py
根因: `.find("## Response")` 在包含多个 Response 块的 cron 输出文件中永远取第一个

## 问题模式

```
# ❌ 错误：取第一个 ## Response
m = re.search(r'^## Response\s*\n(.*)', text, re.DOTALL)
report = m.group(1)

# ❌ 同样错误
idx = text.find("## Response\n")
report = text[idx + len(marker):]
```

## 为什么第一个 Response 是错的

多模型管线的 cron 输出文件包含多个 `## Response` 块：
```
## Response        ← 红队数据审计的中间输出
...审查发现...

## Response        ← 反共识压力测试的中间输出  
...反共识结论...

## Response        ← 合成器的最终输出 ← 这才是我们要的
📊 科创50盘前审查合成报告...
```

`re.DOTALL` 的 `.*` 贪婪匹配会捕获从第一个 `## Response` 到文件末尾的全部内容。

## 修复模式

```
# ✅ 正确：取最后一个 ## Response
responses = list(re.finditer(r'## Response\s*\n', text))
if responses:
    report = text[responses[-1].end():].strip()
```

`re.finditer` 找到所有匹配 → 取最后一个的 `end()` 位置。

## 影响面扫描

任何消费 cron 输出文件的脚本，如果用了 `find("## Response")` 或 `re.search` 取第一个匹配，都可能受此影响。修复前 grep 所有脚本。

## Gold Test

`test_extract_report.py` TC2 + TC7 覆盖此模式。
