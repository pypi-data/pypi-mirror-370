#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TextFSM-Jinja 单元测试
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textfsm_jinja import TextFSMParser, Jinja2Renderer, TextProcessor


def multiply(value, multiplier):
    """测试用的自定义函数"""
    try:
        return int(value) * int(multiplier)
    except (ValueError, TypeError):
        return 0


class TestTextFSMParser(unittest.TestCase):
    """TextFSM解析器测试"""

    def test_parse_basic(self):
        """测试基本解析功能"""
        template = """Value Col1 (\\d+)
Value Col2 (\\S+)
Value Col3 (\\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record"""

        parser = TextFSMParser(template)
        text = "123 abc def"
        result = parser.parse(text)
        
        expected = [{'Col1': '123', 'Col2': 'abc', 'Col3': 'def'}]
        self.assertEqual(result, expected)


class TestJinja2Renderer(unittest.TestCase):
    """Jinja2渲染器测试"""

    def test_render_basic(self):
        """测试基本渲染功能"""
        template = """Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col3 => 
前缀: {{ Col3 }}
后缀"""
        
        renderer = Jinja2Renderer(template)
        data = [{'Col1': '123', 'Col2': 'abc', 'Col3': 'def'}]
        result = renderer.render(data)
        
        expected = [{
            'Col1': '123',
            'Col2': 'ABC', 
            'Col3': '前缀: def\n后缀'
        }]
        self.assertEqual(result, expected)
        
    def test_render_with_custom_functions(self):
        """测试使用自定义函数渲染"""
        template = """Col1 => {{ multiply(Col1, 2) }}
Col2 => {{ Col2|upper }}"""
        
        custom_functions = {'multiply': multiply}
        renderer = Jinja2Renderer(template, custom_functions)
        data = [{'Col1': '123', 'Col2': 'abc'}]
        result = renderer.render(data)
        
        expected = [{
            'Col1': '246',
            'Col2': 'ABC'
        }]
        self.assertEqual(result, expected)
        
    def test_add_custom_function(self):
        """测试动态添加自定义函数"""
        template = """Col1 => {{ multiply(Col1, 3) }}"""
        
        renderer = Jinja2Renderer(template)
        renderer.add_custom_function('multiply', multiply)
        data = [{'Col1': '5'}]
        result = renderer.render(data)
        
        expected = [{'Col1': '15'}]
        self.assertEqual(result, expected)


