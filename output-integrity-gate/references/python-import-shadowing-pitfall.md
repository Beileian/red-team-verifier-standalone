# Python `import sys` 函数内遮蔽陷阱

> 来源：2026-07-31 银行板块轨迹采集 cron 静默失败根因
> 影响：整个银行的盘前管道（红队+反共识+合成）因轨迹缺失而降级为 1/3 路

## 症状

```
UnboundLocalError: cannot access local variable 'sys'
where it is not associated with a value
```

报错在 `if "--dry-run" in sys.argv` 这一行——`sys` 是在文件顶部 `import sys` 引入的，但这行报 `UnboundLocalError`。

## 根因

在 `main()` 函数内部，第 146 行有：

```python
import importlib.util, sys
```

Python 的变量作用域规则：函数内任何对 `sys` 的**赋值或导入**会使 `sys` 成为该函数的**局部变量**，覆盖顶层的 `import sys`。但第 114 行的 `sys.argv` 在 `import sys`（第 146 行）**之前**执行——此时局部 `sys` 尚未绑定任何值，抛出 `UnboundLocalError`。

**这就是为什么 `UnboundLocalError` 而不是 `NameError`**——Python 看到了函数内有一个 `sys` 绑定（第 146 行导入），认为它是局部变量，但访问时还未执行到绑定语句。

## 修复

```python
# 错误：函数内 import sys（已在顶部导入过）
import importlib.util, sys   # ← 这个 sys 遮蔽了全局 sys

# 正确：只导入实际需要的模块
import importlib.util        # ← sys 已在模块顶部 import sys 引入
```

## 教训

1. 函数内添加新依赖时，不要重复 `import sys/os/json` 等已在模块顶部导入的标准库
2. 这个 bug 只在 `sys` 在 `main()` 内被引用**早于** `import sys` 时才触发——极难在本地测试中复现（因为 dry-run 路径可能不经过）
3. 如果要给现有函数加 import，搜索函数内所有对同名模块的引用位置
