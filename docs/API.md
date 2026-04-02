# EZWowX2 接口文档 (API)

**文档版本**: 1.0
**创建日期**: 2026-04-02
**最后更新**: 2026-04-02
**适用范围**: EZWowX2 项目组

---

## 1. 文档概述

### 1.1 目的

本文档定义EZWowX2项目的所有接口规范，包括HTTP API、内部组件接口及数据格式。

### 1.2 接口分类

| 分类 | 说明 |
|-----|------|
| HTTP API | 像素解析服务对外提供的REST接口 |
| 组件接口 | 各模块间的内部接口定义 |

---

## 2. HTTP API 接口

### 2.1 基础信息

| 属性 | 值 |
|-----|---|
| 基础URL | http://127.0.0.1:65131 |
| 默认端口 | 65131 |
| 协议 | HTTP |
| 响应格式 | JSON |
| 字符编码 | UTF-8 |
| CORS | 支持 (Access-Control-Allow-Origin: *) |

### 2.2 接口端点

#### 2.2.1 获取像素数据

**端点**: `GET /`

**描述**: 获取当前游戏状态的像素解析数据

**请求示例**:
```
GET http://127.0.0.1:65131/
```

**响应示例** (200 OK):
```json
{
    "timestamp": "2026-04-02 12:00:00",
    "misc": {
        "ac": "SpellLink:12345",
        "on_chat": true,
        "is_targeting": false
    },
    "spec": {
        "1": {
            "is_pure": false,
            "title": "12345",
            "hash": "a1b2c3d4e5f6"
        }
    },
    "player": {
        "unitToken": "player",
        "status": {
            "unit_damage_absorbs": 0.0,
            "unit_heal_absorbs": 0.0,
            "unit_health": 85.5,
            "unit_power": 45.2,
            "unit_in_combat": true,
            "unit_in_movement": false,
            "unit_in_vehicle": false,
            "unit_is_empowering": false,
            "unit_cast_icon": null,
            "unit_cast_duration": null,
            "unit_channel_icon": null,
            "unit_channel_duration": null,
            "unit_class": "PRIEST",
            "unit_role": "HEALER",
            "unit_is_dead_or_ghost": false,
            "unit_in_range": true
        },
        "spell_sequence": [
            {
                "title": "12345",
                "remaining": 0.0,
                "height": true,
                "charge": 2,
                "known": true,
                "usable": true
            }
        ],
        "spell": {
            "12345": {
                "title": "12345",
                "remaining": 0.0,
                "height": true,
                "charge": 2,
                "known": true,
                "usable": true
            }
        },
        "aura": {
            "buff_sequence": [],
            "buff": {},
            "debuff_sequence": [],
            "debuff": {}
        }
    },
    "target": {
        "unitToken": "target",
        "status": {
            "exists": true,
            "unit_can_attack": true,
            "unit_is_self": false,
            "unit_is_alive": true,
            "unit_in_combat": true,
            "unit_in_range": true,
            "unit_health": 100.0,
            "unit_cast_icon": null,
            "unit_cast_duration": null,
            "unit_cast_interruptible": null,
            "unit_channel_icon": null,
            "unit_channel_duration": null,
            "unit_channel_interruptible": null
        },
        "aura": {
            "debuff_sequence": [],
            "debuff": {}
        }
    },
    "focus": {
        "unitToken": "focus",
        "status": {
            "exists": false
        },
        "aura": {
            "debuff_sequence": [],
            "debuff": {}
        }
    },
    "party": {
        "party1": {
            "exists": true,
            "unitToken": "party1",
            "status": {
                "unit_in_range": true,
                "unit_health": 80.0,
                "selectd": false,
                "unit_damage_absorbs": 0.0,
                "unit_heal_absorbs": 0.0,
                "unit_class": "DRUID",
                "unit_role": "HEALER"
            },
            "aura": {
                "buff_sequence": [],
                "buff": {},
                "debuff_sequence": [],
                "debuff": {}
            }
        }
    },
    "signal": {
        "1": null
    }
}
```

