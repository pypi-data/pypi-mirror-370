#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
外部自定义函数使用示例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textfsm_jinja import TextProcessor


def main():
    print("=== 外部自定义函数使用示例 ===\n")
    
    # 定义模板
    template = """[parser]
Value name (\S+)
Value value (\d+)

Start
  ^${name} ${value} -> Record

[output]
original_name => {{ name }}
reversed_name => {{ reverse_string(name) }}
repeated_value => {{ repeat_string(value, 3) }}
is_name_empty => {{ is_empty(name) }}
capitalized => {{ capitalize_words(name) }}"""
    
    # 从外部模块创建处理器
    module_path = os.path.join(os.path.dirname(__file__), 'external_custom_functions.py')
    processor = TextProcessor.from_config_string_with_module(
        template, 
        custom_functions_module=module_path
    )
    
    # 处理文本
    text = "hello 42"
    result = processor.process(text)
    
    print("处理结果:")
    for item in result:
        for key, value in item.items():
            print(f"  {key}: {value}")
    
    print("\n=== 混合使用默认函数和外部函数 ===")
    
    # 混合使用默认函数和外部函数
    mixed_template = """[parser]
Value number (\d+)

Start
  ^${number} -> Record

[output]
original => {{ number }}
binary => {{ to_binary(number) }}      # 默认函数
hex => {{ to_hex(number) }}            # 默认函数
reversed => {{ reverse_string(number) }} # 外部函数"""
    
    processor_mixed = TextProcessor.from_config_string_with_module(
        mixed_template,
        custom_functions_module=module_path
    )
    
    text_mixed = "42"
    result_mixed = processor_mixed.process(text_mixed)
    
    print("混合使用结果:")
    for item in result_mixed:
        for key, value in item.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()