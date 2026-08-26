# 通过 activate 对抗延迟导入

`ashka` 主入口提供 `activate()`。

## 延迟导入

延迟导入会在 `import ashka` 之后推迟 `ashka` 的加载。调用
`ashka.activate()` 会访问延迟模块的属性，并在调用发生时立即加载 `ashka`，
执行 `activate()`：

```python
import ashka

ashka.activate()

from dishka.integrations.fastapi import setup_dishka
```

## 导入排序

非预期的排序规则可能会把相邻的 `dishka` import 放在 `ashka` import 前面。
此时要让 `activate()` 保持为两个 import 之间的独立可执行语句：

```python
import ashka

ashka.activate()

from dishka.integrations.fastapi import setup_dishka
```

`activate()` 不属于 import 语句块，因此排序规则不能把 `dishka` import 移到这次
调用之前。

## 非延迟导入

即使应用不使用延迟导入，也建议显式调用 `activate()`。在这种场景下，该方法
目前不会执行任何操作，但未来可能会逐步把一些注册机制和 monkey patch 机制
迁移到 `activate()` 中。

始终保留这次调用，可以让导入方式兼容未来的变化。

## 当前行为

`activate()` 目前不会触发任何注册或 monkey patch。相关 monkey patch 仍然会在
对应模块首次被主动导入时执行。

因此，如果先导入 `dishka` 并访问了需要由 ashka patch 的接口，再调用
`ashka.activate()`，已经访问的 `dishka` 对象不会被事后 patch。必须在访问需要
接收 ashka patch 的 `dishka` 接口前，调用 `ashka.activate()`。
