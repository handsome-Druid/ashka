# ashka

## 项目要求

请查看 [pyproject.toml](../../pyproject.toml)。

## 公开接口

### 会 Monkey Patch 的 dishka 接口

应先导入 `ashka`，再导入以下 dishka 接口。导入顺序正确时，ashka 会自动替换或
扩展对应的 dishka 接口：

- `dishka.**.make_container` -> `ashka.**.make_container`
- `dishka.**.make_async_container` -> `ashka.**.make_async_container`
- `dishka.integrations.*.setup_dishka` -> `ashka.integrations.*.setup_dishka`

建议优先从 `ashka` 导入这些接口，以避免 monkey patch 未生效，并获得正确的
返回类型。

这些 monkey patch 保持了与上游 dishka 一致的接口路径，可以降低迁移时的认知负担。
之所以保留这种方式，是为了兼容旧项目：只需优先导入 `ashka`，旧项目就不必立即
修改原有的 dishka 导入。这是一种迁移辅助机制，不是稳定的长期用法；有空时应逐步
将接口从 dishka 手动切换到 ashka，而不是长期依赖 monkey patch。

导入 `ashka` 不会启用 FastStream。显式导入
`ashka.integrations.faststream` 后，才会替换
`dishka.integrations.faststream.setup_dishka` 及其对应版本的实现。

### 必须从 ashka 导入的接口

以下接口不会 monkey patch 到 dishka：

- `ashka.AshkaScope`
- `ashka.provide`
- `ashka.integrations.setup_dishka`
- `ashka.integrations.get_container`
- 每个受支持的 `ashka.integrations.<framework>.get_container`

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