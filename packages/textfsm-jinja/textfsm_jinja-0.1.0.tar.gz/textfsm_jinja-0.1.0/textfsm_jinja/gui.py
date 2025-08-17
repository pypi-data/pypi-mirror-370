import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .processor import TextProcessor


class TextFSMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TextFSM-Jinja GUI")
        self.root.geometry("1000x700")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建控件
        self.create_widgets()
        
        # 设置示例目录路径
        self.examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
        
        # 初始化自定义函数（示例）
        self.custom_functions = {}
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开模板", command=self.open_template)
        file_menu.add_command(label="打开输入文本", command=self.open_input)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 示例菜单
        example_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="示例", menu=example_menu)
        example_menu.add_command(label="基本示例", command=lambda: self.load_example('basic'))
        example_menu.add_command(label="路由表示例", command=lambda: self.load_example('route'))
        example_menu.add_command(label="自定义函数示例", command=lambda: self.load_example('custom_functions'))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_widgets(self):
        # 标题
        title_label = ttk.Label(self.main_frame, text="TextFSM-Jinja GUI", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 控制按钮
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="处理文本", command=self.process_text)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清空", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 创建左右两个主要区域
        # 左侧区域 - 模板和输入文本
        left_frame = ttk.LabelFrame(self.main_frame, text="模板和输入", padding="10")
        left_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(3, weight=1)
        
        # 模板标签和文本框
        template_label = ttk.Label(left_frame, text="模板:")
        template_label.grid(row=0, column=0, sticky=(tk.W), pady=(0, 5))
        
        self.template_text = scrolledtext.ScrolledText(left_frame, width=50, height=15)
        self.template_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.template_text.insert(tk.END, """[parser]
Value Col1 (\\d+)
Value Col2 (\\S+)
Value Col3 (\\S+)

Start
  ^${Col1} ${Col2} ${Col3} -> Record

[output]
Col1 => {{ Col1 }}
Col2 => {{ Col2|upper }}
Col3 => 
前缀: {{ Col3 }}
后缀""")
        
        # 输入文本标签和文本框
        input_label = ttk.Label(left_frame, text="输入文本:")
        input_label.grid(row=2, column=0, sticky=(tk.W), pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(left_frame, width=50, height=10)
        self.input_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.input_text.insert(tk.END, """123 abc def
456 ghi jkl""")
        
        # 右侧区域 - 结果显示
        right_frame = ttk.LabelFrame(self.main_frame, text="处理结果", padding="10")
        right_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(right_frame, width=50, height=30)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.result_text.insert(tk.END, "处理结果将显示在这里...")
        
    def process_text(self):
        template_content = self.template_text.get("1.0", tk.END).strip()
        input_content = self.input_text.get("1.0", tk.END).strip()
        
        if not template_content:
            messagebox.showerror("错误", "请提供模板内容")
            return
            
        if not input_content:
            messagebox.showerror("错误", "请提供输入文本")
            return
            
        try:
            # 创建带有自定义函数的处理器
            processor = TextProcessor.from_config_string(template_content, self.custom_functions)
            result = processor.process(input_content)
            
            # 格式化结果以便显示
            formatted_result = json.dumps(result, ensure_ascii=False, indent=2)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", formatted_result)
            
        except Exception as e:
            messagebox.showerror("处理错误", f"处理文本时出错:\n{str(e)}")
            
    def clear_all(self):
        self.template_text.delete("1.0", tk.END)
        self.input_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "处理结果将显示在这里...")
        
    def open_template(self):
        file_path = filedialog.askopenfilename(
            title="选择模板文件",
            filetypes=[("Template files", "*.template"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.template_text.delete("1.0", tk.END)
                    self.template_text.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件:\n{str(e)}")
                
    def open_input(self):
        file_path = filedialog.askopenfilename(
            title="选择输入文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.input_text.delete("1.0", tk.END)
                    self.input_text.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件:\n{str(e)}")
                
    def load_example(self, example_type):
        try:
            example_dir = os.path.join(self.examples_dir, example_type)
            template_path = os.path.join(example_dir, f"{example_type}.template")
            input_path = os.path.join(example_dir, f"{example_type}.input")
            
            # 对于自定义函数示例，我们需要特殊的处理
            if example_type == 'custom_functions':
                # 这里可以加载预定义的自定义函数
                # 在实际应用中，你可能需要一个更复杂的机制来处理自定义函数
                pass
            
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    self.template_text.delete("1.0", tk.END)
                    self.template_text.insert("1.0", template_content)
                    
            if os.path.exists(input_path):
                with open(input_path, 'r', encoding='utf-8') as f:
                    input_content = f.read()
                    self.input_text.delete("1.0", tk.END)
                    self.input_text.insert("1.0", input_content)
                    
        except Exception as e:
            messagebox.showerror("错误", f"无法加载示例:\n{str(e)}")
            
    def show_about(self):
        about_text = """TextFSM-Jinja GUI
        
一个基于TextFSM和Jinja2的文本解析和渲染工具的图形界面。

功能：
- 使用TextFSM模板解析半结构化文本
- 使用Jinja2模板对解析结果进行渲染
- 提供图形化界面进行实时验证
- 支持自定义函数扩展
- 支持加载示例进行测试

版本: 1.0
"""
        messagebox.showinfo("关于", about_text)


def main():
    root = tk.Tk()
    app = TextFSMGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()