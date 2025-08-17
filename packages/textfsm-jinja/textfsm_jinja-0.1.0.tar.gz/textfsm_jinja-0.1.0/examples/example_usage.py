#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TextFSM-Jinja 使用示例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textfsm_jinja import TextProcessor


def example_basic():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 定义模板
    template = """[parser]
Value Key Col1 (\\d+)
Value Col2 (\\S+)
Value Col3 (\\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record

[output]
Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col5 => 
前缀: {{ Col3 }}-----
后缀"""

    # 创建处理器
    processor = TextProcessor.from_config_string(template)

    # 处理文本
    text = """123 abc def
456 ghi jkl"""

    result = processor.process(text)
    print(result)
    print()


def example_routes():
    """路由表处理示例"""
    print("=== 路由表处理示例 ===")
    
    route_template = """[parser]
Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)
Value nexthop_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value nexthop_port (\\S+)
Value tag (\\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} tag ${tag} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_port} -> Record

[output]
network => {{ ip_address }}/{{ mask }}
nexthop => {{ nexthop_address if nexthop_address else nexthop_port }}
tag => {{ tag if tag else 'None' }}"""

    processor = TextProcessor.from_config_string(route_template)
    
    route_text = """ip route-static 1.1.1.1 32 2.2.2.2
ip route-static 1.1.1.1 32 2.2.2.2 tag 300
ip route-static 1.1.1.1 32 null0"""
    
    result = processor.process(route_text)
    print(result)
    print()


def example_separate_templates():
    """分离模板示例"""
    print("=== 分离模板示例 ===")
    
    parser_template = """Value Key Col1 (\\d+)
Value Col2 (\\S+)
Value Col3 (\\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record"""

    output_template = """Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col3 => 
前缀: {{ Col3 }}
后缀"""

    processor = TextProcessor(parser_template, output_template)
    
    text = """123 abc def
456 ghi jkl"""
    
    result = processor.process(text)
    print(result)
    print()


if __name__ == "__main__":
    example_basic()
    example_routes()
    example_separate_templates()