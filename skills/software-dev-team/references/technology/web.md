# Web、Java 与服务开发

## Java 业务系统

普通业务 Web 可从 JDK 17+、Spring Boot + Spring MVC + MyBatis、Maven 与关系数据库比较起步。数据库按既有运维能力、事务与查询需求选择 MySQL/PostgreSQL，不能未经需求判断引入多个数据库或缓存。

当前官方页面显示 Spring Boot 4.1.2 最低 Java 17，并要求相应 Spring Framework；MyBatis Starter 4.0 对应 Boot 4.0+，3.0 对应 Boot 3.2–3.5。它们是核验快照，具体项目仍须重查，不能把所有版本自由组合。[Boot 要求](https://docs.spring.io/spring-boot/system-requirements.html)、[MyBatis 配套](https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/)。

## 传统 SSM 也是新项目选项

Spring Framework + Spring MVC + MyBatis 不要求使用 Spring Boot。适合有明确容器、配置和维护规范的团队；与 Boot 比较手工配置、运行/部署和升级成本，由需求决定。

明确 Controller / Service / Mapper、DataSource、事务管理、Mapper 扫描、异常映射、校验与认证；确定 WAR 或其他启动方式以及 Servlet 容器兼容性。JDK 17+ 只是基础条件，框架、MyBatis-Spring、Servlet/Jakarta 及容器仍须配套。

MyBatis 官方开发文档可能展示 SNAPSHOT 示例，不能直接用于生产依赖。必须查询实际稳定发布和兼容说明。[MyBatis-Spring](https://mybatis.org/spring/)、[入门配置](https://mybatis.org/spring/getting-started.html)。

## 前端按业务选择

| 场景 | 候选与工具 | 决策重点 |
|---|---|---|
| 内部后台、表单与表格 | Vue + TypeScript + Vite，或 React + TypeScript；组件库按需要选 | 团队经验、组件覆盖、状态/校验、无障碍和长期维护 |
| 公众网站、内容、SEO | Nuxt 或 Next.js 等 SSR/静态生成路线 | 收录、首屏、缓存、服务端权限、托管成本 |
| 已有简单服务端页面 | Spring MVC/模板与现有组件 | 不为局部交互强制重写 SPA |
| API 可用但无 UI 合同 | 先确定 DTO、错误、分页、身份和状态语义 | 不让界面从百分比或 HTTP 200 猜业务成功 |

不预设 Vue 或 React 为所有新项目默认。React 官方建议新应用评估框架；独立 Java API、已有路由与纯客户端约束下应说明采用 Vite/客户端方案的依据。[Vue](https://vuejs.org/guide/introduction.html)、[React](https://react.dev/learn/creating-a-react-app)、[Vite](https://vite.dev/guide/)。

## 微服务与 AI 按需加入

服务确需独立发布/扩缩/隔离后，再评估 Spring Cloud、Spring Cloud Alibaba 的注册配置、网关、限流熔断、消息等能力。严格核对 JDK、Boot、Cloud 发布列车与 Alibaba 配套矩阵，不凭主版本数字猜兼容。

AI/RAG 任务可比较 Java 的 Spring AI 与已有 Python 能力，但先明确数据边界、模型/知识来源、质量评测、成本、超时与失败退路。普通业务执行不因使用 AI 开发而自动引入运行时模型调用。

验证按范围选 JUnit、Mockito、Spring MVC Test、Testcontainers 与真实数据库/API 回读；真实服务启动、鉴权、事务回滚和业务结果分别核验。
