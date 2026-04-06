# 中断恢复用户指南

> **文档版本**: 1.0
> **创建日期**: 2026-04-06
> **适用场景**: 测试执行中断后的恢复操作

---

## 📖 功能介绍

测试执行过程中可能因以下原因中断：

- **API 限流**：百度千帆 API 有 QPS 限制
- **网络故障**：网络连接不稳定
- **程序崩溃**：意外错误导致程序退出
- **主动中断**：用户手动停止测试

**中断恢复功能**可以在不重复执行已完成用例的情况下，继续执行未完成的用例，节省时间和资源。

---

## 🎯 使用场景

### 场景1：API 限流导致中断

```
执行进度: 45/80
错误信息: API rate limit exceeded
```

**恢复方案**：等待限流解除后，使用 incremental 模式恢复执行。

### 场景2：网络故障导致中断

```
执行进度: 30/80
错误信息: Connection timeout
```

**恢复方案**：网络恢复后，使用 incremental 模式恢复执行。

### 场景3：程序崩溃导致中断

```
执行进度: 60/80
错误信息: Unexpected error
```

**恢复方案**：排查问题后，使用 incremental 模式恢复执行。

---

## 📝 操作步骤

### 步骤1：检测中断情况

查看测试执行日志，确认中断位置：

```bash
# 查看最后几条日志
tail -20 projects/01-ai-customer-service/results/batch-004/test_execution.log
```

**输出示例**：

```
[2026-04-06 12:30:45] INFO  [45/80] TC-ACC-005 completed - 通过
[2026-04-06 12:30:47] INFO  [46/80] TC-ACC-006 started
[2026-04-06 12:31:02] ERROR [TC-ACC-006] API rate limit exceeded
```

**分析**：
- 已完成：45 条
- 总数：80 条
- 中断位置：TC-ACC-006

---

### 步骤2：检查环境一致性

确保测试环境未变更：

```bash
# 查看测试配置
cat projects/01-ai-customer-service/results/batch-004/test_config.json | grep -A 5 "environment"
```

**检查项**：
- ✅ 被测模型是否一致
- ✅ 评测模型是否一致
- ✅ API 端点是否一致

**如果环境已变更**，建议新建批次而不是恢复。

---

### 步骤3：恢复执行

使用 incremental 模式恢复测试：

```bash
python3 scripts/run_tests.py \
  --mode incremental \
  --report append \
  --batch-id batch-004
```

**参数说明**：
- `--mode incremental`：只执行未完成的用例
- `--report append`：追加结果到现有批次
- `--batch-id batch-004`：指定要恢复的批次

---

### 步骤4：验证恢复结果

检查测试是否完整执行：

```bash
# 查看新的日志
tail -20 projects/01-ai-customer-service/results/batch-004/test_execution.log

# 查看审计报告
cat projects/01-ai-customer-service/results/batch-004/audit_report.md
```

**预期输出**：

```
[2026-04-06 13:00:15] INFO  Test run completed: 80/80 cases executed
[2026-04-06 13:00:15] INFO  Pass rate: 93.8% (75/80)
[2026-04-06 13:00:15] INFO  Quality gate: PASS (93.8% >= 90.0%)
```

---

## ⚠️ 注意事项

### 1. 环境一致性

**问题**：如果中断期间模型或配置发生变化，测试结果可能不一致。

**解决方案**：
- 恢复前确认环境未变更
- 如果已变更，新建批次重新测试

### 2. 用例版本

**问题**：如果用例文件已更新，恢复可能导致测试不完整。

**解决方案**：
- 检查用例文件版本是否与配置一致
- 如果版本不一致，新建批次

### 3. 网络稳定

**问题**：网络不稳定可能导致多次中断。

**解决方案**：
- 确保网络连接稳定
- 考虑使用 `--concurrent 0` 单线程执行

### 4. API 限流

**问题**：频繁调用 API 可能触发限流。

**解决方案**：
- 等待限流解除后再恢复
- 调整并发数（建议不超过 2）

---

## 🔍 常见问题

### Q1: 如何判断是否需要恢复？

**A**: 查看测试日志，如果 `completed < total`，则需要恢复。

```bash
grep "Test run completed" projects/01-ai-customer-service/results/batch-004/test_execution.log
```

---

### Q2: 恢复后会重复执行吗？

**A**: 不会。incremental 模式会自动跳过已完成的用例。

---

### Q3: 如何查看已完成的用例？

**A**: 查看 results.json 文件：

```bash
cat projects/01-ai-customer-service/results/batch-004/results.json | jq '.[].id'
```

---

### Q4: 恢复失败怎么办？

**A**: 检查以下项：
1. 批次目录是否存在
2. test_config.json 是否完整
3. 用例文件是否可访问
4. API Key 是否有效

如果无法恢复，建议新建批次重新测试。

---

### Q5: 可以跨批次恢复吗？

**A**: 不可以。incremental 模式只能恢复到同一批次。如需新建批次，请使用：

```bash
python3 scripts/run_tests.py --mode full --report new
```

---

## 📊 恢复流程图

```
┌─────────────────┐
│  检测中断情况    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  检查环境一致性  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  环境是否一致？  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    v         v
┌───────┐ ┌──────────┐
│ 恢复  │ │ 新建批次  │
│ 执行  │ │ 重新测试  │
└───┬───┘ └──────────┘
    │
    v
┌─────────────────┐
│  验证恢复结果    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│     完成        │
└─────────────────┘
```

---

## 💡 最佳实践

### 1. 定期检查执行日志

```bash
# 实时监控日志
tail -f projects/01-ai-customer-service/results/batch-004/test_execution.log
```

### 2. 设置合理的并发数

```bash
# 单线程执行（最稳定）
python3 scripts/run_tests.py --mode full --concurrent 0

# 并发执行（注意限流）
python3 scripts/run_tests.py --mode full --concurrent 2
```

### 3. 保存中断现场

如果程序崩溃，保存错误日志：

```bash
# 复制日志文件
cp projects/01-ai-customer-service/results/batch-004/test_execution.log \
   projects/01-ai-customer-service/results/batch-004/test_execution_error.log
```

### 4. 使用版本控制

确保用例文件有版本管理：

```bash
# 查看用例文件版本
git log projects/01-ai-customer-service/cases/universal.json
```

---

## 📚 相关文档

- [测试报告解读指南](./report-interpretation.md)
- [测试执行审计报告说明](../technical-analysis/test-execution-audit.md)
- [项目 README](../../README.md)

---

## 🆘 获取帮助

如果遇到无法解决的问题，请：

1. 查看项目文档：`docs/` 目录
2. 检查日志文件：`test_execution.log`
3. 提交 Issue：GitHub Issues

---

*最后更新: 2026-04-06*
