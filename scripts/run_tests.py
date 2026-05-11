"""
AI客服系统自动化测试执行脚本 V4.0

核心变更（V4.0）：
1. TestRunner 类拆分为 CaseManager + TestOrchestrator + EvaluationResultBuilder
2. 组件编排模式：main() 直接组合各组件，不再有巨型 TestRunner 类
3. MarkdownReportGenerator 从 reporting.py 导入（过渡方案，后续替换为 Dashboard）
4. 硬编码常量统一从 config.py 加载函数获取

日期: 2026-05-11
版本: 4.0
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List

from tools.config import (
    ConfigRegistry,
    get_dimension_names,
    get_evaluator_providers,
    get_model_under_test_config,
    get_pass_statuses,
    get_project_dir,
    get_results_dir,
    get_test_cases_path,
    set_current_project,
    ensure_project_dirs,
    validate_config_consistency,
)
from tools.case_manager import CaseManager
from tools.execution import TestRunRecorder
from tools.reporting import BadCaseManager, MarkdownReportGenerator
from tools.test_orchestrator import TestOrchestrator


def _handle_report_only(args):
    """--report-only 分支：从 results.json 重新生成报告"""
    results_dir = get_results_dir()
    batch_dir = os.path.join(results_dir, args.batch_id)

    results_json_path = os.path.join(batch_dir, "results.json")
    if not os.path.exists(results_json_path):
        print(f"❌ 结果文件不存在: {results_json_path}")
        return

    with open(results_json_path, 'r', encoding='utf-8') as f:
        all_results: List[Dict] = json.load(f)

    test_cases_version = "unknown"
    if all_results and len(all_results) > 0:
        test_cases_version = all_results[0].get("test_case_version", "unknown")

    model = "unknown"
    evaluator_model = "unknown"
    if all_results and len(all_results) > 0:
        model = all_results[0].get("model_under_test", "unknown")
        evaluator_model = all_results[0].get("evaluator_model", "unknown")

    print(f"📊 读取到 {len(all_results)} 条测试结果")

    MarkdownReportGenerator(
        all_results, batch_dir, model=model,
        evaluator_model=evaluator_model,
        test_cases_version=test_cases_version
    ).generate()

    print(f"✅ 测试报告已重新生成: {os.path.join(batch_dir, 'summary.md')}")


def _setup_batch(args, results_dir, orchestrator):
    """创建/追加/更新批次目录和 TestRunRecorder"""
    if args.report in ['append', 'update'] and args.batch_id:
        batch_dir = os.path.join(results_dir, args.batch_id)
        if not os.path.exists(batch_dir):
            print(f"❌ 批次目录不存在: {args.batch_id}")
            return None, None, None

        batch_id = args.batch_id
        output_mode = 'append' if args.report == 'append' else 'new'
        print(f"📁 操作批次: {batch_id} ({args.report} 模式)")

        registry = ConfigRegistry.get_instance() if ConfigRegistry._instance else None
        recorder = TestRunRecorder(batch_dir, config_registry=registry)
        try:
            recorder.load_test_config()
            print(f"📊 已加载批次配置: {batch_id}")
        except FileNotFoundError:
            recorder.create_test_config(
                batch_id=batch_id,
                test_case_version=orchestrator.test_cases_version,
                test_case_file="cases/universal.json",
                model=orchestrator.model,
                evaluator_model=orchestrator.evaluator_model_name,
                test_parameters={"mode": args.mode, "concurrent": args.concurrent},
                evaluator_providers=[{"name": p["name"], "model": p["model"], "base_url": p["base_url"], "priority": p["priority"]} for p in get_evaluator_providers()]
            )
    else:
        existing_batches = [d for d in os.listdir(results_dir) if d.startswith("batch-")]
        if existing_batches:
            last_batch_num = max(int(b.split("-")[1].split("_")[0]) for b in existing_batches)
            next_batch_num = last_batch_num + 1
        else:
            next_batch_num = 1

        current_date = datetime.now().strftime("%Y-%m-%d")
        batch_id = f"batch-{next_batch_num:03d}_{current_date}"
        batch_dir = os.path.join(results_dir, batch_id)
        os.makedirs(batch_dir, exist_ok=True)

        registry = ConfigRegistry.get_instance() if ConfigRegistry._instance else None
        recorder = TestRunRecorder(batch_dir, config_registry=registry)
        recorder.create_test_config(
            batch_id=batch_id,
            test_case_version=orchestrator.test_cases_version,
            test_case_file="cases/universal.json",
            model=orchestrator.model,
            evaluator_model=orchestrator.evaluator_model_name,
            test_parameters={"mode": args.mode, "concurrent": args.concurrent},
            evaluator_providers=[{"name": p["name"], "model": p["model"], "base_url": p["base_url"], "priority": p["priority"]} for p in get_evaluator_providers()]
        )

        output_mode = 'new'
        print(f"📁 新建批次: {batch_id}")

    return batch_dir, output_mode, recorder


def _finalize_audit(recorder, results, test_cases, orchestrator):
    """审计报告 + quality_gates"""
    if not recorder:
        return

    pass_statuses = get_pass_statuses()
    passed_count = sum(1 for r in results if r["evaluation_result"]["status"] in pass_statuses)
    pass_rate = passed_count / len(results) * 100 if results else 0

    registry = ConfigRegistry.get_instance() if ConfigRegistry._instance else None
    threshold = registry.quality_gate.get("overall_threshold", 0.9) if registry else 0.9

    recorder.update_test_config({
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
        "execution_metrics": {
            "total_duration_seconds": 0,
            "average_time_per_case_seconds": 0.0,
            "success_rate": 1.0,
            "api_calls": len(results) * 2,
            "total_tokens": 0
        },
        "quality_gates": {
            "actual_pass_rate": pass_rate / 100,
            "result": "PASS" if pass_rate / 100 >= threshold else "FAIL"
        }
    })

    recorder.end_logging({
        "total": len(test_cases),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "pass_rate": pass_rate
    })

    coverage_validation = recorder.validate_coverage(len(test_cases), len(results))
    consistency_validation = recorder.validate_consistency(len(test_cases), len(results))
    config_validation = recorder.validate_config_integrity()

    validation_results = [coverage_validation, consistency_validation, config_validation]

    audit_report = recorder.generate_audit_report(validation_results)
    recorder.save_audit_report(audit_report)

    if not all(v["passed"] for v in validation_results):
        print("⚠️ 完整性检查未通过:")
        for v in validation_results:
            if not v["passed"]:
                print(f"  - {v['name']}: {v['actual']}")
    else:
        print("✅ 完整性检查通过")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI客服系统自动化测试执行脚本 V4.0')
    parser.add_argument('--mode', type=str, default='full',
                       choices=['single', 'selected', 'incremental', 'full'],
                       help='执行模式: single(单条), selected(指定用例), incremental(增量), full(全量)')
    parser.add_argument('--cases', type=str, default=None,
                       help='指定要执行的用例ID，多个用逗号分隔')
    parser.add_argument('--report', type=str, default='new',
                       choices=['new', 'append', 'update'],
                       help='报告输出模式: new(新建批次), append(追加到批次), update(更新批次报告)')
    parser.add_argument('--batch-id', type=str, default=None,
                       help='指定要操作的批次ID')
    parser.add_argument('--report-only', action='store_true',
                       help='仅重新生成报告（不执行测试）')
    parser.add_argument('--concurrent', type=int, default=0,
                       help='并发执行数（0=单线程，建议不超过2）')
    parser.add_argument('--project', type=str, default=None,
                       help='项目名称，例如 01-ai-customer-service、02-chat-companion')

    args = parser.parse_args()

    if args.project:
        set_current_project(args.project)
        ensure_project_dirs(args.project)

    try:
        validate_config_consistency()
    except ValueError as e:
        print(f"❌ 配置校验失败: {e}")
        return

    if args.report_only:
        _handle_report_only(args)
        return

    mut_config = get_model_under_test_config()
    API_KEY = mut_config.get('api_key', '')
    if not API_KEY:
        print("❌ 请在 api_config.yaml 中配置 model_under_test 的 api_key 或 sk")
        return

    case_mgr = CaseManager(project_name=args.project)
    orchestrator = TestOrchestrator(project_name=args.project)

    test_cases, version = case_mgr.load_and_filter(
        mode=args.mode, cases_ids=args.cases, batch_id=args.batch_id
    )
    orchestrator.test_cases_version = version

    if not test_cases:
        print("⚠️ 没有需要执行的测试用例")
        return

    print(f"\n执行模式: {args.mode}")
    print(f"将执行 {len(test_cases)} 条用例")

    results_dir = str(get_results_dir())
    batch_dir, output_mode, recorder = _setup_batch(args, results_dir, orchestrator)

    if batch_dir is None:
        return

    if recorder:
        dimensions_set = set()
        for case in test_cases:
            dimensions_set.add(case.get('dimension', 'unknown'))
        dimensions = sorted(list(dimensions_set))

        recorder.update_test_config({
            "test_configuration": {
                "total_cases": len(test_cases),
                "dimensions": dimensions
            }
        })
        recorder.start_logging(recorder.config["test_run_id"])

    if args.concurrent > 0:
        results = orchestrator.run_tests_concurrent(test_cases, max_workers=args.concurrent, recorder=recorder)
    else:
        results = orchestrator.run_all_tests(test_cases, recorder=recorder)

    recorder.save_execution_records(results, mode=output_mode)
    recorder.save_evaluation_results(results, mode=output_mode)

    MarkdownReportGenerator(
        results, batch_dir, model=orchestrator.model,
        evaluator_model=orchestrator.evaluator_model_name,
        test_cases_version=orchestrator.test_cases_version
    ).generate()

    project_dir = str(get_project_dir())
    bad_case_mgr = BadCaseManager(project_dir)
    bad_case_mgr.extract_from_batch(batch_dir)
    bad_case_mgr.generate_markdown_report()
    bad_case_mgr.export_csv()
    stats = bad_case_mgr.get_statistics()
    print(f"📊 Bad Case 统计: 总计 {stats['total']} 条, P0 {stats['by_severity'].get('P0', 0)} 条, P1 {stats['by_severity'].get('P1', 0)} 条")

    _finalize_audit(recorder, results, test_cases, orchestrator)

    print(f"\n✅ 测试完成！批次: {os.path.basename(batch_dir)}")


if __name__ == "__main__":
    main()