**错误响应示例** (200 OK with error):
```json
{
    "error": "游戏窗口被遮挡或插件未加载，请检查游戏窗口是否可见",
    "details": [
        "(1,16)应为黑色",
        "(50,1)应为黑色"
    ]
}
```

**错误响应示例** (500 Internal Server Error):
```json
{
    "error": "数据提取失败: 索引超出范围"
}
```

---

## 3. 响应字段说明

### 3.1 顶层字段

| 字段 | 类型 | 说明 |
|-----|------|------|
| timestamp | string | ISO格式时间戳 |
| error | string/null | 错误信息，无错误时为null |
| misc | object | 杂项信息 |
| spec | object | 专精信息 |
| player | object | 玩家单位数据 |
| target | object | 目标单位数据 |
| focus | object | 焦点单位数据 |
| party | object | 队伍成员数据 |
| signal | object | 信号状态 |

### 3.2 status 状态对象

| 字段 | 类型 | 说明 |
|-----|------|------|
| exists | boolean | 单位是否存在 |
| unit_health | float | 生命值百分比 (0-100) |
| unit_power | float | 能量百分比 (0-100) |
| unit_in_combat | boolean | 是否在战斗中 |
| unit_in_movement | boolean | 是否在移动中 |
| unit_in_vehicle | boolean | 是否在载具中 |
| unit_is_empowering | boolean | 是否在引导中 |
| unit_is_dead_or_ghost | boolean | 是否死亡或灵魂状态 |
| unit_in_range | boolean | 是否在范围内 |
| unit_can_attack | boolean | 是否可攻击 (target only) |
| unit_is_self | boolean | 是否是玩家自己 (target/focus only) |
| unit_is_alive | boolean | 是否存活 (target/focus only) |
| unit_cast_icon | string/null | 当前施法图标 |
| unit_cast_duration | float/null | 施法持续时间百分比 |
| unit_channel_icon | string/null | 当前引导图标 |
| unit_channel_duration | float/null | 引导持续时间百分比 |
| unit_class | string | 单位职业 (PLAYER/NONE) |
| unit_role | string | 单位角色 (TANK/DPS/HEALER/NONE) |
| unit_damage_absorbs | float | 伤害吸收值百分比 |
| unit_heal_absorbs | float | 治疗吸收值百分比 |
| selectd | boolean | 是否被选中 (party only) |

### 3.3 spell 法术对象

| 字段 | 类型 | 说明 |
|-----|------|------|
| title | string | 法术图标标题/哈希 |
| remaining | float | 冷却剩余时间（秒） |
| height | boolean | 是否高亮 |
| charge | int | 充能层数 |
| known | boolean | 是否学会 |
| usable | boolean | 是否可用 |

### 3.4 aura 光环对象

| 字段 | 类型 | 说明 |
|-----|------|------|
| buff_sequence | array | 增益序列 |
| buff | object | 增益字典 |
| debuff_sequence | array | 减益序列 |
| debuff | object | 减益字典 |

**单个aura条目**:
| 字段 | 类型 | 说明 |
|-----|------|------|
| title | string | 图标标题 |
| remaining | float | 剩余时间（秒） |
| type | string | 光环类型 (MAGIC/CURSE/DISEASE等) |
| count | int | 层数 |
| forever | boolean | 是否永久 |

---

## 4. 节点坐标映射

### 4.1 玩家区域

| 坐标范围 | 内容 |
|---------|------|
| (2,2)-(37,2) | 技能序列 (36个) |
| (2,5)-(33,5) | 玩家增益 (32个) |
| (2,8)-(9,8) | 玩家减益 (8个) |
| (38,2)-(45,4) | 玩家状态 |
| (38,3) | 伤害吸收条 |
| (38,4) | 治疗吸收条 |

### 4.2 目标/焦点区域

| 坐标范围 | 内容 |
|---------|------|
| (38,6)-(45,7) | 目标状态 |
| (38,7)-(43,7) | 目标施法信息 |
| (38,8)-(45,9) | 焦点状态 |
| (38,9)-(43,9) | 焦点施法信息 |

### 4.3 队伍区域

