"""Dashboard - 交互式 HTML 仪表盘

核心组件：
1. ChartFactory — 6种基础图表 + 2种自适应图表 + 颜色映射
2. DashboardBuilder — 4个Tab + 维度特化注册表 + 通用fallback

设计原则：
- YAML 是单一数据源，所有维度/状态配置从 config.py 动态获取
- 新增安全维度只需在 YAML 中配置，Dashboard 自动适配（通用fallback）
- security_detail 展开路径从 YAML dimensions 配置节动态读取（坑36修复）
- _load_results() 对 security_detail 缺失和格式不一致做防御性处理（坑41修复）
"""

import json
import os
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from tools.config import (
    get_dimension_names,
    get_dimension_status_map,
    get_pass_statuses,
    get_fail_statuses,
    get_security_dimensions,
    get_test_generation_config,
)
from tools.utils import get_logger

logger = get_logger(__name__)


class ChartFactory:
    """图表工厂 — 统一创建所有 Plotly 图表"""

    COLOR_PASS = "#2ecc71"
    COLOR_FAIL = "#e74c3c"
    COLOR_SKIP = "#95a5a6"
    COLOR_UNKNOWN = "#bdc3c7"
    COLOR_P0 = "#e74c3c"
    COLOR_P1 = "#f39c12"
    COLOR_P2 = "#3498db"

    def _status_to_color(self, status: str) -> str:
        """根据 pass/fail 集合动态返回颜色"""
        if status in get_pass_statuses():
            return self.COLOR_PASS
        if status in get_fail_statuses():
            return self.COLOR_FAIL
        if status == "跳过":
            return self.COLOR_SKIP
        return self.COLOR_UNKNOWN

    def make_indicator(self, value, label, color=None, ref=None, fmt=".1f") -> go.Indicator:
        """指标卡片"""
        kwargs = {
            "mode": "number+delta" if ref is not None else "number",
            "value": value,
            "number": {"font": {"size": 48, "color": color or self.COLOR_PASS}, "suffix": "%"},
            "title": {"text": label, "font": {"size": 16}},
        }
        if ref is not None:
            kwargs["delta"] = {"reference": ref, "relative": True, "font": {"size": 20}}
        return go.Indicator(**kwargs)

    def make_bar(self, categories, values, colors=None, title="", x_label="", y_label="") -> go.Figure:
        """柱状图"""
        fig = go.Figure(data=[go.Bar(x=categories, y=values, marker_color=colors or self.COLOR_PASS)])
        fig.update_layout(title=title, xaxis_title=x_label, yaxis_title=y_label, height=400)
        return fig

    def make_radar(self, categories, values, title="", range_max=100) -> go.Figure:
        """雷达图"""
        fig = go.Figure(data=[go.Scatterpolar(r=values, theta=categories, fill="toself", name=title)])
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, range_max])), showlegend=False, height=500)
        return fig

    def make_heatmap(self, z, x, y, title="", colorscale="RdYlGn") -> go.Figure:
        """热力图"""
        fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y, colorscale=colorscale))
        fig.update_layout(title=title, height=400)
        return fig

    def make_donut(self, labels, values, colors=None, title="", hole=0.5) -> go.Figure:
        """环形图"""
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=hole, marker_colors=colors)])
        fig.update_layout(title=title, height=400)
        return fig

    def make_table(self, headers, rows, title="") -> go.Figure:
        """表格"""
        fig = go.Figure(data=[go.Table(
            header=dict(values=headers, fill_color="#2c3e50", font=dict(color="white", size=12), align="left"),
            cells=dict(values=rows, fill_color="#ecf0f1", font=dict(size=11), align="left")
        )])
        fig.update_layout(title=title, height=max(300, 50 + len(rows[0]) * 35 if rows else 300))
        return fig

    def make_auto_bar(self, df, dimension_col="dimension", status_col="status", title="") -> go.Figure:
        """自适应柱状图 — 新增维度无需改代码"""
        dim_map = get_dimension_status_map()
        dim_names = get_dimension_names()

        categories = []
        pass_vals = []
        fail_vals = []
        for dim in df[dimension_col].unique():
            dim_df = df[df[dimension_col] == dim]
            pass_set = dim_map.get(dim, {}).get("pass", get_pass_statuses())
            fail_set = dim_map.get(dim, {}).get("fail", get_fail_statuses())
            categories.append(dim_names.get(dim, dim))
            pass_vals.append(len(dim_df[dim_df[status_col].isin(pass_set)]))
            fail_vals.append(len(dim_df[dim_df[status_col].isin(fail_set)]))

        fig = go.Figure(data=[
            go.Bar(name="通过", x=categories, y=pass_vals, marker_color=self.COLOR_PASS),
            go.Bar(name="不通过", x=categories, y=fail_vals, marker_color=self.COLOR_FAIL),
        ])
        fig.update_layout(barmode="stack", title=title or "各维度通过率", height=400)
        return fig

    def make_auto_donut(self, df, status_col="status", title="") -> go.Figure:
        """自适应环形图 — 新增维度无需改代码"""
        status_counts = df[status_col].value_counts()
        labels = status_counts.index.tolist()
        values = status_counts.values.tolist()
        colors = [self._status_to_color(s) for s in labels]
        return self.make_donut(labels, values, colors, title=title or "状态分布")


