# EZWowX2 测试计划文档

**文档版本**: 1.0
**创建日期**: 2026-04-02
**最后更新**: 2026-04-02
**适用范围**: EZWowX2 项目组

---

## 1. 文档概述

### 1.1 目的

本文档定义EZWowX2项目的测试策略、测试用例设计、测试环境要求及验收标准。

### 1.2 测试范围

| 模块 | 测试类型 | 优先级 |
|-----|---------|-------|
| EZPixelDumperX2 | 单元测试、集成测试 | P0 |
| EZBridgeX2 | 单元测试、集成测试 | P0 |
| EZDriverX2 | 单元测试、集成测试 | P0 |
| EZPixelRotationX2 | 集成测试、E2E测试 | P1 |
| EZPixelAddonX2 | 集成测试 | P1 |

---

## 2. 测试策略

### 2.1 分层测试模型

```
┌─────────────────────────────────────────────────────────┐
│                    金字塔测试模型                        │
│                                                         │
│                        ▲                                │
│                       /│\                               │
│                      / │ \                              │
│                     /  │  \     E2E 测试                │
│                    /   │   \    (关键路径覆盖)           │
│                   /────│────\                           │
│                  /     │     \   集成测试               │
│                 /      │      \  (组件交互)             │
│                /─────── │ ──────\                        │
│               /         │        \  单元测试            │
│              /          │         \ (核心逻辑)          │
│             ▼───────────│─────────▼                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 各级别测试定义

| 级别 | 覆盖率目标 | 执行频率 | 依赖环境 |
|-----|-----------|---------|---------|
| 单元测试 | ≥80% 核心逻辑 | 每次提交 | 本地 |
| 集成测试 | ≥60% 组件交互 | 每日 | CI/CD |
| E2E测试 | 关键路径全覆盖 | 每周/发布前 | 真实环境 |

---

## 3. 测试环境

### 3.1 开发测试环境

| 组件 | 版本要求 |
|-----|---------|
| Python | 3.12+ |
| .NET SDK | 8.0+ |
| Node.js | 20+ (可选) |
| Windows | 10/11 |

### 3.2 硬件要求

| 用途 | 最低要求 | 推荐配置 |
|-----|---------|---------|
| 像素解析 | 4核CPU | 8核CPU |
| 内存 | 8GB | 16GB |
| 显卡 | 集成显卡 | 独立显卡 |
| 显示器 | 1080P | 1440P或更高 |

### 3.3 网络要求

- 本地环回网络 (127.0.0.1)
- 端口 65131 可用

### 3.4 测试数据

| 类型 | 说明 | 数量 |
|-----|------|------|
| 图标样本 | 各类法术图标截图 | 1000+ |
| 像素帧 | 各种游戏状态帧 | 500+ |
| 配置文件 | 不同配置组合 | 10+ |

---

## 4. 单元测试设计

### 4.1 Python 单元测试

#### 4.1.1 测试框架

**框架**: pytest

**配置**: `pyproject.toml`
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
```

#### 4.1.2 核心测试用例

**Node 节点测试**:
```python
# tests/unit/test_node.py
import pytest
import numpy as np

class TestPixelBlock:
    """像素块测试"""
    
    def test_is_pure_with_uniform_color(self):
        """纯色区域识别"""
        data = np.full((8, 8, 3), [255, 0, 0], dtype=np.uint8)
        region = PixelRegion(data)
        assert region.is_pure is True
    
    def test_is_pure_with_gradient(self):
        """渐变区域识别为非纯色"""
        data = np.zeros((8, 8, 3), dtype=np.uint8)
        data[:, :, 0] = np.arange(0, 255, 4)[:, np.newaxis]
        region = PixelRegion(data)
        assert region.is_pure is False
    
    def test_hash_consistency(self):
        """哈希值一致性"""
        data = np.full((8, 8, 3), 128, dtype=np.uint8)
        region1 = PixelRegion(data)
        region2 = PixelRegion(data.copy())
        assert region1.hash == region2.hash
    
    def test_black_detection(self):
        """黑色检测"""
        data = np.zeros((8, 8, 3), dtype=np.uint8)
        region = PixelRegion(data)
        assert region.is_black is True
        assert region.is_white is False
```

