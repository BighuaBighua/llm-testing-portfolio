# 任务2：统一版本号管理

> **优先级**: 高
> **预计工作量**: 1小时
> **涉及文件**: 多个文件

---

## 问题描述

**当前问题**：
- `universal.json` 中 version="1.1"
- `results.json` 中 version="2.0"
- 版本号混乱，无法追溯用例版本

**影响**：
- 无法确定测试结果对应的用例版本
- 版本不一致导致测试结果不可复现

---

## 当前版本号使用情况

### 文件1：`universal.json`（用例文件）

```json
{
  "metadata": {
    "version": "1.1",  // ❌ 用例版本
    "created_at": "2026-04-05",
    "updated_at": "2026-04-05"
  }
}
```

### 文件2：`test_config.json`（批次配置）

```json
{
  "test_configuration": {
    "test_case_version": "1.1",  // ✅ 已记录用例版本
    "test_case_file": "cases/universal.json",
    "test_case_hash": "abc123"
  }
}
```

### 文件3：`results.json`（测试结果）

```json
[
  {
    "test_case_version": "1.1"  // ✅ 已在本次修复中添加
  }
]
```

---

## 修改方案

### 方案A：建立版本管理机制（推荐）

#### 步骤1：创建版本管理模块

**新建文件**: `scripts/version_manager.py`

```python
"""
版本管理模块

职责：
1. 管理用例版本号
2. 生成版本号
3. 验证版本一致性
"""

import os
import json
from datetime import datetime
from typing import Dict, Any


class VersionManager:
    """版本管理器"""
    
    @staticmethod
    def generate_version(previous_version: str = None) -> str:
        """
        生成新版本号
        
        Args:
            previous_version: 上一个版本号（如 "1.0"）
        
        Returns:
            str: 新版本号（如 "1.1"）
        """
        if previous_version is None:
            return "1.0"
        
        try:
            major, minor = map(int, previous_version.split('.'))
            return f"{major}.{minor + 1}"
        except Exception:
            return "1.0"
    
    @staticmethod
    def get_current_version(test_cases_file: str) -> str:
        """
        获取当前用例版本号
        
        Args:
            test_cases_file: 用例文件路径
        
        Returns:
            str: 版本号
        """
        with open(test_cases_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get("metadata", {}).get("version", "unknown")
    
    @staticmethod
    def update_version(test_cases_file: str, changelog_entry: str = None):
        """
        更新用例版本号
        
        Args:
            test_cases_file: 用例文件路径
            changelog_entry: 变更说明
        """
        with open(test_cases_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取当前版本
        current_version = data.get("metadata", {}).get("version", "1.0")
        
        # 生成新版本
        new_version = VersionManager.generate_version(current_version)
        
        # 更新版本号
        if "metadata" not in data:
            data["metadata"] = {}
        
        data["metadata"]["version"] = new_version
        data["metadata"]["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        
        # 添加 changelog
        if changelog_entry:
            if "changelog" not in data["metadata"]:
                data["metadata"]["changelog"] = []
            
            data["metadata"]["changelog"].append({
                "version": new_version,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "changes": changelog_entry
            })
        
        # 保存文件
        with open(test_cases_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 版本已更新: {current_version} → {new_version}")
        return new_version
```

#### 步骤2：在 generate_test_cases.py 中使用

**文件**: `scripts/generate_test_cases.py`

**在保存用例时添加版本更新**：

```python
from version_manager import VersionManager

# 在保存用例时
if args.append:
    # 追加模式：更新版本号
    VersionManager.update_version(
        test_cases_file,
        changelog_entry=f"追加 {len(new_cases)} 条新用例"
    )
```

---

### 方案B：简化方案（快速修复）

#### 步骤1：修正当前版本不一致

**文件**: `universal.json`

将版本号统一为 "1.1"：

```json
{
  "metadata": {
    "version": "1.1",
    "changelog": [
      {
        "version": "1.0",
        "date": "2026-04-05",
        "changes": "初始版本：创建基础测试用例"
      },
      {
        "version": "1.1",
        "date": "2026-04-06",
        "changes": "修正 compliance 维度用例 ID 冲突（TC-COM → TC-CPM）"
      }
    ]
  }
}
```

#### 步骤2：确保所有地方使用相同版本

**检查点**：
- ✅ `universal.json` → version: "1.1"
- ✅ `test_config.json` → test_case_version: "1.1"
- ✅ `results.json` → test_case_version: "1.1"（已在本次修复中添加）

---

## 修改对比

| 当前状态 | 方案A（完整） | 方案B（快速） |
|---------|-------------|-------------|
| 版本混乱 | 自动管理版本 | 手动修正版本 |
| 无法追溯 | 完整changelog | 基础changelog |
| 工作量大 | 2-3小时 | 30分钟 |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 推荐方案

**建议采用方案B（快速修复）**，理由：
1. 当前版本不一致问题不严重
2. 已有基本的版本记录机制
3. 工作量小，可快速完成

**后续优化**：
- 如果项目持续发展，再实现方案A的完整版本管理

---

## 预计工作量

**方案B（推荐）**：
- 修正版本号: 10 分钟
- 更新 changelog: 10 分钟
- 验证一致性: 10 分钟
- **总计**: 30 分钟

**方案A（完整）**：
- 编码: 1.5 小时
- 测试: 0.5 小时
- 文档: 0.5 小时
- **总计**: 2.5 小时

---

*创建时间: 2026-04-06*