class DashboardBuilder:
    """仪表盘构建器 — 4个Tab + 维度特化注册表 + 通用fallback"""

    def __init__(self, results_path: str, bad_cases_path: str = None,
                 historical_dir: str = None):
        self._results_path = results_path
        self._bad_cases_path = bad_cases_path
        self._historical_dir = historical_dir
        self._chart_factory = ChartFactory()
        self._df = self._load_results(results_path)

    def _load_results(self, path: str) -> pd.DataFrame:
        """加载 results.json 并展开为 DataFrame

        防御性处理（坑41修复）：
        - security_detail 缺失时跳过
        - 格式不一致时记录 warning 并跳过
        - 新增维度不在 schema 中时使用通用展开策略
        """
        try:
            with open(path, encoding="utf-8") as f:
                raw: List[Dict] = json.load(f)
        except Exception as e:
            logger.error(f"加载 results.json 失败: {e}")
            return pd.DataFrame()

        if not raw:
            return pd.DataFrame()

        try:
            df = pd.json_normalize(raw, max_level=1)
        except Exception as e:
            logger.error(f"展开 results.json 失败: {e}")
            return pd.DataFrame(raw)

        if "security_detail" in df.columns and "dimension" in df.columns:
            for dim in get_security_dimensions():
                dim_mask = df["dimension"] == dim
                if not dim_mask.any():
                    continue

                dim_records = [r for r in raw if r.get("dimension") == dim and r.get("security_detail")]
                if not dim_records:
                    continue

                try:
                    config = get_test_generation_config()
                    dim_config = config.get("dimensions", {}).get(dim, {})
                    detail_path = dim_config.get("security_detail_path", dim)

                    detail_df = pd.json_normalize(
                        dim_records,
                        record_path=[f"security_detail.{detail_path}"],
                        meta=["id"],
                        errors="ignore",
                    )
                    if not detail_df.empty:
                        for col in detail_df.columns:
                            if col != "id" and col not in df.columns:
                                df.loc[dim_mask, col] = detail_df[col].values[:dim_mask.sum()]
                except Exception as e:
                    logger.warning(f"维度 {dim} 的 security_detail 展开失败: {e}")
                    continue

        if "evaluation_result.status" in df.columns:
            df["status"] = df["evaluation_result.status"]
        elif "evaluation_result" in df.columns:
            try:
                df["status"] = df["evaluation_result"].apply(
                    lambda x: x.get("status", "未知") if isinstance(x, dict) else "未知"
                )
            except Exception:
                df["status"] = "未知"

        return df

    def _get_pass_fail_for_dim(self, dim: str) -> tuple:
        """按维度精确获取 pass/fail 集合"""
        dim_map = get_dimension_status_map()
        mapping = dim_map.get(dim, {})
        pass_set = mapping.get("pass", get_pass_statuses())
        fail_set = mapping.get("fail", get_fail_statuses())
        return pass_set, fail_set

    def _build_tab1_overview(self) -> List:
        """Tab1: 总览 — 指标卡片 + 维度柱状图 + 状态环形图"""
        figs = []
        if self._df.empty:
            return figs

        pass_statuses = get_pass_statuses()
        total = len(self._df)
        passed = len(self._df[self._df["status"].isin(pass_statuses)])
        pass_rate = passed / total * 100 if total > 0 else 0

        figs.append(go.Figure(data=[self._chart_factory.make_indicator(pass_rate, "总通过率", self._chart_factory.COLOR_PASS)]))
        figs.append(self._chart_factory.make_auto_bar(self._df, title="各维度通过率"))
        figs.append(self._chart_factory.make_auto_donut(self._df, title="状态分布"))

        return figs

    def _build_tab2_dimensions(self) -> List:
        """Tab2: 维度详情 — 每个维度一个子图"""
        figs = []
        if self._df.empty:
            return figs

        dim_names = get_dimension_names()
        for dim in self._df["dimension"].unique():
            dim_df = self._df[self._df["dimension"] == dim]
            pass_set, fail_set = self._get_pass_fail_for_dim(dim)

            passed = len(dim_df[dim_df["status"].isin(pass_set)])
            failed = len(dim_df[dim_df["status"].isin(fail_set)])
            total = len(dim_df)
            pass_rate = passed / total * 100 if total > 0 else 0

            dim_name = dim_names.get(dim, dim)

            status_counts = dim_df["status"].value_counts()
            labels = status_counts.index.tolist()
            values = status_counts.values.tolist()
            colors = [self._chart_factory._status_to_color(s) for s in labels]

            figs.append(self._chart_factory.make_donut(
                labels, values, colors,
                title=f"{dim_name} — 通过率 {pass_rate:.1f}%"
            ))

        return figs

    def _build_tab3_bad_cases(self) -> List:
        """Tab3: Bad Case 分析 — 严重度分布 + 根因分析"""
        figs = []
        if not self._bad_cases_path or not os.path.exists(self._bad_cases_path):
            return figs

        try:
            with open(self._bad_cases_path, encoding="utf-8") as f:
                bc_data = json.load(f)
        except Exception as e:
            logger.warning(f"加载 bad_cases.json 失败: {e}")
            return figs

        bad_cases = bc_data.get("bad_cases", []) if isinstance(bc_data, dict) else bc_data
        if not bad_cases:
            return figs

        bc_df = pd.DataFrame(bad_cases)

        if "severity" in bc_df.columns:
            sev_counts = bc_df["severity"].value_counts()
            colors = [self._chart_factory.COLOR_P0 if s == "P0" else
                      self._chart_factory.COLOR_P1 if s == "P1" else
                      self._chart_factory.COLOR_P2 for s in sev_counts.index]
            figs.append(self._chart_factory.make_donut(
                sev_counts.index.tolist(), sev_counts.values.tolist(), colors,
                title="Bad Case 严重度分布"
            ))

        if "root_cause" in bc_df.columns:
            rc_counts = bc_df["root_cause"].value_counts().head(10)
            figs.append(self._chart_factory.make_bar(
                rc_counts.index.tolist(), rc_counts.values.tolist(),
                colors=self._chart_factory.COLOR_P1,
                title="Top 10 根因分析"
            ))

        return figs

    def _build_tab4_trend(self) -> List:
        """Tab4: 趋势 — 历史通过率趋势线"""
        figs = []
        if not self._historical_dir or not os.path.exists(self._historical_dir):
            return figs

        summaries = []
        for batch_dir_name in sorted(os.listdir(self._historical_dir)):
            summary_path = os.path.join(self._historical_dir, batch_dir_name, "batch_summary.json")
            if os.path.exists(summary_path):
                try:
                    with open(summary_path, encoding="utf-8") as f:
                        summaries.append(json.load(f))
                except Exception:
                    continue

        if not summaries:
            try:
                batch_dir = os.path.dirname(self._results_path)
                current_summary = {
                    "batch_id": os.path.basename(batch_dir),
                    "pass_rate": len(self._df[self._df["status"].isin(get_pass_statuses())]) / len(self._df) if not self._df.empty else 0,
                }
                summaries.append(current_summary)
            except Exception:
                pass

        if summaries:
            batch_ids = [s.get("batch_id", "unknown") for s in summaries]
            pass_rates = [s.get("pass_rate", 0) * 100 for s in summaries]

            fig = go.Figure(data=go.Scatter(
                x=batch_ids, y=pass_rates,
                mode="lines+markers",
                marker=dict(size=10, color=self._chart_factory.COLOR_PASS),
                line=dict(width=2, color=self._chart_factory.COLOR_PASS),
            ))
            fig.add_hline(y=90, line_dash="dash", line_color=self._chart_factory.COLOR_FAIL,
                         annotation_text="质量门禁 90%")
            fig.update_layout(title="历史通过率趋势", yaxis_title="通过率 (%)", height=400)
            figs.append(fig)

        return figs

    def build(self) -> go.Figure:
        """构建完整仪表盘"""
        tab1_figs = self._build_tab1_overview()
        tab2_figs = self._build_tab2_dimensions()
        tab3_figs = self._build_tab3_bad_cases()
        tab4_figs = self._build_tab4_trend()

        total_tabs = 4
        has_content = any([tab1_figs, tab2_figs, tab3_figs, tab4_figs])

        if not has_content:
            fig = go.Figure()
            fig.update_layout(title="暂无数据", height=400)
            return fig

        all_figs = tab1_figs + tab2_figs + tab3_figs + tab4_figs
        n_figs = len(all_figs)

        if n_figs == 0:
            fig = go.Figure()
            fig.update_layout(title="暂无数据", height=400)
            return fig

        cols = min(3, n_figs)
        rows = (n_figs + cols - 1) // cols

        subplot_types = []
        subplot_titles = []
        for f in all_figs:
            if isinstance(f, go.Figure):
                has_domain = any(isinstance(t, (go.Pie, go.Indicator)) for t in f.data)
                subplot_types.append({"type": "domain"} if has_domain else {"type": "xy"})
                title_text = f.layout.title.text if f.layout.title and f.layout.title.text else ""
                subplot_titles.append(title_text)
            else:
                subplot_types.append({"type": "domain"})
                subplot_titles.append("")

        while len(subplot_types) < rows * cols:
            subplot_types.append({"type": "xy"})
            subplot_titles.append("")

        specs_2d = [subplot_types[i*cols:(i+1)*cols] for i in range(rows)]

        fig = make_subplots(
            rows=rows, cols=cols,
            specs=specs_2d,
            subplot_titles=subplot_titles,
        )

        for i, sub_fig in enumerate(all_figs):
            row = i // cols + 1
            col = i % cols + 1
            if isinstance(sub_fig, go.Figure):
                for trace in sub_fig.data:
                    fig.add_trace(trace, row=row, col=col)

        fig.update_layout(height=400 * rows, showlegend=False,
                         title_text="AI客服自动化测试仪表盘",
                         title_font_size=24)
        return fig

    def save(self, output_path: str):
        """保存为 HTML 文件"""
        fig = self.build()
        fig.write_html(output_path)
        print(f"✅ Dashboard 已保存: {output_path}")
