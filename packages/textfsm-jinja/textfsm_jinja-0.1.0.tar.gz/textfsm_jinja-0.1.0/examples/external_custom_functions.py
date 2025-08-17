"""
外部自定义函数示例文件

这个文件展示了如何创建外部的自定义函数模块，
这些函数可以在TextFSM-Jinja模板中使用。
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


def capitalize_words(value):
    """将字符串中每个单词的首字母大写"""
    if isinstance(value, str):
        return ' '.join(word.capitalize() for word in value.split())
    return str(value)


def extract_numbers(value):
    """从字符串中提取所有数字"""
    import re
    if isinstance(value, str):
        numbers = re.findall(r'\d+', value)
        return ','.join(numbers) if numbers else ''
    return ''


def count_words(value):
    """计算字符串中的单词数"""
    if isinstance(value, str):
        return len(value.split())
    return 0


def wrap_text(value, width=50):
    """将文本按指定宽度换行"""
    import textwrap
    if isinstance(value, str):
        return '\n'.join(textwrap.wrap(value, width))
    return str(value)


def remove_spaces(value):
    """移除字符串中的所有空格"""
    if isinstance(value, str):
        return value.replace(' ', '')
    return str(value)


# 这个字典定义了要导出的函数列表
# 只有在这个字典中列出的函数才会被加载和使用
# 字典的键是函数在模板中使用的名称，值是函数对象本身
CUSTOM_FUNCTIONS = {
    'reverse_string': reverse_string,
    'repeat_string': repeat_string,
    'capitalize_words': capitalize_words,
}