class TestTextProcessor(unittest.TestCase):
    """文本处理器测试"""

    def test_process_basic(self):
        """测试基本处理功能"""
        config = """[parser]
Value Col1 (\\d+)
Value Col2 (\\S+)
Value Col3 (\\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record

[output]
Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col3 => 
前缀: {{ Col3 }}
后缀"""

        processor = TextProcessor.from_config_string(config)
        text = "123 abc def"
        result = processor.process(text)
        
        expected = [{
            'Col1': '123',
            'Col2': 'ABC',
            'Col3': '前缀: def\n后缀'
        }]
        self.assertEqual(result, expected)
        
    def test_process_with_custom_functions(self):
        """测试使用自定义函数处理"""
        config = """[parser]
Value Col1 (\\d+)
Value Col2 (\\S+)

Start
  ^${Col1} ${Col2} -> Record

[output]
Col1 => {{ multiply(Col1, 2) }}
Col2 => {{ Col2|upper }}"""
        
        custom_functions = {'multiply': multiply}
        processor = TextProcessor.from_config_string(config, custom_functions)
        text = "123 abc"
        result = processor.process(text)
        
        expected = [{
            'Col1': '246',
            'Col2': 'ABC'
        }]
        self.assertEqual(result, expected)
        
    def test_add_custom_function_to_processor(self):
        """测试向处理器动态添加自定义函数"""
        config = """[parser]
Value value (\\d+)

Start
  ^${value} -> Record

[output]
result => {{ multiply(value, 4) }}"""
        
        processor = TextProcessor.from_config_string(config)
        processor.add_custom_function('multiply', multiply)
        text = "5"
        result = processor.process(text)
        
        expected = [{'result': '20'}]
        self.assertEqual(result, expected)
        
    def test_load_custom_functions_from_module(self):
        """测试从外部模块加载自定义函数"""
        # 创建一个临时的自定义函数模块用于测试
        test_module_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'examples', 
            'external_custom_functions.py'
        )
        
        if os.path.exists(test_module_path):
            functions = TextProcessor.load_custom_functions_from_module(test_module_path)
            self.assertIn('reverse_string', functions)
            self.assertIn('repeat_string', functions)
            self.assertTrue(callable(functions['reverse_string']))
            self.assertTrue(callable(functions['repeat_string']))
        
    def test_process_with_module_functions(self):
        """测试使用外部模块函数处理"""
        test_module_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'examples', 
            'external_custom_functions.py'
        )
        
        if os.path.exists(test_module_path):
            config = """[parser]
Value text (\\S+)

Start
  ^${text} -> Record

[output]
original => {{ text }}
reversed => {{ reverse_string(text) }}"""
            
            processor = TextProcessor.from_config_string_with_module(
                config,
                custom_functions_module=test_module_path
            )
            
            text = "hello"
            result = processor.process(text)
            
            expected = [{
                'original': 'hello',
                'reversed': 'olleh'
            }]
            self.assertEqual(result, expected)
            
    def test_custom_functions_filter(self):
        """测试CUSTOM_FUNCTIONS过滤功能"""
        # 创建一个带CUSTOM_FUNCTIONS字典的临时模块
        temp_module_content = '''
def func_a(value):
    return "A_" + str(value)
    
def func_b(value):
    return "B_" + str(value)
    
def internal_func(value):
    return "internal"
    
CUSTOM_FUNCTIONS = {
    "func_a": func_a,
    "func_b": func_b
}
'''
        
        # 写入临时模块文件
        temp_module_path = 'temp_test_module.py'
        with open(temp_module_path, 'w', encoding='utf-8') as f:
            f.write(temp_module_content)
            
        try:
            # 测试加载函数
            functions = TextProcessor.load_custom_functions_from_module(temp_module_path)
            
            # 检查只有CUSTOM_FUNCTIONS中列出的函数被加载
            self.assertIn('func_a', functions)
            self.assertIn('func_b', functions)
            self.assertNotIn('internal_func', functions)
            self.assertEqual(len(functions), 2)
            
            # 测试在处理器中使用
            config = """[parser]
Value value (\\S+)

Start
  ^${value} -> Record

[output]
value => {{ value }}
a => {{ func_a(value) }}
b => {{ func_b(value) }}"""
            
            processor = TextProcessor.from_config_string_with_module(
                config,
                custom_functions_module=temp_module_path
            )
            
            result = processor.process("test")
            expected = [{
                'value': 'test',
                'a': 'A_test',
                'b': 'B_test'
            }]
            self.assertEqual(result, expected)
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_module_path):
                os.remove(temp_module_path)
                
    def test_three_ways_custom_functions(self):
        """测试三种自定义函数方式"""
        # 创建测试模板，包含三种方式的自定义函数
        template = """[parser]
Value text (\\S+)

Start
  ^${text} -> Record

[CUSTOM_FUNCTION]
CUSTOM_FUNCTION_PATH="examples/external_custom_functions.py"

[CUSTOM_FUNCTION_PY]
def test_func(value):
    return f"模板内定义: {value}"

CUSTOM_FUNCTIONS = {
    'test_func': test_func,
}

[output]
result => {{ test_func(text) }}
reversed => {{ reverse_string(text) }}"""
        
        # 通过参数传递同名函数（应该覆盖模板内定义的函数）
        def override_func(value):
            return f"参数传递: {value}"
        
        custom_functions = {'test_func': override_func}
        
        processor = TextProcessor.from_config_string(template, custom_functions=custom_functions)
        result = processor.process("hello")
        
        # 验证参数传递的函数优先级最高
        self.assertEqual(result[0]['result'], "参数传递: hello")
        # 验证外部模块函数可以正常加载
        self.assertEqual(result[0]['reversed'], "olleh")


if __name__ == "__main__":
    unittest.main()