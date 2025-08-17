#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试自定义函数模块功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from textfsm_jinja import TextProcessor


def main():
    print("测试自定义函数模块功能")
    print("=" * 30)
    
    # 创建一个简单的自定义函数模块内容
    custom_module_content = '''
def reverse_string(value):
    """反转字符串"""
    if isinstance(value, str):
        return value[::-1]
    return str(value)

def add_prefix(value, prefix="PREFIX_"):
    """添加前缀"""
    return prefix + str(value)
'''
    
    # 将自定义函数写入临时文件
    with open('temp_custom_functions.py', 'w', encoding='utf-8') as f:
        f.write(custom_module_content)
    
    # 定义模板
    template = """[parser]
Value name (\\S+)

Start
  ^${name} -> Record

[output]
original => {{ name }}
reversed => {{ reverse_string(name) }}
prefixed => {{ add_prefix(name) }}"""
    
    try:
        # 从外部模块创建处理器
        processor = TextProcessor.from_config_string_with_module(
            template, 
            custom_functions_module='temp_custom_functions.py'
        )
        
        text = "hello"
        result = processor.process(text)
        
        print("处理结果:")
        for item in result:
            for key, value in item.items():
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"出错: {e}")
    finally:
        # 清理临时文件
        if os.path.exists('temp_custom_functions.py'):
            os.remove('temp_custom_functions.py')


if __name__ == "__main__":
    main()