| 队伍成员 | 存在节点 | 范围节点 | 生命节点 | 职业节点 |
|---------|---------|---------|---------|---------|
| party1 | (10,14) | (11,14) | (12,14) | (10,15) |
| party2 | (22,14) | (23,14) | (24,14) | (22,15) |
| party3 | (34,14) | (35,14) | (36,14) | (34,15) |
| party4 | (46,14) | (47,14) | (48,14) | (46,15) |

### 4.4 锚点区域

| 坐标 | 用途 | 预期状态 |
|-----|------|---------|
| (0,0)-(1,1) | 左上锚点 | 接近黑色 |
| (50,16)-(51,17) | 右下锚点 | 接近黑色 |
| (1,1) | 参考色1 | 纯色 |
| (50,16) | 参考色2 | 纯色，与(1,1)同色 |
| (51,4) | 数据区验证 | 非纯色 |

---

## 5. 错误码

### 5.1 服务级错误

| error字段值 | HTTP状态码 | 说明 |
|------------|-----------|------|
| 游戏窗口被遮挡... | 200 | 锚点验证失败 |
| 相机尚未启动 | 200 | 服务未启动 |
| 已停止 | 200 | 服务已停止 |
| 数据提取失败: ... | 200 | 解析过程异常 |

### 5.2 客户端错误

| 场景 | 说明 |
|-----|------|
| 请求超时 | 请求在超时时间内未完成 |
| 连接被拒绝 | 服务未启动或端口被占用 |
| JSON解析失败 | 响应不是有效JSON |

---

## 6. 组件接口定义

### 6.1 核心接口

#### 6.1.1 ICapture - 截图捕获接口

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ICapture(Protocol):
    """截图捕获接口"""
    
    def grab_frame(self, timeout_ms: int) -> "PixelFrame | None":
        """捕获一帧图像
        
        Args:
            timeout_ms: 超时时间（毫秒）
            
        Returns:
            PixelFrame对象，失败返回None
        """
        ...
    
    def is_available(self) -> bool:
        """检查捕获是否可用
        
        Returns:
            True表示可用，False表示不可用
        """
        ...
```

#### 6.1.2 IBridgeClient - 数据桥接接口

```python
@runtime_checkable
class IBridgeClient(Protocol):
    """数据桥接客户端接口"""
    
    def fetch(self) -> "AttrDict | None":
        """获取游戏数据
        
        Returns:
            AttrDict对象，失败返回None
        """
        ...
    
    def set_log_callback(self, callback: "Callable[[str], None] | None") -> None:
        """设置日志回调
        
        Args:
            callback: 日志回调函数
        """
        ...
```

#### 6.1.3 IInputSender - 输入发送接口

```python
@runtime_checkable
class IInputSender(Protocol):
    """输入发送接口"""
    
    def send_key_to_window(self, hwnd: int, key: str) -> bool:
        """发送按键到窗口
        
        Args:
            hwnd: 窗口句柄
            key: 按键描述符 (如 "CTRL-F1", "SHIFT-NUMPAD1")
            
        Returns:
            True表示成功，False表示失败
        """
        ...
    
    def send_mouse_to_window(self, hwnd: int, x: int, y: int) -> bool:
        """发送鼠标点击到窗口
        
        Args:
            hwnd: 窗口句柄
            x: X坐标
            y: Y坐标
            
        Returns:
            True表示成功，False表示失败
        """
        ...
```

#### 6.1.4 INodeExtractor - 节点提取器接口

```python
@runtime_checkable
class INodeExtractor(Protocol):
    """节点提取器"""
    
    def node(self, x: int, y: int) -> "Node":
        """获取指定坐标的节点
        
        Args:
            x: 节点X坐标
            y: 节点Y坐标
            
        Returns:
            Node对象
            
        Raises:
            ValueError: 坐标超出范围
        """
        ...
    
    def extract_all(self) -> dict[str, object]:
        """提取所有数据
        
        Returns:
            包含所有游戏数据的字典
        """
        ...
