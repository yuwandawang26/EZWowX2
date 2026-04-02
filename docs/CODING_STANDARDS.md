# EZWowX2 开发规范文档

**文档版本**: 1.0
**创建日期**: 2026-04-02
**最后更新**: 2026-04-02
**适用范围**: EZWowX2 项目组

---

## 1. 文档概述

### 1.1 目的

本文档定义EZWowX2项目的编码规范、命名约定、版本控制标准，确保代码风格统一、可维护性高。

### 1.2 技术栈

| 语言 | 项目 | 规范 |
|-----|------|------|
| Python | EZDriverX2, EZBridgeX2, EZPixelRotationX2 | PEP 8 + pyproject.toml |
| C#/.NET | EZPixelDumperX2.NET | C# Coding Conventions |
| Lua | EZAddonX2, EZPixelAddonX2 | Lua Style Guide |

---

## 2. Python 开发规范

### 2.1 项目结构

```
EZDriverX2/
├── config/
│   ├── defaults.py
│   ├── items.py
│   ├── macros.py
│   └── registry.py
├── contracts/
│   ├── actions.py
│   └── profile.py
├── engine/
│   ├── executor.py
│   └── loop.py
├── input/
│   └── win32_sender.py
├── runtime/
│   ├── context.py
│   ├── data.py
│   └── state_adapter.py
├── transport/
│   └── bridge_client.py
└── ui/
    └── main_window.py
```

### 2.2 命名规范

| 类型 | 规范 | 示例 |
|-----|------|------|
| 模块名 | 小写下划线 | `bridge_client.py` |
| 类名 | CapWords | `RotationLoopEngine` |
| 函数名 | 小写下划线 | `fetch_data()` |
| 方法名 | 小写下划线 | `get_title()` |
| 私有方法 | 小写下划线前缀 | `_internal_method()` |
| 常量 | 全大写下划线 | `MAX_RETRY_COUNT` |
| 变量名 | 小写下划线 | `spell_list` |
| 类型变量 | CapWords | `T`, `TState` |
| 接口类 | I前缀 + CapWords | `ICapture`, `IBridgeClient` |

### 2.3 类型注解

**必需场景**:
- 函数/方法参数和返回值
- 类实例变量（在 `__init__` 中声明）
- 模块级变量（公开API）

**推荐格式**:
```python
from typing import Any, Callable

def fetch_data(url: str, timeout: float = 1.0) -> dict[str, Any] | None:
    ...

class RotationContext:
    def __init__(self, raw_data: dict[str, Any], config: "ConfigRegistry") -> None:
        self._data: dict[str, Any] = raw_data
```

### 2.4 docstring 规范

**公共函数/类**:
```python
def fetch_data(url: str) -> dict[str, Any] | None:
    """从指定URL获取数据。

    Args:
        url: 请求的URL地址

    Returns:
        解析后的JSON数据，失败返回None

    Raises:
        ConnectionError: 网络连接失败
    """
    ...
```

**简单方法**:
```python
@property
def player(self) -> UnitSnapshot:
    """玩家单位快照。"""
    return self._player
```

### 2.5 异常处理

**原则**:
1. 不要使用裸露的 `except Exception`
2. 必须保留异常链 (`raise ... from e`)
3. 记录完整 traceback 信息

**正确示例**:
```python
try:
    result = operation()
except BusinessError as e:
    logger.error(f"业务错误: {e}")
    raise
except Exception as exc:
    logger.error(f"未知错误: {exc}\n{traceback.format_exc()}")
    raise RuntimeError("操作失败") from exc
```

**错误示例**:
```python
try:
    result = operation()
except Exception:
    pass  # 禁止：吞掉异常
```

### 2.6 导入规范

**顺序**:
1. 标准库
2. 第三方库
3. 本项目模块

**每组之间空一行**:
```python
import time
import traceback
from typing import Any

import numpy as np

from ..config.registry import ConfigRegistry
from .actions import CastAction
```

### 2.7 线程安全

**原则**:
- 共享可变状态必须使用锁保护
- 优先使用不可变数据结构
- 显式标注线程安全接口

**示例**:
```python
class ThreadSafeCache:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data: dict[str, Any] = {}
    
    def get(self, key: str) -> Any | None:
        with self._lock:
            return self._data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value
```

### 2.8 数据类

**使用 frozen dataclass**:
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CastAction:
    unitToken: str
    spell: str
