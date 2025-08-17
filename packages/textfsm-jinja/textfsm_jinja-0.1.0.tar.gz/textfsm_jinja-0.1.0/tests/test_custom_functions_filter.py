#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试CUSTOM_FUNCTIONS过滤功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from textfsm_jinja import TextProcessor


def main():
    print("测试CUSTOM_FUNCTIONS过滤功能")
    print("=" * 40)
    
    # 定义模板，使用所有可能的函数
    template = """[parser]
Value text (\\S+)

Start
  ^${text} -> Record

[output]
original => {{ text }}
reversed => {{ reverse_string(text) }}
repeated => {{ repeat_string(text, 2) }}
capitalized => {{ capitalize_words(text) }}"""
    
    # 测试使用examples/external_custom_functions.py模块
    external_module_path = os.path.join(
        os.path.dirname(__file__), 
        'examples', 
        'external_custom_functions.py'
    )
    
    print("1. 测试从外部模块加载函数（受CUSTOM_FUNCTIONS限制）:")
    try:
        processor = TextProcessor.from_config_string_with_module(
            template, 
            custom_functions_module=external_module_path
        )
        
        text = "hello world"
        result = processor.process(text)
        
        print("处理结果:")
        for item in result:
            for key, value in item.items():
                print(f"  {key}: {value}")
        
        # 检查处理器中有哪些函数
        print(f"\n处理器中可用的自定义函数: {list(processor.custom_functions.keys())}")
        
    except Exception as e:
        print(f"出错: {e}")
    
    print("\n" + "=" * 40)
    
    # 创建一个没有CUSTOM_FUNCTIONS的模块进行对比测试
    simple_module_content = '''
def reverse_string(value):
    """反转字符串"""
    return value[::-1] if isinstance(value, str) else str(value)

def hidden_function(value):
    """这个函数不应该被加载，因为没有在CUSTOM_FUNCTIONS中定义"""
    return "hidden"
'''
    
    # 将简单模块写入临时文件
    with open('simple_test_module.py', 'w', encoding='utf-8') as f:
        f.write(simple_module_content)
    
    print("2. 测试没有CUSTOM_FUNCTIONS的模块（加载所有函数）:")
    try:
        processor2 = TextProcessor.from_config_string_with_module(
            template, 
            custom_functions_module='simple_test_module.py'
        )
        
        text = "test"
        result = processor2.process(text)
        
        print("处理结果:")
        for item in result:
            for key, value in item.items():
                print(f"  {key}: {value}")
        
        # 检查处理器中有哪些函数
        print(f"\n处理器中可用的自定义函数: {list(processor2.custom_functions.keys())}")
        
    except Exception as e:
        print(f"出错: {e}")
    finally:
        # 清理临时文件
        if os.path.exists('simple_test_module.py'):
            os.remove('simple_test_module.py')


if __name__ == "__main__":
    main()