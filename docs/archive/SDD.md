# EZWowX2 系统设计文档 (SDD)

**文档版本**: 1.0
**创建日期**: 2026-04-02
**最后更新**: 2026-04-02
**适用范围**: EZWowX2 项目组

---

## 1. 文档概述

### 1.1 目的

本文档描述EZWowX2项目的系统架构设计，包括模块划分、接口定义、数据流设计和关键技术选型。

### 1.2 架构设计原则

1. **业务连续性优先**: 零停机迁移、功能等价、可回滚能力
2. **模块解耦**: 接口抽象化、依赖注入、策略分离
3. **配置驱动**: 硬编码外置、规则引擎化
4. **容错设计**: 异常分类、重试策略、状态机恢复

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          EZWowX2 架构                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  EZAddonX2  │────▶│ EZPixelAddon │────▶│ EZPixelDump │           │
│  │   (Lua)     │     │     X2       │     │     X2      │           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                                                 │                   │
│                                                 ▼                   │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │ EZAssisted  │────▶│ EZAssisted  │────▶│ EZDriverX2  │           │
│  │     X2      │     │    .NET     │     │   (决策)    │           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                                                 │                   │
│                                                 ▼                   │
│                                    ┌─────────────────────┐          │
│                                    │   执行层 (按键)     │          │
│                                    └─────────────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流架构

```
游戏插件 ──▶ 像素块 ──▶ 截图捕获 ──▶ 图像预处理 ──▶ 节点提取 ──▶ JSON输出
                         │                                         │
                         ▼                                         ▼
              ┌─────────────────────┐                   ┌─────────────────┐
              │   像素块质量验证器   │                   │   HTTP API      │
              │  (遮挡/失真/延迟)   │                   │   (65131端口)   │
              └─────────────────────┘                   └─────────────────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────┐
                                                    │   决策执行引擎  │
                                                    │  (RotationLoop) │
                                                    └─────────────────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────┐
                                                    │   动作执行器    │
                                                    │   (Win32 API)   │
                                                    └─────────────────┘
```

---

## 3. 模块详细设计

### 3.1 像素编码层 (Lua)

#### 3.1.1 EZAddonX2 模块

**文件**: `EZAddonX2/`

**职责**:
- 游戏内UI框架创建
- 事件监听与状态更新
- 像素块渲染

**关键组件**:

| 组件 | 文件 | 职责 |
|-----|------|------|
| MainFrame | 02MainFrame.lua | 主框架创建 |
| Event | 01Event.lua | 事件处理 |
| AuraFrame | 10AuraFrame.lua | 光环序列渲染 |
| SpellFrame | 12SpellFrame.lua | 技能序列渲染 |
| PlayerStatusFrame | 11PlayerStatusFrame.lua | 玩家状态渲染 |

**设计要点**:
- 使用World of Warcraft UI框架
- 事件驱动更新模式
- 支持多个Update频率（标准/低频）

#### 3.1.2 EZPixelAddonX2 模块

**文件**: `EZPixelAddonX2/`

**职责**:
- 高级像素编码协议实现
- 颜色曲线映射
- 法术/光环数据编码

**像素协议格式**:
```
每个8x8像素块编码：
- 主图标区域: 像素块中心6x6
- 脚注区域: 右下角2x2 (IconType)
- 混合节点: 四个2x2子区域
  - 左上: 冷却时间
  - 右上: 可用性
  - 左下: 高度/高亮
  - 右下: 是否已知
```

### 3.2 像素解析层

#### 3.2.1 .NET 实现 (EZPixelDumperX2.NET)

**命名空间**: `Dumper.NET`

**核心组件**:

| 组件 | 文件 | 职责 |
|-----|------|------|
| PixelDumpService | Core/PixelDumpService.cs | 主服务，流程控制 |
| PixelCore | Core/PixelCore.cs | 像素数据结构定义 |
| NodeExtractor | Core/PixelCore.cs | 节点提取逻辑 |
| NodeDataExtractor | Core/PixelCore.cs | 数据组装 |
| DesktopDuplicatorCapture | Capture/DesktopDuplicatorCapture.cs | DXGI桌面复制 |
| HttpApiServer | Web/HttpApiServer.cs | HTTP服务 |
| NodeTitleManager | Core/NodeTitleManager.cs | 图标标题管理 |

**设计要点**:
- 使用Desktop Duplication API捕获屏幕
- 模板匹配定位数据区域
- 像素质量验证（遮挡检测）
- 内存缓存减少GC压力

#### 3.2.2 Python 实现 (EZPixelDumperX2)

**核心模块**:

| 模块 | 文件 | 职责 |
|-----|------|------|
| DumperGUI | src/DumperGUI.py | GUI主界面 |
| Worker | src/Worker.py | 抓帧/API工作线程 |
| Node | src/Node.py | 像素块/节点抽象 |
| NodeExtractorData | src/NodeExtractorData.py | 数据提取器 |
| Database | src/Database.py | SQLite图标库 |

**设计要点**:
- 使用DXCam/Python的屏幕捕获
- NumPy数组处理
- xxhash3哈希计算
- 余弦相似度回退匹配

### 3.3 桥接服务层 (EZBridgeX2)

**文件**: `EZBridgeX2/`

**架构**:
```
EZBridgeX2/
├── core/
│   ├── database.py      # SQLite图标库
│   ├── node.py          # 像素节点抽象
│   └── node_extractor_data.py  # 数据提取
├── ui/
│   ├── main_window.py   # 主窗口
│   └── icon_library/    # 图标库UI
└── workers/
    ├── camera_worker.py     # 摄像头捕获
    ├── info_display_worker.py   # 信息显示
    └── web_server_worker.py # HTTP服务
```

**核心类**:

| 类 | 职责 |
|-----|------|
| IconTitleRepository | 图标标题仓库，支持哈希/相似度匹配 |
| GridCell | 8x8像素网格单元 |
| GridDecoder | 网格解码器 |
| PixelRegion | 像素区域抽象 |

### 3.4 决策执行层 (EZDriverX2)

**文件**: `EZDriverX2/`

**架构**:
```
EZDriverX2/
├── config/
│   ├── defaults.py      # 默认配置
│   ├── items.py         # 配置项定义
│   ├── macros.py        # 宏定义
│   └── registry.py      # 配置注册表
├── contracts/
│   ├── actions.py       # 动作定义
│   └── profile.py       # 策略接口
├── engine/
│   ├── executor.py      # 动作执行器
│   └── loop.py         # 循环引擎
├── input/
│   └── win32_sender.py  # Win32输入发送
├── runtime/
│   ├── context.py       # 决策上下文
│   ├── data.py         # 数据结构
│   └── state_adapter.py # 状态适配
├── transport/
│   └── bridge_client.py # HTTP客户端
└── ui/
    └── main_window.py   # 主窗口
```

**核心组件**:

| 组件 | 文件 | 职责 |
|-----|------|------|
| RotationLoopEngine | engine/loop.py | 主循环调度 |
| ActionExecutor | engine/executor.py | 动作执行 |
| BridgeClient | transport/bridge_client.py | HTTP数据获取 |
| Win32Sender | input/win32_sender.py | 按键发送 |
| RotationContext | runtime/context.py | 决策上下文 |
| ConfigRegistry | config/registry.py | 配置管理 |

**接口定义**:

```python
# 核心接口抽象

class ICapture(Protocol):
    """截图捕获接口"""
    def grab_frame(self, timeout_ms: int) -> PixelFrame | None: ...
    def is_available(self) -> bool: ...

class IBridgeClient(Protocol):
    """数据桥接客户端接口"""
    def fetch(self) -> AttrDict | None: ...
    def set_log_callback(self, callback: Callable[[str], None] | None) -> None: ...

class IInputSender(Protocol):
    """输入发送接口"""
    def send_key_to_window(self, hwnd: int, key: str) -> bool: ...
    def send_mouse_to_window(self, hwnd: int, x: int, y: int) -> bool: ...

class INodeExtractor(Protocol):
    """节点提取器"""
    def node(self, x: int, y: int) -> Node: ...
    def extract_all(self) -> dict[str, object]: ...
```

### 3.5 决策逻辑层 (EZPixelRotationX2)

**文件**: `EZPixelRotationX2/`

**架构**:
```
EZPixelRotationX2/
├── src/
│   ├── EZPixelRotationX2.py    # 主引擎
│   └── PriestDiscipline.py    # 戒律牧实现
└── pyproject.toml
```

**职责**:
- 具体职业循环策略实现
- 技能优先级判断
- 动作生成

---

## 4. 接口设计

### 4.1 HTTP API 接口

#### 4.1.1 数据获取接口

**端点**: `GET /`

**响应**: JSON对象

```json
{
    "timestamp": "2026-04-02 12:00:00",
    "error": null,
    "misc": {...},
    "player": {...},
    "target": {...},
    "focus": {...},
    "party": {...},
    "signal": {...},
    "spec": {...}
}
```

#### 4.1.2 错误响应

```json
{
    "error": "错误描述",
    "details": ["详细错误信息列表"]
}
```

### 4.2 组件接口

#### 4.2.1 RotationProfile 接口

```python
class RotationProfile(ABC):
    @abstractmethod
    def setup(self, config: ConfigRegistry, macros: MacroRegistry) -> None:
        """注册配置项和宏映射"""
    
    @abstractmethod
    def main_rotation(self, ctx: RotationContext) -> Action:
        """返回当前tick的动作"""
```

#### 4.2.2 Action 接口

```python
@dataclass(frozen=True, slots=True)
class CastAction:
    unitToken: str
    spell: str

@dataclass(frozen=True, slots=True)
class IdleAction:
    reason: str

Action = CastAction | IdleAction
```

---

## 5. 数据结构设计

### 5.1 像素帧结构

```python
@dataclass(frozen=True)
class PixelFrame:
    """不可变像素帧"""
    width: int
    height: int
    bgra: bytes  # BGRA格式
    
    def crop(self, bounds: tuple[int, int, int, int]) -> "PixelFrame":
        """返回裁剪后的新帧"""
```

### 5.2 节点数据结构

```python
class Node:
    """8x8像素块节点"""
    full: PixelBlock       # 完整8x8
    middle: PixelBlock     # 中心6x6
    inner: PixelBlock      # 内层4x4
    footnote: PixelBlock   # 右下角2x2
    mix_node: tuple[PixelBlock, ...]  # 四个2x2子区域
```

### 5.3 决策上下文结构

```python
class RotationContext:
    """决策上下文"""
    def __init__(self, raw_data: dict, config: ConfigRegistry): ...
    
    @property
    def player(self) -> UnitSnapshot: ...
    
    @property
    def target(self) -> UnitSnapshot: ...
    
    @property
    def focus(self) -> UnitSnapshot: ...
```

---

## 6. 关键技术选型

### 6.1 截图方案对比

| 方案 | 帧率 | 优点 | 缺点 |
|-----|------|------|------|
| Desktop Duplication API | ~100 FPS | 帧率可控、链路稳定 | 无法抓取被遮挡窗口 |
| Windows.Graphics.Capture | ~160 FPS | 可抓遮挡窗口 | 速度不可控 |
| GDI | ~15 FPS | 实现简单 | 性能不足 |

**选择**: Desktop Duplication API（稳定优先）

### 6.2 图标识别方案

| 方案 | 速度 | 准确率 |
|-----|------|-------|
| 精确哈希匹配 | O(1) | 高 |
| 余弦相似度 | O(n) | 可配置 |
| CNN识别 | 慢 | 高 |

**选择**: xxhash3_64哈希 + 余弦相似度回退

### 6.3 数据库选型

| 方案 | 适用场景 |
|-----|---------|
| SQLite | 本地图标库（已选） |
| Redis | 分布式缓存 |
| PostgreSQL | 结构化存储 |

---

## 7. 异常处理设计

### 7.1 异常分类

```python
class ErrorSeverity(Enum):
    DEBUG = auto()      # 仅调试时记录
    INFO = auto()       # 信息性提示
    WARNING = auto()    # 警告，可恢复
    ERROR = auto()      # 错误，需要关注
    CRITICAL = auto()   # 严重错误，需立即处理

class ErrorCategory(Enum):
    DATA_VALIDATION = "data_validation"
    NETWORK_TIMEOUT = "network_timeout"
    RESOURCE_CAPTURE = "resource_capture"
    BUSINESS_STATE = "business_state"
```

### 7.2 重试策略

```python
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 2.0
    exponential_base: float = 2.0
    jitter: bool = True
```

---

## 8. 配置设计

### 8.1 配置项定义

| 配置键 | 类型 | 范围 | 默认值 | 说明 |
|--------|------|------|--------|------|
| fps | int | 1-30 | 15 | 帧率 |
| interval_jitter | float | 0.0-0.5 | 0.2 | 间隔抖动 |
| spell_queue_window | float | 0.1-0.5 | 0.2 | 技能队列窗口 |

### 8.2 配置写入权限

- GUI事件路径: 可写
- 普通代码路径: 仅读，尝试写入抛异常

---

## 9. 附录

### 9.1 文件结构索引

详见 rebuild.md 附录C

### 9.2 颜色映射

详见 ColorMap.json

---

**文档修订记录**:

| 版本 | 日期 | 修订内容 |
|-----|------|---------|
| 1.0 | 2026-04-02 | 初始版本 |