```

---

## 3. C# 开发规范

### 3.1 项目结构

```
EZPixelDumperX2.NET/
├── Capture/
│   └── DesktopDuplicatorCapture.cs
├── Core/
│   ├── PixelCore.cs
│   ├── PixelDumpService.cs
│   └── NodeTitleManager.cs
├── UI/
│   ├── MainForm.cs
│   └── IconLibraryForm.cs
├── Web/
│   └── HttpApiServer.cs
└── Program.cs
```

### 3.2 命名规范

| 类型 | 规范 | 示例 |
|-----|------|------|
| 命名空间 | PascalCase | `Dumper.NET.Core` |
| 类名 | PascalCase | `PixelDumpService` |
| 接口名 | I前缀 + PascalCase | `INodeTitleResolver` |
| 方法名 | PascalCase | `GrabFrame()` |
| 私有字段 | 下划线前缀 + PascalCase | `_colorMap` |
| 常量 | PascalCase | `MaxRetryCount` |
| 参数名 | camelCase | `adapterIndex` |
| 属性名 | PascalCase | `Width` |

### 3.3 访问修饰符

| 修饰符 | 用途 |
|-------|------|
| public | 公开API |
| private | 类内部使用 |
| internal | 同程序集可见 |
| protected | 子类可见 |
| sealed | 禁止继承 |

**默认原则**: 优先使用最严格的访问级别

### 3.4 record vs class

**使用 record** (不可变):
```csharp
public readonly record struct PixelFrame(int Width, int Height, byte[] Bgra);
```

**使用 class** (需要方法或可变状态):
```csharp
public sealed class PixelDumpService : IDisposable
```

### 3.5 异常处理

```csharp
try
{
    var result = operation();
}
catch (ArgumentOutOfRangeException ex)
{
    logger.LogError($"参数越界: {ex.ParamName}");
    throw;
}
catch (Exception ex)
{
    logger.LogError(ex, "未知错误");
    throw new InvalidOperationException("操作失败", ex);
}
```

---

## 4. Lua 开发规范

### 4.1 项目结构

```
EZAddonX2/
├── Class/
│   ├── Druid.lua
│   └── Priest.lua
├── Frame/
│   ├── 00Core.lua
│   ├── 01Event.lua
│   └── ...
├── Libs/
│   ├── LibStub/
│   └── LibRangeCheck-3.0/
├── Fonts/
│   └── CustomFont.ttf
├── EZAddonX2.lua
├── EZAddonX2.toc
└── Setting.lua
```

### 4.2 命名规范

| 类型 | 规范 | 示例 |
|-----|------|------|
| 文件名 | PascalCase | `PlayerStatusFrame.lua` |
| 全局变量 | 大写下划线 | `addonName`, `FRAME_UPDATE_RATE` |
| 局部变量 | 小写下划线 | `local player_health` |
| 函数名 | PascalCase | `UpdatePlayerStatus()` |
| 表名 | PascalCase | `COLOR`, `CLASS` |
| 常量 | 大写下划线 | `MAX_AURA_COUNT` |

### 4.3 编码风格

**缩进**: 4空格

**运算符空格**:
```lua
local x = 1 + 2
local y = x * 2 - 1
```

**表定义**:
```lua
local COLOR = {
    RED = CreateColor(1, 0, 0, 1),
    GREEN = CreateColor(0, 1, 0, 1),
    BLUE = CreateColor(0, 0, 1, 1),
}
```

**函数定义**:
```lua
local function UpdateStatus()
    -- function body
end
```

### 4.4 性能优化

**缓存API引用**:
```lua
local CreateFrame = CreateFrame
local UnitHealthPercent = UnitHealthPercent
```

**避免重复查询**:
```lua
local function UpdateFrame()
    local nodeSize = addonTable.nodeSize  -- 缓存
    frame:SetSize(nodeSize * 8, nodeSize * 4)
end
```

---

## 5. 版本控制规范

### 5.1 分支策略

```
main (稳定版本)
  └── develop (开发分支)
        ├── feature/xxx (功能分支)
        ├── bugfix/xxx (修复分支)
        └── release/xxx (发布分支)
```

### 5.2 提交信息格式

**格式**:
```
<类型>(<范围>): <描述>

[可选正文]

[可选尾部]
```

**类型**:
| 类型 | 说明 |
|-----|------|
| feat | 新功能 |
| fix | 修复bug |
| docs | 文档变更 |
| style | 代码格式（不影响功能） |
| refactor | 重构（不影响功能） |
| test | 测试相关 |
| chore | 构建/工具变更 |

**示例**:
```
feat(dumper): 添加模板匹配定位功能

- 使用锚点坐标验证游戏窗口位置
- 支持多显示器环境
- 失败时返回诊断截图

Closes #123
```

### 5.3 文件命名

| 文件类型 | 命名规范 |
|---------|---------|
| 文档 | `PROJECT-doc-name.md` |
| 配置文件 | `*.json`, `*.yaml`, `*.toml` |
| 测试文件 | `test_*.py`, `*Test.cs` |

---

## 6. Git 工作流

### 6.1 功能开发流程

```bash
# 1. 从develop创建功能分支
git checkout develop
git pull
git checkout -b feature/add-new-spell

# 2. 开发并提交
git add .
git commit -m "feat(spell): 添加新法术支持"

# 3. 同步develop
git checkout develop
git pull
git merge feature/add-new-spell

# 4. 删除分支
git branch -d feature/add-new-spell
```

### 6.2 标签管理

```bash
# 创建版本标签
git tag -a v1.0.0 -m "发布版本1.0.0"
git push origin v1.0.0
```

---

## 7. 代码审查清单

### 7.1 Python

- [ ] 导入顺序正确
- [ ] 类型注解完整
- [ ] docstring 存在且正确
- [ ] 无裸露 except Exception
- [ ] 异常链保留
- [ ] 线程安全检查
- [ ] 单元测试覆盖

### 7.2 C#

- [ ] 访问修饰符正确
- [ ] record vs class 选择正确
- [ ] 异常处理规范
- [ ] 命名一致

### 7.3 Lua

- [ ] API缓存
- [ ] 无全局变量泄漏
- [ ] 缩进一致

---

## 8. 附录

### 8.1 Python 配置

**pyproject.toml**:
```toml
[project]
name = "ezdriverx2"
version = "1.0.0"
requires-python = ">=3.12"

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I"]
```

### 8.2 .NET 配置

**Directory.Build.props**:
```xml
<Project>
  <PropertyGroup>
    <LangVersion>latest</LangVersion>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
```

---

**文档修订记录**:

| 版本 | 日期 | 修订内容 |
|-----|------|---------|
| 1.0 | 2026-04-02 | 初始版本 |
