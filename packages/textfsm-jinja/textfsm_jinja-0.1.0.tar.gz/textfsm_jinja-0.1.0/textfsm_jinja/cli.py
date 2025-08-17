#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TextFSM-Jinja 命令行工具
"""

import argparse
import sys
from .processor import TextProcessor


def main():
    parser = argparse.ArgumentParser(description='TextFSM-Jinja 文本解析和渲染工具')
    parser.add_argument('-t', '--template', required=True, 
                        help='模板文件路径 (包含[parser]和[output]部分)')
    parser.add_argument('-i', '--input', required=True, 
                        help='输入文本文件路径')
    parser.add_argument('-o', '--output', 
                        help='输出文件路径 (默认为标准输出)')
    
    args = parser.parse_args()
    
    # 读取模板文件
    try:
        with open(args.template, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到模板文件 '{args.template}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取模板文件时出错: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 读取输入文件
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{args.input}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取输入文件时出错: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 处理文本
    try:
        processor = TextProcessor.from_config_string(template_content)
        result = processor.process(input_text)
    except Exception as e:
        print(f"错误: 处理文本时出错: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 输出结果
    output_str = str(result)
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_str)
        except Exception as e:
            print(f"错误: 写入输出文件时出错: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_str)


if __name__ == '__main__':
    main()