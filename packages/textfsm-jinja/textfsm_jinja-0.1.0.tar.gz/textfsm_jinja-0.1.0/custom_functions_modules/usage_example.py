#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用用户自定义函数模块的示例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textfsm_jinja import TextProcessor


def main():
    print("=== 使用用户自定义函数模块示例 ===\n")
    
    # 定义模板
    template = """[parser]
Value name (\\S+)
Value value (\\S+)

Start
  ^${name} ${value} -> Record

[output]
original_name => {{ name }}
reversed_name => {{ reverse_string(name) }}
name_length => {{ get_string_length(name) }}
repeated_value => {{ repeat_string(value, 3) }}
is_value_numeric => {{ is_numeric(value) }}
original_value => {{ value }}
modified_value => {{ replace_char(value, 'o', '0') }}"""

    # 获取自定义函数模块的路径
    custom_module_path = os.path.join(
        os.path.dirname(__file__), 
        'my_custom_functions.py'
    )
    
    print("从用户自定义模块加载函数:")
    try:
        # 从用户自定义模块创建处理器
        processor = TextProcessor.from_config_string_with_module(
            template, 
            custom_functions_module=custom_module_path
        )
        
        text = "hello world"
        result = processor.process(text)
        print(result)
        print()
        
    except Exception as e:
        print(f"出错: {e}")
        print()
    
    print("同时使用默认函数和用户自定义函数:")
    try:
        # 使用默认函数和自定义函数
        template2 = """[parser]
Value number (\\d+)

Start
  ^${number} -> Record

[output]
original => {{ number }}
binary => {{ to_binary(number) }}
hex => {{ to_hex(number) }}
reversed => {{ reverse_string(number) }}
length => {{ get_string_length(number) }}"""
        
        processor2 = TextProcessor.from_config_string_with_module(
            template2, 
            custom_functions_module=custom_module_path
        )
        
        text = "42"
        result2 = processor2.process(text)
        print(result2)
        print()
        
    except Exception as e:
        print(f"出错: {e}")
        print()


if __name__ == "__main__":
    main()