# EZWowX2 数据库设计文档 (DBDD)

**文档版本**: 1.0
**创建日期**: 2026-04-02
**最后更新**: 2026-04-02
**适用范围**: EZWowX2 项目组

---

## 1. 文档概述

### 1.1 目的

本文档描述EZWowX2项目中的数据库设计，包括数据模型、表结构、字段定义及ER图。

### 1.2 数据库使用分析

经过代码分析，本项目中**确实使用了数据库**：

- **使用位置**: EZBridgeX2/core/database.py
- **数据库类型**: SQLite
- **用途**: 图标标题仓库，存储图标哈希与法术名称的映射关系

### 1.3 技术选型理由

| 考虑因素 | 选择SQLite的原因 |
|---------|----------------|
| 数据量 | 本地图标库，数据量可控（万级） |
| 性能 | 嵌入式，无需网络延迟 |
| 部署 | 无需单独数据库服务 |
| 事务 | 支持ACID，保证数据一致性 |

---

## 2. 数据库架构

### 2.1 数据库文件

- **文件路径**: `EZBridgeX2/database.sqlite` (默认)
- **可配置**: 通过 IconTitleRepository 构造函数参数指定

### 2.2 核心表结构

#### 2.2.1 icons 表

**用途**: 存储法术图标基本信息

```sql
CREATE TABLE IF NOT EXISTS icons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    footnote_title TEXT NOT NULL DEFAULT 'Unknown',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明**:

| 字段名 | 数据类型 | 约束 | 说明 |
|-------|---------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 主键 |
| title | TEXT | NOT NULL | 法术名称 |
| footnote_title | TEXT | NOT NULL, DEFAULT 'Unknown' | 图标类型名称 |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**示例数据**:

| id | title | footnote_title | created_at | updated_at |
|----|-------|----------------|-------------|------------|
| 1 | 惩击 | PLAYER_SPELL | 2026-04-02 12:00:00 | 2026-04-02 12:00:00 |
| 2 | 暗影魔 | PLAYER_SPELL | 2026-04-02 12:00:00 | 2026-04-02 12:00:00 |

#### 2.2.2 icon_signatures 表

**用途**: 存储图标像素签名，用于哈希匹配

```sql
CREATE TABLE IF NOT EXISTS icon_signatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icon_id INTEGER NOT NULL,
    middle_hash TEXT NOT NULL UNIQUE,
    full_data BLOB NOT NULL,
    match_type TEXT NOT NULL DEFAULT 'manual',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(icon_id) REFERENCES icons(id) ON DELETE CASCADE
);
```

**字段说明**:

| 字段名 | 数据类型 | 约束 | 说明 |
|-------|---------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 主键 |
| icon_id | INTEGER | NOT NULL, FOREIGN KEY | 关联icons表 |
| middle_hash | TEXT | NOT NULL, UNIQUE | 6x6区域哈希值 |
| full_data | BLOB | NOT NULL | 完整8x8像素数据 |
| match_type | TEXT | NOT NULL, DEFAULT 'manual' | 匹配类型: manual/cosine |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**:

```sql
CREATE INDEX IF NOT EXISTS idx_icon_signatures_icon_id ON icon_signatures(icon_id);
CREATE INDEX IF NOT EXISTS idx_icons_title ON icons(title);
```

**示例数据**:

| id | icon_id | middle_hash | full_data | match_type | created_at |
|----|---------|-------------|-----------|------------|------------|
| 1 | 1 | abc123def456 | <192字节> | manual | 2026-04-02 12:00:00 |
| 2 | 1 | def456ghi789 | <192字节> | cosine | 2026-04-02 12:01:00 |

---

## 3. ER图

### 3.1 实体关系

```
┌─────────────────────┐       ┌──────────────────────────────┐
│       icons         │       │     icon_signatures          │
├─────────────────────┤       ├──────────────────────────────┤
│ PK  id              │◀──────│ FK  icon_id                 │
│     title           │  1:N  │ PK  id                      │
│     footnote_title  │       │     middle_hash (UNIQUE)   │
│     created_at     │       │     full_data (BLOB)        │
│     updated_at     │       │     match_type              │
└─────────────────────┘       │     created_at              │
                             └──────────────────────────────┘
