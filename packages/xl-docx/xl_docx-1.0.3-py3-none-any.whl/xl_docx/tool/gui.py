from tkinter import *
from tkinter.messagebox import showinfo
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk


class App:
    """GUI应用程序基类
    
    用法示例:
        app = App({
            'title': '应用程序',
            'size': (300, 200),
            'loc': (500, 300)
        })
        app.run()
    """
    
    def __init__(self, setting=None):
        """初始化GUI应用程序
        
        Args:
            setting: 窗口设置字典，支持以下键:
                    - title: 窗口标题
                    - size: (宽度, 高度)元组
                    - loc: (x坐标, y坐标)元组
        """
        self.instance = TkinterDnD.Tk()  # 使用支持拖拽的Tk
        self.instance.wm_attributes('-topmost', 1)
        
        if setting:
            self._apply_settings(setting)

    def _apply_settings(self, setting):
        """应用窗口设置"""
        if 'title' in setting:
            self.set_title(setting['title'])
        if 'size' in setting:
            self.set_size(*setting['size'])
        if 'loc' in setting:
            self.set_loc(*setting['loc'])

    def set_title(self, title):
        """设置窗口标题"""
        self.instance.title(title)
        return self

    def set_size(self, width, height):
        """设置窗口大小"""
        self.instance.geometry(f"{width}x{height}")
        return self

    def set_loc(self, x, y):
        """设置窗口位置"""
        self.instance.geometry(f"+{x}+{y}")
        return self

    # 基础组件创建方法
    def button(self, root, text, callback, **kwargs):
        """创建按钮组件
        
        Args:
            root: 父容器
            text: 按钮文本
            callback: 点击回调函数
        """
        return Button(root, text=text, command=callback, **kwargs)

    def label(self, root, text, **kwargs):
        """创建标签组件"""
        return Label(root, text=text, **kwargs)

    def input(self, root, string_var, callback=print, **kwargs):
        """创建输入框组件
        
        Args:
            root: 父容器
            string_var: StringVar变量
            callback: 回车回调函数
        """
        entry = Entry(root, textvariable=string_var, **kwargs)
        entry.bind('<Return>', callback)
        return entry

    def menu(self, root, items, **kwargs):
        """创建列表菜单组件
        
        Args:
            root: 父容器
            items: 菜单项列表
        """
        listbox = Listbox(root, **kwargs)
        for i, item in enumerate(items):
            listbox.insert(i, item)
        return listbox

    def message(self, text, **kwargs):
        """创建消息组件"""
        return Message(self.instance, text=text, **kwargs)

    def text(self, width=100, height=100):
        """创建文本编辑组件"""
        return Text(self.instance, width=width, height=height)

    def string_var(self, text):
        """创建字符串变量"""
        return StringVar(value=text)

    def alert(self, title, content):
        """显示提示对话框"""
        showinfo(title, content)

    def notebook(self, root):
        """创建选项卡组件"""
        return ttk.Notebook(root)

    def run(self):
        """运行应用程序"""
        self.instance.mainloop() 

