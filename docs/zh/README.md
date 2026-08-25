# ashka

## 项目要求

请查看 [pyproject.toml](../../pyproject.toml)。

## 公开接口

优先从 `ashka` 导入下表接口，以获得正确的返回类型。为兼容旧项目，部分 dishka
接口会 monkey patch；使用它们时必须先导入 `ashka`。这只是迁移辅助机制，应逐步
将 dishka 导入改为 ashka 导入，而不是长期依赖 monkey patch。

| 接口 | 说明 |
| --- | --- |
| `dishka.integrations.*.setup_dishka` | 会 monkey patch |
| `ashka.activate` | 需要从 `ashka` 导入 |
| `ashka.integrations.setup_dishka` | 需要从 `ashka` 导入 |
| `ashka.integrations.get_container` | 需要从 `ashka` 导入 |
| `ashka.integrations.<framework>.get_container` | 需要从 `ashka` 导入 |
| `ashka.integrations.faststream.setup_dishka` | 需要从 `ashka.integrations.faststream` 导入；导入后会触发 monkey patch |
| `ashka.integrations.faststream.get_container` | 需要从 `ashka.integrations.faststream` 导入 |
| `dishka.**.make_container` | 会 monkey patch；需要安装 `ashka[lifecycle]` |
| `dishka.**.make_async_container` | 会 monkey patch；需要安装 `ashka[lifecycle]` |
| `ashka.AshkaScope` | 需要从 `ashka` 导入；需要安装 `ashka[lifecycle]` |
| `ashka.provide` | 需要从 `ashka` 导入；需要安装 `ashka[lifecycle]` |
| `ashka.lifespan` | 需要从 `ashka` 导入；需要安装 `ashka[lifecycle]` |
| `ashka.async_lifespan` | 需要从 `ashka` 导入；需要安装 `ashka[lifecycle]` |

`ashka.container.ContainerType` 和 `ashka.async_container.AsyncContainerType`
不是承诺的公开 API，仅可用于类型标注，不可用于运行时判断。对实际容器使用
`isinstance(container, ContainerType)`、
`isinstance(container, AsyncContainerType)`、
`issubclass(type(container), ContainerType)` 或
`issubclass(type(container), AsyncContainerType)` 一律返回 `False`。

## 功能

- [通过 activate 对抗延迟导入](features/activate.md)
- [获取集成容器](features/integration-container-access.md)
- [按类型分派集成](features/type-dispatched-integrations.md)
- [Bootstrap 生命周期](features/bootstrap-lifecycle.md)（需要安装 `ashka[lifecycle]`）
- [通用 Lifespan](features/lifespan.md)（需要安装 `ashka[lifecycle]`）

## 支持状态

- [FastStream 支持](support/faststream.md)