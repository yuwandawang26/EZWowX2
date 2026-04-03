# EZWowX2 项目实施计划

**文档版本**: 1.0  
**创建日期**: 2026-04-03  
**基于文档**: [guide.md](../guide.md) v1.1  
**适用范围**: EZWowX2 全部子系统

---

## 1. 项目现状总览

### 1.1 项目定位

EZWowX2 是一个面向魔兽世界 12.0+ 版本的 **非侵入式像素自动化辅助工具**，通过游戏内插件将战斗状态编码为屏幕像素矩阵，由外部程序读取并转换为按键操作。

### 1.2 子系统架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                        游戏内层 (WoW Client)                          │
│                                                                      │
│  ┌─────────────┐    ┌──────────────────────────────────────────┐     │
│  │ EZAddonX2   │    │         EZPixelAddonX2 (主用)            │     │
│  │ (WoW插件)   │    │  像素矩阵编码: 52×18节点, 含血量/Buff/技能 │     │
│  │ 模块化架构   │    │  C_AssistedCombat.GetNextCastSpell()      │     │
│  └──────┬──────┘    └────────────┬─────────────────────────────┘     │
│         │                        │                                    │
│         └────────┬───────────────┘                                    │
│                  │ 屏幕渲染 (GPU)                                      │
└──────────────────┼───────────────────────────────────────────────────┘
                   │ 像素数据
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         外部程序层                                     │
│                                                                      │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │
│  │EZAssistedX2.PY │  │  EZPixelRotation │  │   EZDriverX2        │  │
│  │ (当前活跃版本)  │  │  X2 (独立版)     │  │ (完整驱动引擎)       │  │
│  │ 简化:颜色→按键  │  │ HTTP API+GUI     │  │ 循环引擎+条件判断    │  │
│  └────────┬───────┘  └────────┬────────┘  └──────────┬───────────┘  │
│           │                    │                       │             │
│           ▼                    ▼                       ▼             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  数据采集与桥接层                              │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐    │   │
│  │  │EZBridgeX2   │  │EZPixelDumper │  │EZPixelDumperX2.NET│    │   │
│  │  │(Python桥接) │  │X2(Python版)  │  │(.NET 版本)        │    │   │
│  │  └─────────────┘  └──────────────┘  └───────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.3 各子系统成熟度评估

| 子系统 | 语言 | 成熟度 | 功能完整性 | 当前状态 |
|--------|------|--------|-----------|---------|
| **EZAssistedX2.PY** | Python/PySide6 | ⭐⭐⭐ 可运行 | 30% — 仅支持颜色→按键映射，无条件判断 | ✅ 活跃使用中 |
| **EZDriverX2** | Python | ⭐⭐⭐⭐ 架构完善 | 80% — 循环引擎/条件判断/配置系统齐全，但职业循环为空壳 | 🔄 开发中 |
| **EZPixelAddonX2** | Lua | ⭐⭐⭐⭐⭐ 完善 | 95% — 完整的52×18像素矩阵编码 | ✅ 已完成 |
| **EZAddonX2** | Lua | ⭐⭐⭐⭐ 完善 | 90% — 模块化 WoW 插件框架（替代方案） | ✅ 已完成 |
| **EZBridgeX2** | Python | ⭐⭐⭐ 基础可用 | 60% — NodeExtractor + 图像工具 | 🔧 需整合 |
| **EZPixelDumperX2** | Python/.NET | ⭐⭐⭐ 核心可用 | 70% — NodeExtractorData + Database + ColorMap | 🔧 需整合 |
| **EZPixelRotationX2** | Python | ⭐⭐ 独立原型 | 50% — 自含 RotationEngine + GUI + HTTP API | 🧪 原型阶段 |

---

## 2. 目标需求定义

### 2.1 终极目标

实现一个 **完整的、可条件判断的自动化输出辅助系统**，具备以下能力：

