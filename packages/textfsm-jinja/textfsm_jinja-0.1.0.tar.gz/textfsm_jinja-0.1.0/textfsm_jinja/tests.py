#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TextFSM-Jinja 单元测试
"""

import unittest
from textfsm_jinja import TextFSMParser, Jinja2Renderer, TextProcessor


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


if __name__ == "__main__":
    unittest.main()