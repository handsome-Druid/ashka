# FastStream 支持

> [!WARNING]
> 此集成不保证可用性、兼容性或正确性。除非已经针对部署所用的确切依赖版本和
> 应用配置进行充分测试，否则不要在生产环境中使用。

初始化 `ashka` 时不会启用 FastStream 支持。

它也被排除在项目的常规覆盖率目标之外，并且不会由中央 `ashka.integrations`
导入完成注册。

## 上游弃用

上游 `dishka.integrations.faststream` 接口已弃用，并迁移到单独维护的
`dishka-faststream` 包。

## 版本测试

FastStream 需要特定于版本的集成代码。FastStream 0.5、0.6 和 0.7 使用不同的
内部 API，而 `StreamRouter` 等可选集成依赖相互兼容的 FastStream 和 FastAPI
版本。正式支持需要覆盖所有受支持组合的测试矩阵，而本项目目前没有该测试矩阵。

当前实现依赖 FastStream 私有 API。这些 API 可能在没有兼容期的情况下变更，
包括 FastStream 小版本之间的变更。

欢迎贡献所需的版本专项测试。所有受支持组合得到完整覆盖后，FastStream 才能被
纳入受支持的集成。

## 手动导入

实现仍可显式使用，但不会自动导入。需要该集成的应用可以手动启用：

```python
import ashka.integrations.faststream
```

实际使用中发生错误时，请提交 issue，并附上相关 FastStream、FastAPI 和 dishka
版本。维护者会切换到受影响的版本组合来复现并修复问题。