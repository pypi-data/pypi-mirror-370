#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TextFSM-Jinja 三种自定义函数方式使用示例

预期的文件结构：
.
├── three_ways_example.py   # 本脚本
├── three_ways_example.template  # 模板文件
└── three_ways_example.input     # 输入数据文件
"""

import sys
import os

# 获取当前脚本的绝对路径，并将其所在目录添加到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))  # 添加项目根目录到Python路径

from textfsm_jinja import TextProcessor


def multiply(x, y):
    """额外的自定义函数，用于演示参数传递的函数"""
    try:
        return int(x) * int(y)
    except (ValueError, TypeError):
        return 0


def main():
    print("=== TextFSM-Jinja 三种自定义函数方式使用示例 ===\n")
    
    # 构建模板文件路径并读取内容
    template_path = os.path.join(script_dir, 'three_ways_example.template')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"错误：模板文件未找到，请确认文件存在于: {template_path}")
        return
    
    # 通过参数传递额外的自定义函数
    extra_functions = {'multiply': multiply}
    
    # 创建处理器（使用模板中定义的所有三种方式的自定义函数）
    try:
        processor = TextProcessor.from_config_string(template_content, custom_functions=extra_functions)
    except Exception as e:
        print(f"错误：创建TextProcessor时出错 - {str(e)}")
        return
    
    # 构建输入文件路径并读取内容
    input_path = os.path.join(script_dir, 'three_ways_example.input')
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"错误：输入文件未找到，请确认文件存在于: {input_path}")
        return
    
    # 处理文本
    try:
        result = processor.process(input_text)
    except Exception as e:
        print(f"错误：处理文本时出错 - {str(e)}")
        return
    
    print("处理结果:")
    for i, record in enumerate(result):
        print(f"记录 {i+1}:")
        for key, value in record.items():
            print(f"  {key}: {value}")
        print()
    
    # 演示优先级：参数传递的函数 > 模板内定义的函数 > 外部模块函数
    print("=== 函数优先级演示 ===")
    
    # 创建一个演示优先级的模板
    priority_template = """[parser]
Value value (\d+)

Start
  ^${value} -> Record

[CUSTOM_FUNCTION]
CUSTOM_FUNCTION_PATH="examples/external_custom_functions.py"

[CUSTOM_FUNCTION_PY]
def test_func(value):
    return f"模板内定义的函数: {value}"

CUSTOM_FUNCTIONS = {
    'test_func': test_func,
}

[output]
result => {{ test_func(value) }}"""
    
    # 通过参数传递同名函数
    def test_func_override(value):
        return f"参数传递的函数: {value}"
    
    priority_functions = {'test_func': test_func_override}
    
    try:
        processor_priority = TextProcessor.from_config_string(priority_template, custom_functions=priority_functions)
        result_priority = processor_priority.process("123")
    except Exception as e:
        print(f"错误：处理优先级测试时出错 - {str(e)}")
        return
    
    print("优先级测试结果:")
    print(f"  {result_priority[0]['result']}")
    print("  (应该显示'参数传递的函数: 123'，因为参数传递的函数优先级最高)")


if __name__ == "__main__":
    main()