**GridCell 测试**:
```python
# tests/unit/test_grid_cell.py

class TestGridCell:
    """网格单元测试"""
    
    def test_middle_slice_bounds(self):
        """中间区域切片边界"""
        cell = GridCell(x=5, y=10, img_array=np.zeros((8, 8, 3), dtype=np.uint8))
        assert cell.middle.pix_array.shape == (6, 6, 3)
    
    def test_footnote_slice_bounds(self):
        """脚注区域切片边界"""
        cell = GridCell(x=5, y=10, img_array=np.zeros((8, 8, 3), dtype=np.uint8))
        assert cell.footnote.pix_array.shape == (2, 2, 3)
    
    def test_sub_node_count(self):
        """子节点数量"""
        cell = GridCell(x=5, y=10, img_array=np.zeros((8, 8, 3), dtype=np.uint8))
        sub = cell.sub_node
        assert len(sub) == 4
```

**配置系统测试**:
```python
# tests/unit/test_config.py

class TestConfigRegistry:
    """配置注册表测试"""
    
    def test_get_with_default(self):
        """默认值回退"""
        config = ConfigRegistry()
        config.add(SliderConfig("test", 0, 100, 1, 50))
        assert config.get_or_default("test") == 50
        assert config.get_or_default("nonexistent", 0) == 0
    
    def test_clamp_value(self):
        """数值边界限制"""
        config = ConfigRegistry()
        config.add(SliderConfig("test", 0, 100, 1, 50))
        config.set("test", 150)  # 超出范围
        assert config.get_or_default("test") == 100  # 应被限制到100
    
    def test_enum_default_index_out_of_range(self):
        """枚举索引越界返回空字符串"""
        config = ConfigRegistry()
        config.add(ComboConfig("test", ["A", "B", "C"], 99))
        assert config.get_or_default("test") == ""  # 越界返回空字符串
```

**AttrDict 测试**:
```python
# tests/unit/test_data.py

class TestAttrDict:
    """AttrDict测试"""
    
    def test_dot_access(self):
        """点号访问"""
        data = AttrDict({"player": {"health": 100}})
        assert data.player.health == 100
    
    def test_missing_key_returns_none_object(self):
        """缺失键返回NoneObject"""
        data = AttrDict({"player": {"health": 100}})
        result = data.player.mana
        assert isinstance(result, NoneObject)
        assert bool(result) is False
    
    def test_chained_access_no_exception(self):
        """链式访问不抛异常"""
        data = AttrDict({})
        result = data.player.target.health  # 完全不存在的路径
        assert isinstance(result, NoneObject)
    
    def test_nested_dict_conversion(self):
        """嵌套字典转换"""
        data = AttrDict({"outer": {"inner": {"value": 42}}})
        assert data.outer.inner.value == 42
```

#### 4.1.3 覆盖率目标

| 模块 | 覆盖率目标 |
|-----|-----------|
| engine/loop.py | ≥85% |
| engine/executor.py | ≥80% |
| runtime/context.py | ≥80% |
| runtime/data.py | ≥90% |
| config/registry.py | ≥85% |
| transport/bridge_client.py | ≥75% |

### 4.2 C# 单元测试

#### 4.2.1 测试框架

**框架**: xUnit + FluentAssertions

#### 4.2.2 核心测试用例

```csharp
// tests/unit/PixelCoreTests.cs

public class PixelBlockTests
{
    [Fact]
    public void IsPure_UniformColor_ReturnsTrue()
    {
        // Arrange
        var data = Enumerable.Repeat((byte)255, 192).ToArray(); // 8x8x3
        var block = new PixelBlock(data);
        
        // Act & Assert
        block.IsPure.Should().BeTrue();
    }
    
    [Fact]
    public void IsBlack_AllZeros_ReturnsTrue()
    {
        // Arrange
        var data = new byte[192];
        var block = new PixelBlock(data);
        
        // Act & Assert
        block.IsBlack.Should().BeTrue();
    }
    
    [Theory]
    [InlineData(0, 0.0)]
    [InlineData(100, 5.0)]
    [InlineData(150, 30.0)]
    [InlineData(255, 375.0)]
    public void Remaining_MapsToCorrectTime(byte brightness, double expectedTime)
    {
        // Arrange
        var data = Enumerable.Repeat(brightness, 192).ToArray();
        var block = new PixelBlock(data);
        
        // Act & Assert
        block.Remaining.Should().BeApproximately(expectedTime, 0.5);
    }
}
```

---

## 5. 集成测试设计

### 5.1 像素解析链路测试

**测试目标**: 验证从截图到JSON输出的完整链路

**测试环境**:
- 已启动的 Dumper.NET HTTP服务
- 游戏窗口或模拟输入

