# 文档更新检查清单

> **目的**：确保项目变更后，所有相关文档同步更新，避免遗漏

---

## 📋 使用方法

1. 完成代码变更后
2. 打开本检查清单
3. 找到对应的变更类型
4. 逐项检查并更新
5. 运行 `git status` 确认所有文档已更新

---

## 🔧 新增脚本时

**触发条件**：在 `scripts/` 目录新增 Python 脚本

**需要更新的文档**：

- [ ] `README.md` → "自动化评测脚本"部分
  - 添加脚本到表格
  - 标注状态（推荐/旧版/✅）

- [ ] `PROJECT_GUIDE.md` → `scripts/` 目录结构
  - 添加脚本到列表
  - 标注状态

- [ ] `scripts/README.md` → 脚本列表
  - 添加脚本说明
  - 添加使用方法

- [ ] `scripts/GUIDE.md` → 使用指南
  - 如果脚本需要详细说明，添加指南

**示例**：
```markdown
新增 generate_test_cases.py 后：
- README.md: 添加 "| generate_test_cases.py | 自动生成测试用例 | ✅ 已验证 |"
- PROJECT_GUIDE.md: 添加 "├── generate_test_cases.py  # 测试用例生成脚本 ✅"
- scripts/README.md: 添加脚本的详细说明
```

---

## 📦 新增模板时

**触发条件**：在 `templates/` 目录新增 Prompt 模板

**需要更新的文档**：

- [ ] `README.md` → "已验证的 Prompt 模板"部分
  - 添加模板到表格
  - 标注验证结果

- [ ] `PROJECT_GUIDE.md` → `templates/` 目录结构
  - 添加模板到列表
  - 标注验证状态

- [ ] `templates/README.md` → 已验证模板
  - 添加模板说明
  - 添加使用方法

---

## 🗂️ 文件移动/归档时

**触发条件**：移动或归档任何文件

**需要更新的文档**：

- [ ] `README.md` → 项目结构
  - 更新目录树

- [ ] `PROJECT_GUIDE.md` → 对应目录结构
  - 更新目录列表
  - 更新使用说明（如果有路径变化）

- [ ] 所有包含该文件路径的文档
  - 搜索文件名，更新路径
  - 例如：`cot-comparison-report.md` 移动后，更新 `templates/README.md` 的链接

**示例**：
```markdown
cot-comparison-report.md 移动到 archive/ 后：
- templates/README.md: 
  旧路径：../projects/01-ai-customer-service/results/cot-comparison-report.md
  新路径：../archive/historical-experiments/2026-04-03-cot-comparison/cot-comparison-report.md
```

---

## 📊 测试用例变化时

**触发条件**：新增、修改、删除测试用例

**需要更新的文档**：

- [ ] `README.md` → "数据说话"部分
  - 更新"测试用例覆盖场景"数值

- [ ] `PROJECT_GUIDE.md` → 项目状态
  - 如果是重大变化，更新"里程碑"

- [ ] `projects/01-ai-customer-service/README.md` → 核心数据
  - 更新测试覆盖统计
  - 更新批次运行记录

**示例**：
```markdown
测试用例从 7 → 50 后：
- README.md: "| 测试用例覆盖场景 | 50+ 条 |"
- PROJECT_GUIDE.md: "### ✅ 已完成 - 2026-04-05: 扩充测试用例到 50 条"
```

---

## 🚀 项目状态变化时

**触发条件**：完成重要里程碑、开始新阶段

**需要更新的文档**：

- [ ] `PROJECT_GUIDE.md` → 里程碑
  - 已完成 → 移到"✅ 已完成"
  - 进行中 → 移到"🚧 进行中"
  - 下一步 → 移到"📅 下一步"

- [ ] `README.md` → 项目状态
  - 更新"项目状态"行

- [ ] `MY_JOURNEY.md` → 学习记录
  - 添加新的学习阶段
  - 记录认知突破

- [ ] `projects/01-ai-customer-service/README.md` → 项目状态
  - 更新状态行

**示例**：
```markdown
扩充测试用例完成后：
- PROJECT_GUIDE.md:
  从 "### 🚧 进行中 - 扩充测试用例到 50+"
  到 "### ✅ 已完成 - 2026-04-05: 扩充测试用例到 50 条"
```

---

## 📝 文档更新时

**触发条件**：更新任何文档的内容

**需要更新的文档**：

- [ ] 检查其他文档是否有相同内容
- [ ] 确保内容一致

**常见检查点**：
- 脚本列表 → README.md, PROJECT_GUIDE.md, scripts/README.md
- 项目状态 → README.md, PROJECT_GUIDE.md, projects/README.md
- 文件路径 → 所有包含该路径的文档

---

## 🔍 快速检查命令

### 检查脚本列表一致性

```bash
# 检查 README.md 中的脚本列表
grep -A 10 "### 自动化评测脚本" README.md

# 检查 PROJECT_GUIDE.md 中的脚本列表
grep -A 10 "scripts/" PROJECT_GUIDE.md

# 检查 scripts/README.md 中的脚本列表
grep -A 20 "## 脚本列表" scripts/README.md
```

### 检查测试用例数一致性

```bash
# 检查 README.md 中的测试用例数
grep "测试用例覆盖场景" README.md

# 检查 PROJECT_GUIDE.md 中的里程碑
grep "扩充测试用例" PROJECT_GUIDE.md

# 检查 projects/README.md 中的核心数据
grep "当前用例库" projects/01-ai-customer-service/README.md
```

### 检查文件路径

```bash
# 搜索所有文档中的文件路径
grep -r "cot-comparison-report.md" --include="*.md" .
grep -r "automated-test-report.md" --include="*.md" .
```

---

## ⚠️ 常见遗漏

### 容易忘记更新的文档

1. **PROJECT_GUIDE.md 的脚本列表**
   - 原因：不是主要展示文档，容易被忽略
   - 解决：在检查清单中明确列出

2. **templates/README.md 的路径**
   - 原因：路径引用在其他文档中
   - 解决：文件移动时搜索所有引用

3. **MY_JOURNEY.md 的学习记录**
   - 原因：不是技术文档，容易被忽略
   - 解决：完成重要里程碑后立即记录

---

## 📅 定期检查

### 每周检查（建议周日）

```bash
# 1. 检查所有文档的一致性
python scripts/update_docs.py --check

# 2. 手动核对
# - 脚本列表是否一致
# - 测试用例数是否准确
# - 文件路径是否正确
```

### 每月检查（建议月初）

```bash
# 1. 清理 drafts/ 目录
ls drafts/

# 2. 检查 archive/ 是否需要整理
ls archive/historical-experiments/

# 3. 更新项目状态
# - 检查里程碑是否需要移动
# - 检查是否有新的学习记录需要添加
```

---

## 💡 核心原则

1. **变更即更新**：不要等，代码变更后立即更新文档
2. **清单即记忆**：不要依赖记忆，打开清单逐项检查
3. **一致即信任**：文档不一致 = 项目不可信
4. **路径即关键**：快速复用路径必须100%正确

---

## 🎯 使用流程

```
代码变更
    ↓
打开检查清单
    ↓
找到对应变更类型
    ↓
逐项检查并更新
    ↓
运行 git status 确认
    ↓
提交变更
```

---

**创建日期**: 2026-04-05
**维护人**: 项目负责人
**更新频率**: 每次代码变更后使用
