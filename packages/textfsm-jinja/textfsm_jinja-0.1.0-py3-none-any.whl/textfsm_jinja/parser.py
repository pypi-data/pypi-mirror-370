import textfsm
from io import StringIO


class TextFSMParser:
    """
    TextFSM解析器类，用于解析基于模板的半结构化文本
    """

    def __init__(self, template_content):
        """
        初始化解析器
        
        Args:
            template_content (str): TextFSM模板内容
        """
        self.template_content = template_content
        self.template = textfsm.TextFSM(StringIO(template_content))

    def parse(self, text):
        """
        解析文本
        
        Args:
            text (str): 要解析的文本
            
        Returns:
            list: 解析结果列表，每个元素是一个字典
        """
        parsed_data = self.template.ParseText(text)
        result = []
        for row in parsed_data:
            item = {}
            for i, header in enumerate(self.template.header):
                item[header] = row[i] if i < len(row) else None
            result.append(item)
        return result

    @classmethod
    def from_file(cls, template_file):
        """
        从文件加载模板
        
        Args:
            template_file (str): 模板文件路径
            
        Returns:
            TextFSMParser: 解析器实例
        """
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        return cls(template_content)