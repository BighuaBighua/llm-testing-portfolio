"""
Prompt模板加载与渲染工具

职责：
1. 从 templates/ 目录加载 .md 模板文件
2. 使用 {{variable}} 占位符渲染变量
3. 模板缓存避免重复IO
4. 支持转义 {{ 为 \\{{ 避免误替换
"""

import os
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PromptTemplateLoader:
    """Prompt模板加载器

    使用实例级缓存（非类变量），避免多实例间缓存污染。
    """

    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            self._templates_dir = os.path.normpath(
                os.path.join(this_dir, "..", "..", "templates")
            )
        else:
            self._templates_dir = templates_dir

        self._cache: Dict[str, str] = {}

    def load(self, relative_path: str, use_cache: bool = True) -> str:
        """加载模板文件

        Args:
            relative_path: 相对于 templates_dir 的路径
            use_cache: 是否使用缓存

        Returns:
            模板内容字符串

        Raises:
            FileNotFoundError: 模板文件不存在
        """
        if use_cache and relative_path in self._cache:
            return self._cache[relative_path]

        full_path = os.path.join(self._templates_dir, relative_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"模板文件未找到: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if use_cache:
            self._cache[relative_path] = content

        return content

    def render(self, relative_path: str, variables: Dict[str, str], use_cache: bool = True) -> str:
        """加载并渲染模板

        Args:
            relative_path: 模板相对路径
            variables: 变量字典
            use_cache: 是否使用缓存

        Returns:
            渲染后的内容
        """
        template = self.load(relative_path, use_cache=use_cache)
        return self.render_string(template, variables)

    @staticmethod
    def render_string(template: str, variables: Dict[str, str]) -> str:
        """渲染模板字符串，替换 {{variable}} 占位符

        支持 \\{{ 转义：模板中 \\{{ 不会被替换，而是输出 {{
        """
        escaped = template.replace('\\{{', '\x00ESCAPED_OPEN\x00')
        escaped = escaped.replace('\\}}', '\x00ESCAPED_CLOSE\x00')

        def replacer(match):
            key = match.group(1)
            if key in variables:
                return str(variables[key])
            logger.warning(f"模板变量未找到: {key}")
            return match.group(0)

        result = re.sub(r'\{\{(\w+)\}\}', replacer, escaped)

        result = result.replace('\x00ESCAPED_OPEN\x00', '{{')
        result = result.replace('\x00ESCAPED_CLOSE\x00', '}}')

        return result

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.debug("模板缓存已清空")