1. **全状态感知**：读取玩家/目标/焦点/队友的血量、蓝量、Buff、Debuff、GCD、施法信息
2. **智能决策**：基于多条件组合（如"血量<75% && 存在某Buff → 施放某技能"）执行策略
3. **安全输入**：通过 SecureActionButtonTemplate + PostMessage 合法释放技能
4. **用户友好**：浮窗UI控制启停、快捷键切换、日志调试、配置持久化

### 2.2 能力差距分析

| 能力需求 | EZAssistedX2.PY (当前) | EZDriverX2 (目标) | 差距 |
|---------|----------------------|-------------------|------|
| 读取推荐技能信号 | ✅ SignalFrame 8灰度节点 | ✅ 同上 | 无差距 |
| 读取玩家血量 | ❌ 未解析 | ✅ PlayerHealth 节点 → percent | **需新增** |
| 识别具体 Buff 名称 | ❌ 仅读RGB值 | ✅ NodeTitleManager 哈希匹配 | **需新增** |
| 条件组合判断 | ❌ 不支持 | ✅ RotationProfile.main_rotation() | **需新增** |
| 按名称施法 | ❌ 只能按颜色发键 | ✅ ctx.cast("愈合") / ctx.idle() | **需新增** |
| 配置参数化 | ❌ 硬编码常量 | ✅ SliderConfig/ComboConfig GUI | **需新增** |
| 多职业支持 | ❌ 单一固定逻辑 | ✅ RotationProfile 子类化 | **需新增** |
| 浮窗 UI | ✅ 完整实现 | ❌ 使用独立 MainWindow | **需合并** |
| 快捷键管理 | ✅ GlobalHotkeyManager | ❌ 无全局热键 | **需移植** |
| 日志系统 | ✅ SmartLogManager | ❌ 简单 callback | **需统一** |

---

## 3. 实施路线图

### Phase 0: 基础对齐（已完成 ✅）

- [x] guide.md 文档与代码实现对齐审查（v1.0→v1.1）
- [x] 9处文档差异修复（颜色编码/UI布局/配置字段等）

### Phase 1: 核心能力升级 — 从"颜色→按键"到"全状态感知+条件决策"

**目标**：让 EZAssistedX2.PY 具备读取完整像素矩阵并进行条件判断的能力。

#### 1.1 引入 NodeExtractor 数据解析层