**测试用例**:
```python
# tests/integration/test_pixel_dump_flow.py

class TestPixelDumpFlow:
    """像素解析流程集成测试"""
    
    @pytest.fixture
    def running_dumper(self):
        """启动的Dumper服务"""
        # 启动逻辑
        yield "http://127.0.0.1:65131"
        # 清理逻辑
    
    def test_get_valid_data(self, running_dumper):
        """获取有效数据"""
        response = requests.get(running_dumper, timeout=2.0)
        assert response.status_code == 200
        data = response.json()
        assert "player" in data
        assert "timestamp" in data
    
    def test_player_status_structure(self, running_dumper):
        """玩家状态结构验证"""
        response = requests.get(running_dumper, timeout=2.0)
        data = response.json()
        
        player = data["player"]
        assert "status" in player
        assert "spell" in player
        assert "aura" in player
        
        status = player["status"]
        assert "unit_health" in status
        assert "unit_power" in status
        assert 0 <= status["unit_health"] <= 100
```

### 5.2 决策引擎集成测试

**测试目标**: 验证决策循环的正确执行

**测试用例**:
```python
# tests/integration/test_decision_engine.py

class TestDecisionEngine:
    """决策引擎集成测试"""
    
    @pytest.fixture
    def engine(self):
        """测试引擎实例"""
        config = ConfigRegistry()
        config.add(SliderConfig("fps", 1, 30, 1, 15))
        bridge = BridgeClient("http://127.0.0.1:65131")
        sender = MockInputSender()
        executor = ActionExecutor(sender)
        profile = MockProfile()
        return RotationLoopEngine(profile, config, bridge, executor)
    
    def test_start_stop(self, engine):
        """启动停止测试"""
        assert engine.is_running() is False
        engine.start()
        assert engine.is_running() is True
        engine.stop()
        assert engine.is_running() is False
    
    def test_tick_interval(self, engine):
        """Tick间隔验证"""
        engine.start()
        intervals = []
        last_tick = [time.time()]
        
        original_fetch = engine.bridge_client.fetch
        def mock_fetch():
            intervals.append(time.time() - last_tick[0])
            last_tick[0] = time.time()
            return AttrDict({"player": {"status": {"exists": True}}})
        engine.bridge_client.fetch = mock_fetch
        
        time.sleep(1.0)  # 运行约15个tick
        engine.stop()
        
        avg_interval = sum(intervals) / len(intervals)
        assert 0.06 <= avg_interval <= 0.08  # 约15fps，允许抖动
```

### 5.3 配置系统集成测试

```python
# tests/integration/test_config_integration.py

class TestConfigGUIIntegration:
    """配置GUI集成测试"""
    
    def test_gui_can_write_config(self):
        """GUI路径可写"""
        config = ConfigRegistry()
        config.add(SliderConfig("test", 0, 100, 1, 50))
        
        # GUI事件路径（模拟）
        config.set_from_gui("test", 75)
        assert config.get_or_default("test") == 75
    
    def test_normal_path_cannot_write(self):
        """普通路径不可写"""
        config = ConfigRegistry()
        config.add(SliderConfig("test", 0, 100, 1, 50))
        
        with pytest.raises(PermissionError):
            config.set("test", 75)  # 应抛异常
```

---

## 6. E2E 测试设计

### 6.1 完整战斗流程测试

**测试目标**: 验证从游戏到决策到执行的全链路

**测试环境**:
- 真实游戏窗口
- 已启动的所有服务

**测试用例**:
```python
# tests/e2e/test_priest_rotation.py

class TestPriestRotationE2E:
    """戒律牧旋转E2E测试"""
    
    @pytest.fixture(scope="class")
    def game_process(self):
        """游戏进程"""
        # 启动游戏或连接到已运行游戏
        yield
        # 清理
    
    def test_full_rotation_cycle(self, game_process):
        """完整战斗循环"""
        # 1. 启动组件
        dumper = start_dumper()
        rotation = start_rotation("PriestDiscipline")
        
        # 2. 进入战斗
        enter_combat()
        
        # 3. 验证自动循环
        time.sleep(10)
        
        # 4. 检查日志无错误
        assert rotation.error_count == 0
        
        # 5. 验证关键技能施放
        cast_log = rotation.get_cast_log()
        assert any("Penance" in log for log in cast_log) or \
               any("Shadow Word: Pain" in log for log in cast_log)
```

### 6.2 遮挡恢复测试

