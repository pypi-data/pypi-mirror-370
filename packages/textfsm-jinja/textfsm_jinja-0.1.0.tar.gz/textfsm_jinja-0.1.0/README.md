# TextFSM-Jinja

一个基于TextFSM和Jinja2的文本解析和渲染库。

## 目录

- [简介](#简介)
- [功能特点](#功能特点)
- [安装](#安装)
  - [使用虚拟环境（推荐）](#使用虚拟环境推荐)
  - [直接安装](#直接安装)
- [快速开始](#快速开始)
- [核心类介绍](#核心类介绍)
  - [TextFSMParser 类](#textfsmparser-类)
  - [Jinja2Renderer 类](#jinja2renderer-类)
  - [TextProcessor 类](#textprocessor-类)
- [使用方法](#使用方法)
  - [基本用法](#基本用法)
  - [自定义函数](#自定义函数)
  - [三种自定义函数方式](#三种自定义函数方式)
- [编写自定义函数模块](#编写自定义函数模块)
- [图形界面](#图形界面)
- [模板语法](#模板语法)
- [运行测试](#运行测试)
- [示例](#示例)
- [内置自定义函数](#内置自定义函数)
- [致谢](#致谢)
- [贡献](#贡献)
- [许可证](#许可证)

## 简介

TextFSM-Jinja是一个Python库，结合了TextFSM的文本解析能力和Jinja2的模板渲染功能。它允许你使用TextFSM模板解析半结构化文本，然后使用Jinja2模板对解析结果进行后处理和格式化。

## 功能特点

- 使用TextFSM模板解析半结构化文本
- 使用Jinja2模板对解析结果进行渲染和格式化
- 支持自定义输出格式
- 易于使用的API
- 提供图形界面用于模板验证
- 支持自定义函数扩展
- 支持从外部Python模块加载自定义函数
- 支持三种方式定义自定义函数

## 安装

### 使用虚拟环境（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd textfsm-jinja

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# 安装依赖
pip install -e .
```

### 直接安装

```bash
pip install textfsm-jinja
```

## 快速开始

```python
from textfsm_jinja import TextProcessor

# 定义模板
template = """
[parser]
Value Key Col1 (\d+)
Value Col2 (\S+)
Value Col3 (\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record

[output]
Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col3 => 
前缀: {{ Col3 }}
后缀
"""

# 创建处理器
processor = TextProcessor.from_config_string(template)

# 处理文本
text = """
123 abc def
456 ghi jkl
"""

result = processor.process(text)
print(result)
```

## 核心类介绍

### TextFSMParser 类

TextFSMParser 类用于解析基于TextFSM模板的半结构化文本。

#### 主要方法：

- `__init__(self, template_content)`: 使用TextFSM模板内容初始化解析器
- `parse(self, text)`: 解析文本并返回结构化数据
- `from_file(cls, template_file)`: 从文件加载模板并创建解析器实例

#### 使用示例：

```python
from textfsm_jinja import TextFSMParser

# 直接使用模板内容
template = """
Value Col1 (\d+)
Value Col2 (\S+)

Start
  ^${Col1} ${Col2} -> Record
"""

parser = TextFSMParser(template)
text = "123 abc"
result = parser.parse(text)
# result: [{'Col1': '123', 'Col2': 'abc'}]
```

### Jinja2Renderer 类

Jinja2Renderer 类用于根据Jinja2模板渲染数据。

#### 主要方法：

- `__init__(self, output_template, custom_functions=None)`: 使用输出模板定义初始化渲染器
- `render(self, data)`: 渲染数据并返回格式化结果
- `add_custom_function(self, name, func)`: 添加自定义函数到渲染环境

#### 使用示例：

```python
from textfsm_jinja import Jinja2Renderer

# 定义自定义函数
def multiply(value, multiplier):
    try:
        return int(value) * int(multiplier)
    except (ValueError, TypeError):
        return 0

# 定义输出模板
output_template = """
Col1 => {{ multiply(Col1, 2) }}
Col2 => {{ Col2|upper }}
"""

# 创建渲染器并添加自定义函数
custom_functions = {'multiply': multiply}
renderer = Jinja2Renderer(output_template, custom_functions)
data = [{'Col1': '123', 'Col2': 'abc'}]
result = renderer.render(data)
# result: [{'Col1': '246', 'Col2': 'ABC'}]
```

### TextProcessor 类

TextProcessor 类整合了TextFSM解析和Jinja2渲染功能，提供统一的处理接口。

#### 主要方法：

- `__init__(self, parser_template, renderer_template, custom_functions=None, load_default_functions=True)`: 使用解析模板和渲染模板初始化处理器
- `process(self, text)`: 处理文本：解析然后渲染
- `from_config_string(cls, config_string, custom_functions=None, load_default_functions=True)`: 从配置字符串创建处理器
- `from_config_string_with_module(cls, config_string, custom_functions_module=None, custom_functions=None, load_default_functions=True)`: 从配置字符串创建处理器，并可选择从外部模块加载自定义函数
- `add_custom_function(self, name, func)`: 添加自定义函数到处理器
- `load_custom_functions_from_module(cls, module_path)`: 从外部Python模块文件加载自定义函数

#### 使用示例：

```python
from textfsm_jinja import TextProcessor

# 定义自定义函数
def format_ip(ip, mask):
    return f"{ip}/{mask}"

# 定义配置
config = """
[parser]
Value ip_address (\d+\.\d+\.\d+\.\d+)
Value mask (\d+)

Start
  ^${ip_address} ${mask} -> Record

[output]
network => {{ format_ip(ip_address, mask) }}
"""

# 创建处理器并添加自定义函数
custom_functions = {'format_ip': format_ip}
processor = TextProcessor.from_config_string(config, custom_functions)
text = "192.168.1.1 24"
result = processor.process(text)
# result: [{'network': '192.168.1.1/24'}]
```

## 使用方法

### 基本用法

```python
from textfsm_jinja import TextProcessor

# 定义模板
template = """
[parser]
Value Key Col1 (\d+)
Value Col2 (\S+)
Value Col3 (\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record

[output]
Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col3 => 
前缀: {{ Col3 }}
后缀
"""

# 创建处理器
processor = TextProcessor.from_config_string(template)

# 处理文本
text = """
123 abc def
456 ghi jkl
"""

result = processor.process(text)
print(result)
```

### 高级用法

```python
# 处理路由表等复杂文本
route_template = """
[parser]
Value ip_address (\d+\.\d+\.\d+\.\d+)
Value mask (\d+)
Value nexthop_address (\d+\.\d+\.\d+\.\d+)
Value nexthop_port (\S+)
Value tag (\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} tag ${tag} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_port} -> Record

[output]
network => {{ ip_address }}/{{ mask }}
nexthop => {{ nexthop_address if nexthop_address else nexthop_port }}
tag => {{ tag if tag else 'None' }}
"""

processor = TextProcessor.from_config_string(route_template)
```

### 自定义函数

TextFSM-Jinja支持多种方式添加自定义函数来扩展模板功能。

#### 通过参数传递函数

```python
from textfsm_jinja import TextProcessor

def multiply(x, y):
    return int(x) * int(y)

# 通过参数传递自定义函数
custom_functions = {'multiply': multiply}
processor = TextProcessor.from_config_string(template, custom_functions=custom_functions)
```

#### 外部自定义函数模块

```python
from textfsm_jinja import TextProcessor

# 假设你有一个自定义函数模块文件: my_custom_functions.py
# 在模板中使用外部模块定义的函数
template = """
[parser]
Value name (\S+)
Value value (\d+)

Start
  ^${name} ${value} -> Record

[output]
original => {{ name }}
reversed => {{ reverse_string(name) }}  # 来自外部模块的函数
binary => {{ to_binary(value) }}        # 来自默认函数库的函数
"""

# 从外部模块创建处理器
processor = TextProcessor.from_config_string_with_module(
    template, 
    custom_functions_module="path/to/my_custom_functions.py"
)

text = "hello 42"
result = processor.process(text)
```

### 三种自定义函数方式

TextFSM-Jinja 支持三种定义和使用自定义函数的方式，按照优先级从高到低排列：

1. **通过参数传递的函数** - 优先级最高
2. **在模板中直接定义的函数** 
3. **通过路径指定的外部模块函数** - 优先级最低

#### 方式1：通过参数传递函数

```python
from textfsm_jinja import TextProcessor

def multiply(x, y):
    return int(x) * int(y)

# 通过参数传递自定义函数
custom_functions = {'multiply': multiply}
processor = TextProcessor.from_config_string(template, custom_functions=custom_functions)
```

#### 方式2：在模板中直接定义函数

```text
[parser]
Value text (\S+)

Start
  ^${text} -> Record

[CUSTOM_FUNCTION_PY]
import re 

def repeat_string(value, count):
    """重复字符串指定次数"""
    try:
        return str(value) * int(count)
    except (ValueError, TypeError):
        return str(value)

def custom_upper(value):
    """自定义大写函数"""
    if isinstance(value, str):
        return value.upper()
    return str(value)

CUSTOM_FUNCTIONS = {
    'repeat_string': repeat_string,
    'custom_upper': custom_upper,
}

[output]
original => {{ text }}
upper => {{ custom_upper(text) }}
repeated => {{ repeat_string(text, 3) }}
```

#### 方式3：通过路径指定外部模块

```text
[parser]
Value text (\S+)

Start
  ^${text} -> Record

[CUSTOM_FUNCTION]
CUSTOM_FUNCTION_PATH="path/to/my_custom_functions.py"

[output]
reversed => {{ reverse_string(text) }}
```

#### 完整示例（三种方式结合使用）

```text
[parser]
Value text (\S+)
Value number (\d+)

Start
  ^${text} ${number} -> Record

[CUSTOM_FUNCTION]
CUSTOM_FUNCTION_PATH="examples/external_custom_functions.py"

[CUSTOM_FUNCTION_PY]
import re 

def repeat_string(value, count):
    """重复字符串指定次数"""
    try:
        return str(value) * int(count)
    except (ValueError, TypeError):
        return str(value)

def custom_upper(value):
    """自定义大写函数"""
    if isinstance(value, str):
        return value.upper()
    return str(value)

CUSTOM_FUNCTIONS = {
    'repeat_string': repeat_string,
    'custom_upper': custom_upper,
}

[output]
original_text => {{ text }}
upper_text => {{ custom_upper(text) }}
repeated_text => {{ repeat_string(text, number) }}
reversed_text => {{ reverse_string(text) }}  # 来自外部模块
capitalized_words => {{ capitalize_words(text) }}  # 来自外部模块
```

## 编写自定义函数模块

要创建可在TextFSM-Jinja模板中使用的自定义函数模块，请遵循以下要求：

### 基本要求

1. **文件格式**：创建一个标准的Python `.py` 文件
2. **函数定义**：每个自定义函数应该是独立的Python函数
3. **函数命名**：使用清晰、描述性的函数名
4. **错误处理**：函数应包含适当的错误处理机制

### 函数编写规范

```python
# my_custom_functions.py - 自定义函数模块示例

def my_function(param1, param2=None):
    """
    函数文档说明
    
    Args:
        param1: 第一个参数
        param2: 第二个参数（可选）
        
    Returns:
        处理结果
    """
    try:
        # 函数逻辑
        result = do_something(param1, param2)
        return result
    except Exception as e:
        # 错误处理
        return None

def another_function(value):
    """另一个自定义函数"""
    # 简单的函数逻辑
    return str(value).upper()
```

### 函数设计建议

1. **参数处理**：
   - 函数应能处理各种类型的输入参数
   - 提供合理的默认值
   - 包含类型转换和验证

2. **返回值**：
   - 返回字符串或数字类型，便于在模板中使用
   - 避免返回复杂对象

3. **错误处理**：
   - 使用try/except处理可能的异常
   - 出错时返回合理的默认值

### 控制函数导出

通过定义 `CUSTOM_FUNCTIONS` 字典，可以精确控制哪些函数可以被TextFSM-Jinja加载和使用：

```python
# my_custom_functions.py
"""
自定义函数模块示例
"""

def reverse_string(value):
    """反转字符串"""
    if isinstance(value, str):
        return value[::-1]
    return str(value)

def repeat_string(value, count):
    """重复字符串指定次数"""
    try:
        return str(value) * int(count)
    except (ValueError, TypeError):
        return str(value)

def internal_helper(value):
    """内部辅助函数，不会被导出"""
    return value.strip()

# 定义要导出的函数列表
# 只有在这个字典中列出的函数才会被加载和使用
# 字典的键是函数在模板中使用的名称，值是函数对象本身
CUSTOM_FUNCTIONS = {
    'reverse_string': reverse_string,
    'repeat_string': repeat_string,
}
```

在上面的示例中，只有 `reverse_string` 和 `repeat_string` 函数会被加载，而 `internal_helper` 函数不会被导出，因为它没有在 `CUSTOM_FUNCTIONS` 字典中列出。

这种方式允许您：
1. 在模块中定义多个函数，但只导出需要的函数
2. 避免意外导出内部辅助函数
3. 精确控制模板中可用的函数

### 示例自定义函数模块

```python
# my_custom_functions.py
"""
自定义函数模块示例
"""

def reverse_string(value):
    """反转字符串"""
    if isinstance(value, str):
        return value[::-1]
    return str(value)

def repeat_string(value, count):
    """重复字符串指定次数"""
    try:
        return str(value) * int(count)
    except (ValueError, TypeError):
        return str(value)

def format_mac_address(mac):
    """格式化MAC地址"""
    # 移除所有非十六进制字符
    clean_mac = ''.join(c for c in mac if c.lower() in '0123456789abcdef')
    
    # 确保是12个字符
    if len(clean_mac) != 12:
        return mac
    
    # 格式化为标准形式
    return ':'.join(clean_mac[i:i+2] for i in range(0, 12, 2))

def is_valid_ip(ip):
    """检查IP地址是否有效"""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# 定义要导出的函数列表
CUSTOM_FUNCTIONS = {
    'reverse_string': reverse_string,
    'repeat_string': repeat_string,
    'format_mac_address': format_mac_address,
    'is_valid_ip': is_valid_ip
}
```

### 使用自定义函数模块

```python
from textfsm_jinja import TextProcessor

# 模板中使用自定义函数
template = """
[parser]
Value device_name (\S+)
Value mac_address ([0-9a-fA-F:]+)
Value ip_address (\d+\.\d+\.\d+\.\d+)

Start
  ^${device_name} ${mac_address} ${ip_address} -> Record

[output]
device => {{ device_name }}
formatted_mac => {{ format_mac_address(mac_address) }}
is_valid_ip => {{ is_valid_ip(ip_address) }}
reversed_name => {{ reverse_string(device_name) }}
"""

# 从外部模块创建处理器
processor = TextProcessor.from_config_string_with_module(
    template, 
    custom_functions_module="path/to/my_custom_functions.py"
)

text = "Router1 001122334455 192.168.1.1"
result = processor.process(text)
```

## 图形界面

TextFSM-Jinja 还提供了一个图形用户界面，用于方便地测试和验证模板。

### 启动GUI

```bash
# 使用命令行工具启动
textfsm-jinja-gui

# 或者直接运行Python脚本
python start_gui.py
```

### GUI功能

1. **模板编辑**：在左侧文本区域编辑TextFSM-Jinja模板
2. **输入文本**：在左侧下方区域输入要处理的文本
3. **处理结果**：在右侧区域查看处理结果
4. **示例加载**：从"示例"菜单加载预定义的示例
5. **文件操作**：从"文件"菜单打开模板和输入文件

## 模板语法

### Parser部分

Parser部分使用标准的TextFSM语法：

```
[parser]
Value Key Col1 (\d+)
Value Col2 (\S+)
Value Col3 (\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record
```

### Output部分

Output部分使用Jinja2语法定义输出格式：

```
[output]
Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col3 => 
多行
模板
内容: {{ Col3 }}
结束
```

## 运行测试

```bash
# 运行所有测试
python -m unittest tests.test_textfsm_jinja

# 或者直接运行测试文件
python tests/test_textfsm_jinja.py
```

## 示例

查看 `examples/` 目录获取更多使用示例:
- `examples/basic/` - 基本文本解析示例
- `examples/route/` - 路由表解析示例
- `examples/example_usage.py` - 代码使用示例
- `examples/custom_functions_example.py` - 自定义函数使用示例
- `examples/external_functions_example.py` - 外部自定义函数使用示例
- `examples/three_ways_example.py` - 三种自定义函数方式使用示例

## 内置自定义函数

TextFSM-Jinja 不再提供内置的自定义函数。所有自定义函数都需要用户自行定义并通过以下方式之一提供：

1. 通过参数传递给处理器
2. 在模板中直接定义（使用[CUSTOM_FUNCTION_PY]部分）
3. 通过外部模块文件提供（使用[CUSTOM_FUNCTION]部分）

## 致谢

本项目使用了以下优秀的开源项目：

- [TextFSM](https://github.com/google/textfsm) - Google开发的模板驱动的文本解析器
- [Jinja2](https://palletsprojects.com/p/jinja/) - 现代、设计友好的Python模板语言

感谢这些项目的开发者们为我们提供了如此强大的工具。

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT