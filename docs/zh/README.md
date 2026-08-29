# ashka

## 项目要求

请查看 [pyproject.toml](../../pyproject.toml)。

## 安装

安装 `ashka[lifecycle]` 可以启用所有功能，包括 Bootstrap 生命周期支持、
`AshkaScope.BOOTSTRAP`，以及显式初始化或使用上下文管理器初始化容器。此安装方式
会为 dishka 的同步和异步容器添加 `init()`，并扩展上下文进入行为，使依赖可以在
Bootstrap 阶段初始化。

如果不需要 Bootstrap 生命周期支持，可以安装不带 extra 的 `ashka`。这种安装方式
提供受支持的框架集成、统一容器访问和按类型分派的集成配置，但不提供 Bootstrap
生命周期 API。导入 `ashka` 时，它会替换 Dishka 部分框架集成中的
`setup_dishka`，使已有的 Dishka 导入路径也能使用 ashka 扩展后的集成功能。

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
| `ashka.lifespan` | 需要从 `ashka` 导入；安装 `ashka[lifecycle]` 后会自动将 `container.init()` 挂载到 lifespan |
| `ashka.async_lifespan` | 需要从 `ashka` 导入；安装 `ashka[lifecycle]` 后会自动将 `container.init()` 挂载到 lifespan |
| `dishka.provide` | 会 monkey patch；需要安装 `ashka[lifecycle]` |
| `dishka.Container.init` | 通过 monkey patch 添加；需要安装 `ashka[lifecycle]` |
| `dishka.AsyncContainer.init` | 通过 monkey patch 添加；需要安装 `ashka[lifecycle]` |
| `ashka.AshkaScope` | 需要从 `ashka` 导入；需要安装 `ashka[lifecycle]` |

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
- [通用 Lifespan](features/lifespan.md)

## 支持状态

- [FastStream 支持](support/faststream.md)