```python
# tests/e2e/test_occlusion_recovery.py

class TestOcclusionRecovery:
    """遮挡恢复E2E测试"""
    
    def test_recovery_after_occlusion(self):
        """遮挡后恢复"""
        # 1. 正常运行
        rotation = start_rotation("PriestDiscipline")
        time.sleep(2)
        
        # 2. 模拟遮挡
        overlap_window()
        time.sleep(2)
        
        # 3. 验证error状态
        assert "遮挡" in rotation.last_error
        
        # 4. 移除遮挡
        remove_overlap()
        time.sleep(2)
        
        # 5. 验证恢复
        assert rotation.is_recovered()
        assert rotation.error_count == 1  # 只有一个错误
```

---

## 7. 性能测试

### 7.1 帧处理延迟测试

```python
# tests/performance/test_frame_processing.py

class TestFrameProcessingPerformance:
    """帧处理性能测试"""
    
    def test_frame_processing_latency_p99(self):
        """帧处理延迟P99 < 50ms"""
        latencies = []
        for _ in range(1000):
            start = time.time()
            # 模拟帧处理
            process_frame()
            latencies.append((time.time() - start) * 1000)
        
        p99 = np.percentile(latencies, 99)
        assert p99 < 50, f"P99 latency {p99}ms exceeds 50ms"
```

### 7.2 内存增长测试

```python
# tests/performance/test_memory_growth.py

class TestMemoryGrowth:
    """内存增长测试"""
    
    def test_memory_growth_under_1_percent_per_minute(self):
        """内存增长 < 1%/min"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 运行1分钟
        rotation = start_rotation("PriestDiscipline")
        time.sleep(60)
        rotation.stop()
        
        final_memory = process.memory_info().rss
        growth = (final_memory - initial_memory) / initial_memory * 100
        
        assert growth < 1.0, f"Memory growth {growth}% exceeds 1%"
```

---

## 8. 自动化测试执行

### 8.1 CI/CD 集成

**GitHub Actions**:
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run unit tests
        run: uv run pytest tests/unit -v --cov
      
      - name: Run integration tests
        run: uv run pytest tests/integration -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### 8.2 测试执行命令

| 测试类型 | 命令 |
|---------|------|
| 所有单元测试 | `pytest tests/unit -v` |
| 带覆盖率 | `pytest tests/unit --cov=ezdriverx2 --cov-report=html` |
| 特定模块 | `pytest tests/unit/test_node.py -v` |
| 集成测试 | `pytest tests/integration -v` |
| E2E测试 | `pytest tests/e2e -v` |
| 性能测试 | `pytest tests/performance -v` |

---

## 9. 测试验收标准

### 9.1 功能验收

| 编号 | 检查项 | 验收方法 |
|-----|-------|---------|
| TC-01 | 像素解析结果与原版一致 | 快照对比 |
| TC-02 | 决策延迟 P99 < 100ms | 性能测试 |
| TC-03 | 遮挡检测准确 | 人工测试 |
| TC-04 | 异常恢复自动重试 | 故障注入 |
| TC-05 | 配置正确应用 | 配置覆盖测试 |

### 9.2 质量验收

| 指标 | 目标值 | 测量方法 |
|-----|-------|---------|
| 单元测试覆盖率 | ≥60% | Coverage.py |
| 集成测试覆盖率 | ≥60% | 组件交互覆盖 |
| 关键路径E2E覆盖 | 100% | 测试用例映射 |
| 代码重复率 | ≤5% | SonarQube |

### 9.3 回归检查清单

- [ ] 像素解析结果与原版一致
- [ ] 决策延迟 P99 < 100ms
- [ ] 内存增长 < 1%/min
- [ ] CPU 占用变化 < 5%
- [ ] 网络重试逻辑正常
- [ ] 异常不导致崩溃

---

## 10. 附录

### 10.1 Mock 对象

**MockBridgeClient**:
```python
class MockBridgeClient:
    def __init__(self, data: dict | None = None):
        self._data = data or self._default_data()
    
    def fetch(self) -> AttrDict | None:
        return AttrDict(self._data)
    
    def _default_data(self) -> dict:
        return {
            "player": {
                "status": {"exists": True, "unit_health": 100}
            }
        }
```

**MockInputSender**:
```python
class MockInputSender:
    def __init__(self):
        self.sent_keys: list[str] = []
    
    def send_key_to_window(self, hwnd: int, key: str) -> bool:
        self.sent_keys.append(key)
        return True
```

### 10.2 测试数据生成

**合成像素帧**:
```python
def create_synthetic_frame(
    width: int = 424,
    height: int = 144,
    player_health: float = 85.0
) -> np.ndarray:
    """创建合成像素帧用于测试"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    # ... 填充测试数据
    return frame
```

---

**文档修订记录**:

| 版本 | 日期 | 修订内容 |
|-----|------|---------|
| 1.0 | 2026-04-02 | 初始版本 |
