"""
用户自定义函数模块示例

这个模块展示了用户如何创建自己的自定义函数模块，
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


def get_string_length(value):
    """获取字符串长度"""
    return len(str(value))


def replace_char(value, old, new):
    """替换字符串中的字符"""
    return str(value).replace(old, new)


def is_numeric(value):
    """检查字符串是否为数字"""
    try:
        int(value)
        return True
    except ValueError:
        return False


# 可选：定义要导出的函数列表
# 如果定义了这个字典，只有其中列出的函数会被加载
# CUSTOM_FUNCTIONS = {
#     'reverse_string': reverse_string,
#     'repeat_string': repeat_string,
#     'get_string_length': get_string_length,
# }