**现状**：[WorkerThread.run()](EZAssistedX2.PY/EZAssistedX2.py#L235-L254) 只裁剪 12×4 的 SignalFrame 区域并做简单颜色匹配。

**目标**：引入 [NodeExtractor](EZPixelDumperX2/src/NodeExtractorData.py) 解析完整的 52×18 像素矩阵。

```
当前流程:
  dxcam.capture() → find_template_bounds() → crop(12×4) → RGB比较 → KEY_COLOR_MAP → send_hot_key()

目标流程:
  dxcam.capture() → find_template_bounds() → crop(完整矩阵)
       → NodeExtractor.extract_all_data()
       → { player: { status: {unit_health: 68.5}, aura: {buff: {...}} }, target: {...} }
       → 条件判断引擎 → ctx.cast("愈合") 或 ctx.idle()
```

**涉及文件**：
| 操作 | 文件 | 说明 |
|------|------|------|
| 新增 | `EZAssistedX2.PY/node_extractor.py` | 从 EZBridgeX2/EZPixelDumperX2 移植核心提取逻辑 |
| 修改 | `EZAssistedX2.PY/EZAssistedX2.py` | WorkerThread 改用 NodeExtractor 替代简单颜色匹配 |
| 新增 | `EZAssistedX2.PY/title_manager.py` | 从 EZPixelDumperX2 移植 NodeTitleManager（图标哈希→名称） |
| 新增 | `data/icon_db.json` | Buff/Debuff 图标哈希数据库（首次运行时自动构建） |

**关键技术点**：
- [Node.read_aura_sequence()](EZPixelDumperX2/src/Node.py#L278-L347)：读取 Buff/Debuff 序列，返回 AuraInfo 列表
- [NodeTitleManager.get_title()](EZPixelDumperX2/src/Database.py#L101-L130)：通过 xxhash64 + 余弦相似度匹配图标名称
- [extract_all_data()](EZPixelDumperX2/src/NodeExtractorData.py#L33)：一次性提取全部结构化数据

#### 1.2 实现条件决策引擎

**现状**：无任何条件逻辑，纯颜色触发。

**目标**：实现类似 [DruidBalance.main_rotation()](EZDriverX2/DruidBalance.py#L48-L60) 的决策函数接口。

```python
# 目标接口设计
class RotationProfile(ABC):
    @abstractmethod
    def main_rotation(self, ctx: 'RotationContext') -> Action:
        """接收完整游戏状态，返回要执行的动作"""
        ...

class RotationContext:
    @property
    def player(self) -> UnitData: ...      # 玩家状态（血量/蓝量/buff/debuff）
    @property
    def target(self) -> UnitData: ...      # 目标状态
    @property
    def focus(self) -> UnitData: ...       # 焦点状态
    @property
    def party(self) -> list[UnitData]: ... # 队友列表
    
    def cast(self, spell_name: str) -> CastAction: ...
    def idle(self, reason: str) -> IdleAction: ...
```

**示例：用户期望的条件逻辑**
```python
class MyDruidHealer(RotationProfile):
    def main_rotation(self, ctx):
        hp = ctx.player.health_percent          # 从像素还原的血量%
        buffs = ctx.player.buffs               # {"掠食者的迅捷": {...}, ...}
        
        if hp < 75 and "掠食者的迅捷" in buffs:
            return ctx.cast("愈合")            # 通过 SecureActionButton 释放
        
        if hp < 50:
            return ctx.cast("治疗之触")
            
        return ctx.idle("血量充足")
```

**涉及文件**：
| 操作 | 文件 | 说明 |
|------|------|------|
| 新增 | `EZAssistedX2.PY/rotation_engine.py` | 决策引擎核心（可参考 EZDriverX2/engine/loop.py） |
| 新增 | `EZAssistedX2.PY/context.py` | RotationContext 数据封装 |
| 新增 | `EZAssistedX2.PY/actions.py` | CastAction / IdleAction 定义 |
| 新增 | `profiles/my_profile.py` | 用户自定义的职业循环脚本 |
| 修改 | `EZAssistedX2.PY/EZAssistedX2.py` | WorkerThread 调用 rotation_engine 替代直接发送 |

#### 1.3 整合 SecureActionButton 技能释放机制

**现状**：通过 `KEY_COLOR_MAP` 颜色→按键→PostMessage 发送。

**目标**：支持两种模式并存：
- **模式A（保留）**：颜色信号直连按键（适合官方一键宏场景）
- **模式B（新增）**：按技能名称施法，内部查找对应 macro key → PostMessage

```python
# 宏注册表（来自插件的 SetOverrideBindingClick）
MACRO_REGISTRY = {
    "惩击": "SHIFT-NUMPAD1",
    "治疗之触": "SHIFT-NUMPAD2",
    "愈合": "SHIFT-NUMPAD7",
    "回春术": "ALT-NUMPAD3",
    # ... 用户可通过 UI 或 JSON 编辑
}
```

**涉及文件**：
| 操作 | 文件 | 说明 |
|------|------|------|
| 新增 | `EZAssistedX2.PY/macro_registry.py` | 技能名→按键映射管理 |
| 修改 | `EZAssistedX2.PY/settings_manager.py` | 增加 macro_registry 持久化字段 |
| 修改 | 插件端 `macroList` | 确保覆盖用户需要的所有技能 |

---

### Phase 2: 用户体验增强

#### 2.1 浮窗 UI 升级

**目标**：在现有 [floating_window.py](EZAssistedX2.PY/floating_window.py) 基础上增加：

| 新增组件 | 说明 | 参考 |
|---------|------|------|
| 模式选择器 | 颜色模式 / 智能模式 切换 | — |
| 实时状态面板 | 显示当前检测到的血量%/Buff列表 | EZPixelRotationX2 的 log_view |
| 职业配置加载器 | 选择/编辑 .py 循环脚本 | — |
| 参数调节面板 | 动态调整阈值（如自我治疗阈值%） | [SliderConfig](EZPixelRotationX2/src/EZPixelRotationX2.py#L142) |

#### 2.2 配置系统升级

**目标**：从当前的 4 字段 settings.json 扩展为完整配置体系：

```json
{
    "hotkey": "q",
    "window_position": null,
    "window_expanded": false,
    "selected_window": null,
    "mode": "smart",
    "profile": "MyDruidHealer",
    "macros": {
        "愈合": "SHIFT-NUMPAD7",
        "治疗之触": "SHIFT-NUMPAD2"
    },
    "params": {
        "self_heal_threshold": 45.0,
        "fps": 15.0,
        "interval_jitter": 0.2
    }
}
```

---

### Phase 3: 稳定性与质量

#### 3.1 编码规范修复

根据 [guide.md §8.4](../guide.md) 自身定义的规范，修复以下已知违规：

| 违规类型 | 数量 | 涉及文件 | 修复方式 |
|---------|------|---------|---------|
| 裸露 `except:` | 4处 | [EZAssistedX2.py:269](EZAssistedX2.PY/EZAssistedX2.py#L269), [floating_window.py:484](EZAssistedX2.PY/floating_window.py#L484), [window_enumerator.py:35](EZAssistedX2.PY/window_enumerator.py#L35), [generate_icon.py:45](EZAssistedX2.PY/generate_icon.py#L45) | 改为 `except Exception:` |

#### 3.2 错误处理标准化

**目标**：在代码中正式引入附录C描述的错误码体系（或确认放弃该设计）。

建议方案：采用 **结构化错误对象** 替代纯文本字符串：

```python
class ErrorCode(Enum):
    CAPTURE_FAILED = ("E001", "无法抓取屏幕帧")
    TEMPLATE_NOT_FOUND = ("E002", "未找到模板")
    TEMPLATE_SIZE_ERROR = ("E003", "模板大小不正确")
    INIT_TIMEOUT = ("E004", "初始化失败(超时)")
    WINDOW_INVALID = ("E005", "窗口无效/已关闭")
    PERMISSION_DENIED = ("E006", "Win32 API权限不足")

class AppError(Exception):
    def __init__(self, code: ErrorCode, detail: str = "", cause: Exception = None):
        self.code = code
        self.detail = detail
        self.cause = cause
        super().__init__(f"[{code.value[0]}] {code.value[1]}: {detail}")
```

---

## 4. 任务分解与优先级

### P0 — 必须完成（核心功能）

| ID | 任务 | 依赖 | 估计工作量 | 对应 Phase |
|----|------|------|-----------|-----------|
| T1 | 移植 NodeExtractor 到 EZAssistedX2.PY | — | 0.5天 | 1.1 |
| T2 | 实现 RotationContext + 条件决策引擎 | T1 | 1天 | 1.2 |
| T3 | 实现 MacroRegistry + 按名施法 | T2 | 0.5天 | 1.3 |
| T4 | 编写一个可运行的示例职业循环（德鲁伊/牧师） | T3 | 0.5天 | 1.2 |
| T5 | 端到端联调验证（插件→像素→解析→判断→按键→施法） | T1-T4 | 1天 | 1.x |

### P1 — 应当完成（体验提升）

| ID | 任务 | 依赖 | 估计工作量 | 对应 Phase |
|----|------|------|-----------|-----------|
| T6 | 浮窗 UI 增加模式切换和实时状态显示 | T2 | 1天 | 2.1 |
| T7 | 配置系统扩展（macros/params/profile） | T3 | 0.5天 | 2.2 |
| T8 | 裸露 except 修复 | — | 0.5天 | 3.1 |
| T9 | NodeTitleManager 图标数据库初始构建 | T1 | 0.5天 | 1.1 |

### P2 — 可以做（锦上添花）

| ID | 任务 | 依赖 | 估计工作量 | 对应 Phase |
|----|------|------|-----------|-----------|
| T10 | 错误码体系正式落地 | T8 | 0.5天 | 3.2 |
| T11 | 多职业 Profile 模板库 | T4 | 2天 | 2.1 |
| T12 | 性能优化（帧率/延迟 benchmark） | T5 | 1天 | 3.x |
| T13 | 单元测试覆盖核心模块 | T5 | 2天 | 3.x |

---

## 5. 技术决策记录

### ADR-001: 为什么不直接使用 EZDriverX2 作为主程序？

**决策**：在 EZAssistedX2.PY 基础上增量升级，而非替换为 EZDriverX2。

**理由**：
1. **EZAssistedX2.PY 已有完整的浮窗UI、快捷键、日志、设置管理** — 这些是用户体验的核心，重写成本高
2. **EZDriverX2 的循环引擎和配置系统可以独立引入** — 作为 library 被调用，而非作为主程序
3. **风险可控** — 渐进式改造比一次性替换更安全

**方案**：
```
EZAssistedX2.PY (主程序，保留 UI/热键/日志层)
    ├── node_extractor.py     ← 从 EZBridgeX2 移植
    ├── title_manager.py      ← 从 EZPixelDumperX2 移植
    ├── rotation_engine.py    ← 参考 EZDriverX2/engine/loop.py 重写
    ├── context.py            ← 参考 EZDriverX2/runtime/context.py
    ├── actions.py            ← 参考 EZDriverX2/contracts/actions.py
    ├── macro_registry.py     ← 新建
    └── profiles/             ← 用户循环脚本目录
```

### ADR-002: 颜色模式 vs 智能模式 共存策略

**决策**：两种模式共存，用户可在运行时切换。

| 模式 | 触发方式 | 适用场景 |
|------|---------|---------|
| **颜色模式** | SignalFrame 颜色变化 → 直接查表发键 | 官方一键宏推荐跟随，零配置即用 |
| **智能模式** | 完整矩阵解析 → 条件判断 → 按名施法 | 需要自定义策略（保命/治疗/复杂输出） |

**切换机制**：浮窗 UI 新增下拉框，切换后 WorkerThread 使用不同的处理分支。

### ADR-003: 图标识别冷启动问题

**问题**：NodeTitleManager 首次运行时无法识别任何 Buff 名称（数据库为空）。

**解决方案**：
1. **首次运行**：显示"未知Buff(hash=xxxx)"提示，用户可手动标注
2. **渐进学习**：每次标注结果存入 `icon_db.json`，下次自动匹配
3. **社区共享**：提供预置的常用 Buff 图标数据库（德鲁伊/牧师/法师等主流职业）

---

## 6. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| NodeExtractor 移植后像素坐标偏移 | 中 | 高 | 保留原始 SignalFrame 路径作为 fallback；添加坐标校准工具 |
| 图标哈希因 WoW 版本更新失效 | 低 | 中 | 余弦相似度兜底 + 用户重新标注流程 |
| 条件决策引入延迟导致 GCD 丢失 | 中 | 高 | 性能 benchmark；优化热点路径；保持颜色模式作为低延迟选项 |
| 多线程竞争（UI线程 vs 工作线程） | 低 | 高 | 严格遵循 Signal-Slot 机制；共享数据加锁 |

---

## 7. 验收标准

### Phase 1 完成标志

- [ ] 能够从像素矩阵中正确提取玩家血量百分比（误差 < ±2%）
- [ ] 能够识别至少 10 个常见 Buff/Debuff 名称
- [ ] 能够执行 "血量 < X% && 存在某Buff → 施放某技能" 的条件逻辑
- [ ] 通过 SecureActionButtonTemplate 成功释放技能（非动作栏绑定）
- [ ] 颜色模式仍然正常工作（向后兼容）

### 最终验收标志

- [ ] 全部 P0 任务完成并通过端到端测试
- [ ] 至少有 1 个完整的职业循环脚本可正常运行
- [ ] 裸露 except 全部修复
- [ ] guide.md 与代码实现完全一致（v1.2）
