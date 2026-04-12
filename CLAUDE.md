# 项目开发规范

## 核心规则

1. 未经用户说"执行"批准，不得创建/修改/删除文件或运行命令
2. 未完全理解代码前不得提方案；先探索所有相关文件，给完整方案不分多次
3. 不得跳过 brainstorming；不得无证据声称完成
4. 每次调用 Skill、给出建议、执行修改前，必须重新读取 CLAUDE.md 确认最新版本
5. 每次回复时必须说明当前阶段状态

## 技能触发

用户输入匹配以下意图时，必须立即调用对应 Skill（不得继续正常回复）：

| 意图 | Skill |
|------|-------|
| 清理/优化/方案设计/可行性询问/目标表达 | `brainstorming` |
| Bug/错误/失败/异常排查 | `systematic-debugging` |
| 开始实施/写代码/执行计划 | `writing-plans` |
| 声称完成/修好/搞定 | `verification-before-completion` |

**无需触发 Skill**：纯读取/解释/确认类询问（如"看一下"、"什么意思"、"确认一下"）

## 工作流

**标准**：brainstorming → writing-plans → test-driven-development → verification-before-completion

**Bug修复**：systematic-debugging → test-driven-development → verification-before-completion

**铁律**：
1. 不得跳过任何阶段
2. 每阶段完成后须获用户批准
3. 完成前须提供验证证据
4. 违反铁律须立即停止并道歉

## 文档规范

设计文档路径：`archive/superpowers/specs/YYYY-MM-DD-<topic>-design.md`

- 日期格式 YYYY-MM-DD，主题用 kebab-case
- 目录不存在时自动创建
