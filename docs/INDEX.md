# EZWowX2 项目文档索引

**文档版本**: 1.0
**创建日期**: 2026-04-02
**最后更新**: 2026-04-02
**适用范围**: EZWowX2 项目组

---

## 1. 文档概述

本文档为 EZWowX2 项目的文档总索引，提供所有项目文档的导航和关联关系说明。

---

## 2. 文档清单

### 2.1 核心文档

| 文档 | 文件 | 版本 | 说明 |
|-----|------|-----|------|
| 项目需求规格说明书 | [SRS.md](SRS.md) | 1.0 | 功能需求、非功能需求、用户场景、验收标准 |
| 系统设计文档 | [SDD.md](SDD.md) | 1.0 | 架构设计、模块划分、接口定义 |
| 数据库设计文档 | [DBDD.md](DBDD.md) | 1.0 | 数据模型、表结构、字段定义 |
| 接口文档 | [API.md](API.md) | 1.0 | HTTP API、内部接口、数据格式 |
| 开发规范文档 | [CODING_STANDARDS.md](CODING_STANDARDS.md) | 1.0 | 编码标准、命名约定、版本控制 |
| 测试计划文档 | [TEST_PLAN.md](TEST_PLAN.md) | 1.0 | 测试策略、测试用例、环境要求 |

### 2.2 补充文档

| 文档 | 文件 | 说明 |
|-----|------|------|
| 重构文档 | ../rebuild.md | 架构问题分析、重构方案 |
| 像素转储文档 | ../EZPixelDumperX2.md | 像素解析实战经验 |
| 像素旋转文档 | ../EZPixelRotationX2/README.md | Rotation实现说明 |
| 颜色映射文档 | ../EZPixelDumperX2.NET/ColorMap.json | 颜色编码定义 |
| 图标数据库 | ../EZBridgeX2/core/database.py | SQLite图标库实现 |

---

## 3. 文档关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                    EZWowX2 文档架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐                                             │
│  │ SRS (需求)    │──────────────┐                              │
│  └───────────────┘              │                              │
│         │                       ▼                              │
│         │              ┌───────────────┐                       │
│         └─────────────▶│ SDD (设计)    │                       │
│                         └───────┬───────┘                       │
│                                 │                               │
│         ┌───────────────────────┼───────────────────────┐       │
│         │                       │                       │       │
│         ▼                       ▼                       ▼       │
│  ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  │ DBDD (数据库) │      │ API (接口)    │      │ CODING_STD    │ │
│  └───────────────┘      └───────────────┘      │ (开发规范)    │
│                                                  └───────┬───────┘
│                                                          │
│                                                          ▼
│                                                 ┌───────────────┐
│                                                 │ TEST_PLAN     │
│                                                 │ (测试计划)    │
│                                                 └───────────────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 文档依赖关系

### 4.1 SRS 依赖

- **上游**: 无
- **下游**: SDD, TEST_PLAN
- **说明**: SRS是需求输入，其他文档都应基于SRS

### 4.2 SDD 依赖

- **上游**: SRS
- **下游**: API, DBDD, CODING_STANDARDS
- **说明**: SDD细化了系统设计，接口和数据库设计都基于此

### 4.3 DBDD 依赖

- **上游**: SDD
- **下游**: API
- **说明**: 数据库设计基于系统设计

### 4.4 API 依赖

- **上游**: SDD, DBDD
- **下游**: TEST_PLAN
- **说明**: API文档定义了接口规范

### 4.5 CODING_STANDARDS 依赖

- **上游**: SDD
- **下游**: 所有代码实现
- **说明**: 编码规范指导代码编写

### 4.6 TEST_PLAN 依赖

- **上游**: SRS, SDD, API
- **下游**: 无
- **说明**: 测试计划基于需求和接口设计

---

## 5. 快速导航

### 5.1 新成员入门

