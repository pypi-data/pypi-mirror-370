import jinja2
import re
from typing import Dict, Any, List, Callable, Optional


class Jinja2Renderer:
    """
    Jinja2渲染器类，用于根据Jinja2模板渲染数据
    """

    def __init__(self, output_template: str, custom_functions: Optional[Dict[str, Callable]] = None):
        """
        初始化渲染器
        
        Args:
            output_template (str): 输出模板定义
            custom_functions (dict, optional): 自定义函数字典
        """
        self.field_templates = self._parse_output_template(output_template)
        self.env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        
        # 添加内置过滤器
        self.env.filters['split'] = lambda x, sep=None: x.split(sep) if x else []
        self.env.filters['replace'] = lambda x, old, new: x.replace(old, new) if x else x
        
        # 添加自定义函数
        self.custom_functions = custom_functions or {}
        for name, func in self.custom_functions.items():
            self.env.globals[name] = func

    def _parse_output_template(self, output_template: str) -> Dict[str, str]:
        """
        解析输出模板定义
        
        Args:
            output_template (str): 输出模板定义
            
        Returns:
            dict: 字段到模板的映射
        """
        field_templates = {}
        current_field = None
        current_template = []

        for line in output_template.splitlines():
            if '=>' in line:
                # 保存前一个字段的模板
                if current_field is not None:
                    field_templates[current_field] = '\n'.join(current_template).strip()

                # 开始新的字段
                parts = line.split('=>', 1)
                current_field = parts[0].strip()
                current_template = [parts[1].strip()] if len(parts) > 1 else []
            elif current_field is not None:
                # 继续当前字段的模板
                current_template.append(line)

        # 保存最后一个字段的模板
        if current_field is not None:
            field_templates[current_field] = '\n'.join(current_template).strip()

        return field_templates

    def render(self, data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        渲染数据
        
        Args:
            data (List[Dict[str, Any]]): 要渲染的数据
            
        Returns:
            List[Dict[str, str]]: 渲染后的数据
        """
        result = []
        for item in data:
            rendered_item = {}
            for field, template_str in self.field_templates.items():
                try:
                    # 创建模板上下文，包含所有字段
                    context = {k: v for k, v in item.items() if v is not None}
                    # 添加一些常用的过滤器和函数
                    context['upper'] = lambda x: x.upper() if x else x
                    context['lower'] = lambda x: x.lower() if x else x
                    
                    if template_str.strip():
                        template = self.env.from_string(template_str)
                        rendered_item[field] = template.render(**context).strip()
                    else:
                        rendered_item[field] = ''
                except Exception as e:
                    rendered_item[field] = f"Error rendering template: {str(e)}"
            result.append(rendered_item)
        return result

    def add_custom_function(self, name: str, func: Callable):
        """
        添加自定义函数到渲染环境
        
        Args:
            name (str): 函数名称
            func (Callable): 函数对象
        """
        self.custom_functions[name] = func
        self.env.globals[name] = func