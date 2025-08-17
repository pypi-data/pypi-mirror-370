#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TextFSM-Jinja 自定义函数使用示例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textfsm_jinja import TextProcessor


# 定义一些自定义函数
def multiply(value, multiplier):
    """将值乘以指定的倍数"""
    try:
        return int(value) * int(multiplier)
    except (ValueError, TypeError):
        return 0


def format_ip(ip_address, mask=None):
    """格式化IP地址，可选择添加子网掩码"""
    if mask:
        return f"{ip_address}/{mask}"
    return ip_address


def to_binary(value):
    """将数字转换为二进制表示"""
    try:
        return bin(int(value))
    except (ValueError, TypeError):
        return "0b0"


def custom_upper(value):
    """自定义大写函数"""
    if isinstance(value, str):
        return value.upper()
    return str(value)


def main():
    print("=== TextFSM-Jinja 自定义函数示例 ===\n")
    
    # 定义模板
    template = """[parser]
Value Col1 (\\d+)
Value Col2 (\\S+)
Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)

Start
  ^${Col1} ${Col2} ${ip_address} ${mask} -> Record

[output]
Col1 => {{ multiply(Col1, 2) }}
Col2 => {{ custom_upper(Col2) }}
ip_info => {{ format_ip(ip_address, mask) }}
binary => {{ to_binary(Col1) }}
combined => {{ Col1 }} * 3 = {{ multiply(Col1, 3) }}"""

    # 创建自定义函数字典
    custom_functions = {
        'multiply': multiply,
        'format_ip': format_ip,
        'to_binary': to_binary,
        'custom_upper': custom_upper
    }

    # 方法1: 在创建处理器时传递自定义函数
    print("方法1: 在创建处理器时传递自定义函数")
    processor1 = TextProcessor.from_config_string(template, custom_functions)
    
    text = "123 abc 192.168.1.1 24"
    result1 = processor1.process(text)
    print(result1)
    print()

    # 方法2: 使用add_custom_function方法添加自定义函数
    print("方法2: 使用add_custom_function方法添加自定义函数")
    processor2 = TextProcessor.from_config_string(template)
    
    # 逐个添加自定义函数
    processor2.add_custom_function('multiply', multiply)
    processor2.add_custom_function('format_ip', format_ip)
    processor2.add_custom_function('to_binary', to_binary)
    processor2.add_custom_function('custom_upper', custom_upper)
    
    result2 = processor2.process(text)
    print(result2)
    print()

    # 方法3: 处理多个记录
    print("方法3: 处理多个记录")
    multi_line_text = """123 abc 192.168.1.1 24
456 def 10.0.0.1 16
789 ghi 172.16.0.1 12"""
    
    result3 = processor1.process(multi_line_text)
    for i, record in enumerate(result3):
        print(f"记录 {i+1}: {record}")
    print()

    # 方法4: 在模板中使用复杂的自定义函数组合
    print("方法4: 复杂的自定义函数组合")
    complex_template = """[parser]
Value number (\\d+)

Start
  ^${number} -> Record

[output]
original => {{ number }}
squared => {{ multiply(number, number) }}
binary => {{ to_binary(number) }}
description => 原始值 {{ number }} 的平方是 {{ multiply(number, number) }}, 二进制表示为 {{ to_binary(number) }}"""
    
    processor4 = TextProcessor.from_config_string(complex_template, custom_functions)
    result4 = processor4.process("42")
    print(result4)


if __name__ == "__main__":
    main()