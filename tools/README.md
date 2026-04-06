# 工具目录

> 项目辅助工具脚本

---

## 工具列表

### setup_environment.sh

**功能**: 开发环境自动配置脚本

**核心特性**:
- ✅ 自动检测 Python 和 pip 环境
- ✅ 自动尝试多个国内镜像（清华、阿里、豆瓣）
- ✅ 自动创建 `.env` 配置文件
- ✅ 验证安装是否成功

**使用方法**:
```bash
# 一键配置环境（推荐）
bash tools/setup_environment.sh
```

**脚本会自动**:
1. 检测 Python 3.8+ 是否安装
2. 检测 pip 是否可用
3. 使用国内镜像安装依赖（自动切换镜像源）
4. 从 `.env.example` 创建 `.env` 配置文件
5. 验证关键依赖是否安装成功

**手动配置**:
```bash
# 如果不想使用脚本，可以手动执行：
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cp .env.example .env
```

---

### generate_docs.py

**功能**: 文档生成器 - 自动生成项目文档

**核心特性**:
- 从 `.codebuddy/project_data.json` 读取数据
- 自动更新 `README.md` 的脚本列表部分
- 自动生成 `scripts/README.md`

**使用方法**:
```bash
# 查看生成的文档内容（不自动替换）
python3 tools/generate_docs.py

# 自动更新所有文档
python3 tools/generate_docs.py --auto-update
```

**推荐方式**: 启用 Git Hook 自动运行（见下方 `setup_git_hooks.sh`）

---

### setup_git_hooks.sh

**功能**: 启用自动更新文档的 Git Hook

**使用方法**:
```bash
bash tools/setup_git_hooks.sh
```

**效果**:
- 配置 Git 使用 `.githooks` 目录
- 每次执行 `git commit` 时，自动检查 `project_data.json` 是否有变化
- 如果有变化，自动运行文档生成器并更新文档

**禁用 Git Hook**:
```bash
git config --unset core.hooksPath
```

---

## 目录设计理念

**职责分离**：
- `scripts/` - 核心业务脚本（生成用例、运行测试、对比实验）
- `tools/` - 辅助工具脚本（文档生成、Git Hook 设置等）

**命名原则**：
- 工具类脚本放在 `tools/` 目录
- 核心业务脚本放在 `scripts/` 目录
- 保持项目结构清晰，职责明确

---

*最后更新: 2026-04-05*
