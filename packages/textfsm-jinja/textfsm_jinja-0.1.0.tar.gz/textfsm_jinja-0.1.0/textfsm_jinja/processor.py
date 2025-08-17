from .parser import TextFSMParser
from .renderer import Jinja2Renderer
import re
from typing import Dict, Any, List, Callable, Optional, Union
import importlib.util
import sys
import os
import tempfile


class TextProcessor:
    """
    文本处理器类，整合TextFSM解析和Jinja2渲染功能
    """

    def __init__(self, parser_template: str, renderer_template: str, 
                 custom_functions: Optional[Dict[str, Callable]] = None):
        """
        初始化处理器
        
        Args:
            parser_template (str): TextFSM解析模板
            renderer_template (str): Jinja2渲染模板
            custom_functions (dict, optional): 自定义函数字典
        """
        self.parser = TextFSMParser(parser_template)
        
        # 合并自定义函数
        functions = {}
        if custom_functions:
            functions.update(custom_functions)
            
        self.renderer = Jinja2Renderer(renderer_template, functions)
        self.custom_functions = functions

    def process(self, text: str) -> list:
        """
        处理文本：解析然后渲染
        
        Args:
            text (str): 要处理的文本
            
        Returns:
            list: 处理后的结果
        """
        # 解析文本
        parsed_data = self.parser.parse(text)
        
        # 渲染数据
        rendered_data = self.renderer.render(parsed_data)
        
        return rendered_data

    @classmethod
    def from_template_string(cls, template_string: str, 
                            custom_functions: Optional[Dict[str, Callable]] = None):
        """
        从包含parser和output部分的模板字符串创建处理器
        
        Args:
            template_string (str): 包含parser和输出部分的完整模板
            custom_functions (dict, optional): 自定义函数字典
            
        Returns:
            TextProcessor: 处理器实例
        """
        # 分离parser和output部分
        parser_match = re.search(r'\[parser\](.*?)\n(?=\[|$)', template_string, re.DOTALL)
        output_match = re.search(r'\[output\](.*)', template_string, re.DOTALL)
        
        parser_template = parser_match.group(1).strip() if parser_match else ""
        output_template = output_match.group(1).strip() if output_match else ""
        
        return cls(parser_template, output_template, custom_functions)

    @classmethod
    def from_config_string(cls, config_string: str,
                          custom_functions: Optional[Dict[str, Callable]] = None):
        """
        从配置字符串创建处理器
        
        Args:
            config_string (str): 配置字符串，包含[parser]和[output]部分
            custom_functions (dict, optional): 自定义函数字典
            
        Returns:
            TextProcessor: 处理器实例
        """
        # 查找各部分
        parser_start = config_string.find('[parser]')
        custom_function_start = config_string.find('[CUSTOM_FUNCTION]')
        custom_function_py_start = config_string.find('[CUSTOM_FUNCTION_PY]')
        output_start = config_string.find('[output]')
        
        if parser_start == -1 or output_start == -1:
            raise ValueError("配置必须包含[parser]和[output]部分")
            
        # 提取parser模板
        parser_end = min(
            [x for x in [custom_function_start, custom_function_py_start, output_start] if x > 0] or [len(config_string)]
        )
        parser_content = config_string[parser_start + len('[parser]'):parser_end].strip()
        
        # 提取CUSTOM_FUNCTION部分
        custom_function_content = ""
        if custom_function_start != -1:
            custom_function_end = min(
                [x for x in [custom_function_py_start, output_start] if x > custom_function_start] or [len(config_string)]
            )
            custom_function_content = config_string[custom_function_start + len('[CUSTOM_FUNCTION]'):custom_function_end].strip()
        
        # 提取CUSTOM_FUNCTION_PY部分
        custom_function_py_content = ""
        if custom_function_py_start != -1:
            custom_function_py_end = output_start if output_start > custom_function_py_start else len(config_string)
            custom_function_py_content = config_string[custom_function_py_start + len('[CUSTOM_FUNCTION_PY]'):custom_function_py_end].strip()
        
        # 提取output模板
        output_content = config_string[output_start + len('[output]'):].strip()
        
        # 加载自定义函数
        all_custom_functions = {}
        
        # 1. 加载通过路径指定的外部模块函数
        if custom_function_content:
            # 解析CUSTOM_FUNCTION部分
            path_match = re.search(r"CUSTOM_FUNCTION_PATH\s*=\s*['\"](.+?)['\"]", custom_function_content)
            if path_match:
                module_path = path_match.group(1)
                if os.path.exists(module_path):
                    module_functions = cls.load_custom_functions_from_module(module_path)
                    all_custom_functions.update(module_functions)
        
        # 2. 加载直接在模板中定义的函数
        if custom_function_py_content:
            # 创建临时模块来执行自定义函数代码
            temp_functions = cls._load_functions_from_code(custom_function_py_content)
            all_custom_functions.update(temp_functions)
        
        # 3. 加载通过参数传递的函数（优先级最高）
        if custom_functions:
            all_custom_functions.update(custom_functions)
        
        return cls(parser_content, output_content, all_custom_functions)

    @classmethod
    def _load_functions_from_code(cls, code_string: str) -> Dict[str, Callable]:
        """
        从代码字符串中加载函数
        
        Args:
            code_string (str): 包含函数定义的代码字符串
            
        Returns:
            dict: 函数字典
        """
        # 创建一个临时模块
        functions = {}
        
        # 创建一个独立的命名空间
        namespace = {}
        
        try:
            # 执行代码
            exec(code_string, namespace)
            
            # 查找CUSTOM_FUNCTIONS字典
            if 'CUSTOM_FUNCTIONS' in namespace:
                custom_functions_dict = namespace['CUSTOM_FUNCTIONS']
                for name, func_name in custom_functions_dict.items():
                    if isinstance(func_name, str) and func_name in namespace:
                        func = namespace[func_name]
                        if callable(func):
                            functions[name] = func
                    elif callable(func_name):
                        # 如果值本身就是函数对象
                        functions[name] = func_name
            else:
                # 如果没有CUSTOM_FUNCTIONS字典，加载所有函数
                for name, obj in namespace.items():
                    if callable(obj) and not name.startswith('_'):
                        functions[name] = obj
                        
        except Exception as e:
            # 如果执行代码出错，忽略错误
            pass
            
        return functions

    def add_custom_function(self, name: str, func: Callable):
        """
        添加自定义函数到处理器
        
        Args:
            name (str): 函数名称
            func (Callable): 函数对象
        """
        self.custom_functions[name] = func
        self.renderer.add_custom_function(name, func)

    @classmethod
    def load_custom_functions_from_module(cls, module_path: str) -> Dict[str, Callable]:
        """
        从外部Python模块文件加载自定义函数
        
        Args:
            module_path (str): Python模块文件路径
            
        Returns:
            dict: 自定义函数字典
        """
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"模块文件不存在: {module_path}")
            
        # 获取模块名
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 检查是否有CUSTOM_FUNCTIONS字典
        if hasattr(module, 'CUSTOM_FUNCTIONS'):
            # 如果有CUSTOM_FUNCTIONS字典，只加载其中列出的函数
            custom_functions_dict = getattr(module, 'CUSTOM_FUNCTIONS')
            functions = {}
            for name, func_name in custom_functions_dict.items():
                if isinstance(func_name, str) and hasattr(module, func_name):
                    func = getattr(module, func_name)
                    if callable(func):
                        functions[name] = func
                elif callable(func_name):
                    # 如果值本身就是函数对象
                    functions[name] = func_name
            return functions
        else:
            # 如果没有CUSTOM_FUNCTIONS字典，加载模块中的所有函数
            functions = {}
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and not name.startswith('_'):
                    functions[name] = obj
                    
            return functions

    @classmethod
    def from_config_string_with_module(cls, config_string: str, 
                                      custom_functions_module: Optional[str] = None,
                                      custom_functions: Optional[Dict[str, Callable]] = None):
        """
        从配置字符串创建处理器，并可选择从外部模块加载自定义函数
        
        Args:
            config_string (str): 配置字符串，包含[parser]和[output]部分
            custom_functions_module (str, optional): 自定义函数模块文件路径
            custom_functions (dict, optional): 额外的自定义函数字典
            
        Returns:
            TextProcessor: 处理器实例
        """
        # 加载外部模块中的自定义函数
        module_functions = {}
        if custom_functions_module:
            module_functions = cls.load_custom_functions_from_module(custom_functions_module)
            
        # 合并所有自定义函数
        all_functions = {}
        if module_functions:
            all_functions.update(module_functions)
        if custom_functions:
            all_functions.update(custom_functions)
            
        # 查找[parser]部分
        parser_start = config_string.find('[parser]')
        output_start = config_string.find('[output]')
        
        if parser_start == -1 or output_start == -1:
            raise ValueError("配置必须包含[parser]和[output]部分")
            
        # 提取parser模板 (在[parser]和[output]之间)
        parser_content = config_string[parser_start + len('[parser]'):output_start].strip()
        
        # 提取output模板 (从[output]到字符串结尾)
        output_content = config_string[output_start + len('[output]'):].strip()
        
        return cls(parser_content, output_content, all_functions)