```

### 6.2 数据结构

#### 6.2.1 PixelFrame

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PixelFrame:
    """不可变像素帧"""
    width: int
    height: int
    bgra: bytes  # BGRA格式字节数组
    
    def crop(self, bounds: tuple[int, int, int, int]) -> "PixelFrame":
        """裁剪图像
        
        Args:
            bounds: (left, top, right, bottom) 裁剪边界
            
        Returns:
            裁剪后的新PixelFrame
        """
        ...
```

#### 6.2.2 Node

```python
class Node:
    """8x8像素块节点"""
    
    @property
    def full(self) -> PixelBlock:
        """完整8x8区域"""
        ...
    
    @property
    def middle(self) -> PixelBlock:
        """中心6x6区域（用于哈希）"""
        ...
    
    @property
    def inner(self) -> PixelBlock:
        """内层4x4区域"""
        ...
    
    @property
    def footnote(self) -> PixelBlock:
        """右下角2x2区域（图标类型）"""
        ...
    
    @property
    def hash(self) -> str:
        """中间6x6哈希值"""
        ...
    
    @property
    def title(self) -> str:
        """图标标题"""
        ...
    
    @property
    def is_pure(self) -> bool:
        """是否纯色"""
        ...
    
    @property
    def is_black(self) -> bool:
        """是否黑色"""
        ...
    
    @property
    def is_white(self) -> bool:
        """是否白色"""
        ...
```

#### 6.2.3 Action

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CastAction:
    """施法动作"""
    unitToken: str   # 目标单位标识
    spell: str       # 法术名称

@dataclass(frozen=True, slots=True)
class IdleAction:
    """空闲动作"""
    reason: str       # 空闲原因

Action = CastAction | IdleAction
```

#### 6.2.4 RotationContext

```python
class RotationContext:
    """决策上下文"""
    
    @property
    def player(self) -> "UnitSnapshot":
        """玩家单位快照"""
        ...
    
    @property
    def target(self) -> "UnitSnapshot":
        """目标单位快照"""
        ...
    
    @property
    def focus(self) -> "UnitSnapshot":
        """焦点单位快照"""
        ...
    
    @property
    def party1(self) -> "UnitSnapshot":
        """队伍成员1快照"""
        ...
    
    def cfg(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        ...
```

### 6.3 Profile接口

```python
from abc import ABC, abstractmethod

class RotationProfile(ABC):
    """循环策略基类"""
    
    @abstractmethod
    def setup(self, config: "ConfigRegistry", macros: "MacroRegistry") -> None:
        """注册配置项和宏映射
        
        Args:
            config: 配置注册表
            macros: 宏注册表
        """
        ...
    
    @abstractmethod
    def main_rotation(self, ctx: "RotationContext") -> "Action":
        """主循环决策
        
        Args:
            ctx: 决策上下文
            
        Returns:
            Action: 要执行的动作
        """
        ...
```

---

## 7. 配置项接口

### 7.1 ConfigRegistry

```python
class ConfigRegistry:
    """配置注册表"""
    
    def get_or_default(self, key: str, default: Any = None) -> Any:
        """获取配置值，默认值回退"""
        ...
    
    def add(self, config_item: "ConfigItem") -> None:
        """添加配置项"""
        ...
    
    def __iter__(self) -> Iterator:
        """遍历所有配置项"""
        ...
```

### 7.2 配置项类型

```python
@dataclass
class SliderConfig:
    """滑块配置"""
    key: str
    min_value: float
    max_value: float
    step: float
    default_value: float
    description: str = ""

@dataclass
class ComboConfig:
    """下拉配置"""
    key: str
    options: list[str]
    default_index: int
    description: str = ""
```

---

## 8. 附录

### 8.1 按键修饰符

| 修饰符 | 说明 |
|-------|------|
| CTRL | Ctrl键 |
| SHIFT | Shift键 |
| ALT | Alt键 |

### 8.2 按键范围

- NUMPAD0 - NUMPAD9
- F1 - F12 (含F4)

### 8.3 宏映射键格式

```
{target}{spell}
例如: "target惩击", "party1治疗"
```

---

**文档修订记录**:

| 版本 | 日期 | 修订内容 |
|-----|------|---------|
| 1.0 | 2026-04-02 | 初始版本 |