```

### 3.2 实体说明

**icons 实体**:
- 代表一个法术图标
- title: 法术名称（如"惩击"）
- footnote_title: 图标类型（如"PLAYER_SPELL"）

**icon_signatures 实体**:
- 代表一个图标的具体像素签名
- 同一个图标可能有多个签名（不同形态）
- 支持两种匹配方式：精确哈希(manual)和余弦相似度(cosine)

---

## 4. 数据访问层

### 4.1 核心类

#### 4.1.1 IconTitleRepository

**文件**: `EZBridgeX2/EZBridgeX2/core/database.py`

**职责**:
- 图标标题的CRUD操作
- 哈希匹配查询
- 余弦相似度计算
- 数据导入/导出

**主要方法**:

| 方法 | 签名 | 说明 |
|-----|------|------|
| get_title | `(middle_hash, middle_array, full_array) -> str` | 获取图标标题（先哈希后余弦） |
| add_title | `(full_array, middle_hash, middle_array, title, match_type) -> int` | 添加新图标 |
| delete_title | `(record_id) -> bool` | 删除图标记录 |
| update_title | `(record_id, new_title, match_type) -> bool` | 更新图标标题 |
| get_all_titles | `() -> list[IconTitleRecord]` | 获取所有图标 |
| export_to_json | `(path) -> bool` | 导出到JSON |
| import_from_json | `(path, merge) -> bool` | 从JSON导入 |

#### 4.1.2 IconTitleRecord

**数据类**:

```python
@dataclass
class IconTitleRecord:
    id: int
    icon_id: int
    full_data: bytes
    middle_hash: str
    title: str
    match_type: str
    created_at: str
    footnote_title: str
    
    @property
    def full_blob(self) -> bytes: ...
    
    @property
    def middle_blob(self) -> bytes: ...
    
    @property
    def footnote_color(self) -> tuple[int, int, int] | None: ...
```

### 4.2 匹配算法

#### 4.2.1 精确哈希匹配

```
1. 提取图标中间6x6像素区域
2. 使用xxhash3_64计算哈希
3. 在_hash_map中O(1)查找
4. 命中返回title，否则继续
```

#### 4.2.2 余弦相似度回退

```
1. 哈希未命中时启动
2. 遍历_middle_cache中的所有记录
3. 计算余弦相似度: cos(A,B) = A·B/(|A|·|B|)
4. 相似度 >= 阈值(0.995)时认为匹配
5. 自动添加为新签名
```

---

## 5. 数据字典

### 5.1 footnote_title 枚举值

| 值 | 说明 |
|----|------|
| MAGIC | 魔法类型 |
| CURSE | 诅咒类型 |
| DISEASE | 疾病类型 |
| POISON | 中毒类型 |
| ENRAGE | 激怒类型 |
| BLEED | 流血类型 |
| PLAYER_DEBUFF | 玩家减益 |
| PLAYER_BUFF | 玩家增益 |
| PLAYER_SPELL | 玩家施法 |
| ENEMY_SPELL_INTERRUPTIBLE | 可打断敌方施法 |
| ENEMY_SPELL_NOT_INTERRUPTIBLE | 不可打断敌方施法 |
| ENEMY_DEBUFF | 敌方减益 |
| NONE | 无/未知 |
| Unknown | 无法识别 |

### 5.2 match_type 枚举值

| 值 | 说明 |
|----|------|
| manual | 手动添加的精确匹配 |
| cosine | 余弦相似度自动匹配 |

---

## 6. 性能优化

### 6.1 缓存策略

**内存缓存**:
- `_hash_map`: 哈希 -> (title, signature_id) 映射
- `_middle_cache`: (signature_id, middle_array, title) 列表
- 启动时全量加载

**缓存更新**:
- 添加/删除/更新后同步更新缓存
- 不一致时重新加载

### 6.2 索引优化

| 索引名 | 表 | 字段 | 用途 |
|-------|-----|------|------|
| idx_icon_signatures_icon_id | icon_signatures | icon_id | 按图标ID查询签名 |
| idx_icons_title | icons | title | 按名称搜索图标 |

---

## 7. 数据迁移

### 7.1 导入导出格式

**导出格式** (JSON v2):
```json
{
    "format": "EZBridgeX2.NodeTitlesExport",
    "version": 2,
    "exported_at": "2026-04-02T12:00:00",
    "record_count": 100,
    "records": [
        {
            "middle_hash": "abc123...",
            "title": "惩击",
            "match_type": "manual",
            "created_at": "2026-04-02T12:00:00",
            "footnote_title": "PLAYER_SPELL",
            "full_data": "base64 encoded..."
        }
    ]
}
```

### 7.2 版本迁移

- v1: 纯JSON数组格式
- v2: 带元数据的JSON对象格式
- 迁移工具: `tools/migrate_node_titles_export_v1_to_v2.py`

---

## 8. 备份与恢复

### 8.1 备份

```bash
# 手动备份
cp database.sqlite database_backup.sqlite
```

### 8.2 恢复

```bash
# 从备份恢复
cp database_backup.sqlite database.sqlite
```

---

## 9. 附录

### 9.1 存储空间估算

| 数据量 | 估算大小 |
|--------|---------|
| 1000个图标 | ~200KB |
| 10000个图标 | ~2MB |
| 100000个图标 | ~20MB |

### 9.2 字段大小说明

- `full_data`: 8x8x3 = 192字节
- `middle_hash`: 8字节 (xxhash3_64)
- 单条签名记录: ~250字节

---

**文档修订记录**:

| 版本 | 日期 | 修订内容 |
|-----|------|---------|
| 1.0 | 2026-04-02 | 初始版本 |