1. **阅读顺序**: SRS -> SDD -> API -> rebuild.md
2. **目标**: 理解项目架构和核心概念

### 5.2 开发参考

1. **编码规范**: [CODING_STANDARDS.md](CODING_STANDARDS.md)
2. **接口定义**: [API.md](API.md)
3. **数据库结构**: [DBDD.md](DBDD.md)

### 5.3 测试参考

1. **测试策略**: [TEST_PLAN.md](TEST_PLAN.md#2-测试策略)
2. **测试用例**: [TEST_PLAN.md](TEST_PLAN.md#4-单元测试设计)
3. **环境要求**: [TEST_PLAN.md](TEST_PLAN.md#3-测试环境)

### 5.4 重构参考

1. **重构文档**: ../rebuild.md
2. **架构问题**: rebuild.md 第一章
3. **重构方案**: rebuild.md 第三章

---

## 6. 文档维护

### 6.1 版本控制

- 所有文档使用 Markdown 格式
- 版本号格式: 主版本.次版本 (如 1.0)
- 每次重大更新递增版本号

### 6.2 文档责任

| 文档 | 主要维护者 | 审核者 |
|-----|-----------|-------|
| SRS | 产品经理 | 技术负责人 |
| SDD | 架构师 | 开发团队 |
| DBDD | 后端开发 | 架构师 |
| API | 后端开发 | 架构师 |
| CODING_STANDARDS | 所有开发者 | 技术负责人 |
| TEST_PLAN | 测试负责人 | 开发团队 |

### 6.3 更新频率

| 文档 | 更新频率 |
|-----|---------|
| SRS | 需求变更时 |
| SDD | 架构变更时 |
| DBDD | 数据库变更时 |
| API | 接口变更时 |
| CODING_STANDARDS | 编码规范变更时 |
| TEST_PLAN | 测试计划变更时 |

---

## 7. 关键文件索引

### 7.1 核心实现文件

| 模块 | 关键文件 | 说明 |
|-----|---------|------|
| 像素编码 | ../EZPixelAddonX2/EZPixelAddonX2.lua | 游戏内像素协议 |
| 像素解析(.NET) | ../EZPixelDumperX2.NET/Core/PixelCore.cs | 节点提取核心 |
| 像素解析(.NET) | ../EZPixelDumperX2.NET/Core/PixelDumpService.cs | 主服务 |
| 像素解析(Python) | ../EZBridgeX2/EZBridgeX2/core/node.py | Python节点抽象 |
| 决策引擎 | ../EZDriverX2/EZDriverX2/engine/loop.py | 循环调度 |
| 决策引擎 | ../EZDriverX2/EZDriverX2/engine/executor.py | 动作执行 |
| 图标数据库 | ../EZBridgeX2/EZBridgeX2/core/database.py | SQLite图标库 |
| HTTP API | ../EZPixelDumperX2.NET/Web/HttpApiServer.cs | .NET HTTP服务 |

### 7.2 配置文件

| 配置文件 | 说明 |
|---------|------|
| ../EZPixelDumperX2.NET/ColorMap.json | 颜色映射定义 |
| ../EZPixelAddonX2/Setting.lua | 插件设置 |
| ../EZAddonX2/Setting.lua | 基础插件设置 |

---

## 8. 联系方式

如对文档有疑问或建议，请联系:

- 项目负责人: EZWowX2 Team
- 文档管理员: Project Coordinator

---

## 9. 附录

### 9.1 术语表

详见 [SRS.md](SRS.md#13-术语表)

### 9.2 颜色映射

详见 [ColorMap.json](../EZPixelDumperX2.NET/ColorMap.json)

### 9.3 参考资料

- WoW API Documentation
- .NET 8 Documentation
- Python 3.12 Documentation
- pytest Documentation

---

**文档修订记录**:

| 版本 | 日期 | 修订内容 |
|-----|------|---------|
| 1.0 | 2026-04-02 | 初始版本 |
