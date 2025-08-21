from xl_docx.tool.gui import *
from xl_docx.tool.utility import SuperWordFile
from xl_docx.compiler import XMLCompiler
import os


class WordTemplateEditor:
    """Word模板编辑器"""

    def __init__(self):
        """初始化编辑器"""
        self.app = App({
            'title': 'XiLong DOCX Toolkit',
            'size': (420, 400),  # 调整窗口高度
            'loc': (500, 300)
        })
        self.root = self.app.instance
        self._init_ui()

    def _init_ui(self):
        """初始化UI界面"""
        self.main_frame = Frame(self.root, relief='ridge', borderwidth=1)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # DOCX区域
        self.docx_group = LabelFrame(self.main_frame, text="DOCX文件", padx=5, pady=5)
        self.docx_group.pack(fill=X, padx=5, pady=5)
        
        # 创建DOCX拖拽区域和打开按钮的容器
        docx_drop_frame = Frame(self.docx_group)
        docx_drop_frame.pack(fill=X, pady=5)
        
        # 创建DOCX拖拽区域
        self.docx_drop_label = Label(docx_drop_frame, text="拖拽DOCX文件到这里", relief="solid")
        self.docx_drop_label.pack(side=LEFT, expand=True, fill=X, padx=(0, 5))
        
        # 添加打开DOCX按钮
        open_docx_btn = Button(docx_drop_frame, text="打开", command=self._open_docx, width=8)
        open_docx_btn.pack(side=RIGHT)
        
        # 绑定拖拽事件
        self.docx_drop_label.drop_target_register("DND_Files")
        self.docx_drop_label.dnd_bind('<<Drop>>', self._on_docx_drop)

        # 提取按钮组
        extract_frame = Frame(self.docx_group)
        extract_frame.pack(fill=X, pady=5)
        
        extract_buttons = [
            ('提取document', self._extract_document),
            ('提取header', self._extract_header),
            ('提取footer', self._extract_footer)
        ]
        
        for text, command in extract_buttons:
            btn = self.app.button(extract_frame, text, command, width=13)
            btn.pack(side=LEFT, padx=2)

        # 反编译按钮组
        decompile_frame = Frame(self.docx_group)
        decompile_frame.pack(fill=X, pady=5)
        
        decompile_buttons = [
            ('反编译document', self._decompile_document),
            ('反编译header', self._decompile_header),
            ('反编译footer', self._decompile_footer)
        ]
        
        for text, command in decompile_buttons:
            btn = self.app.button(decompile_frame, text, command, width=13)
            btn.pack(side=LEFT, padx=2)

        # XML区域
        self.xml_group = LabelFrame(self.main_frame, text="XML文件", padx=5, pady=5)
        self.xml_group.pack(fill=X, padx=5, pady=5)
        
        # 创建XML拖拽区域和打开按钮的容器
        xml_drop_frame = Frame(self.xml_group)
        xml_drop_frame.pack(fill=X, pady=5)
        
        # 创建XML拖拽区域
        self.xml_drop_label = Label(xml_drop_frame, text="拖拽XML文件到这里", relief="solid")
        self.xml_drop_label.pack(side=LEFT, expand=True, fill=X, padx=(0, 5))
        
        # 添加打开XML按钮
        open_xml_btn = Button(xml_drop_frame, text="打开", command=self._open_xml, width=8)
        open_xml_btn.pack(side=RIGHT)
        
        # 绑定拖拽事件
        self.xml_drop_label.drop_target_register("DND_Files")
        self.xml_drop_label.dnd_bind('<<Drop>>', self._on_xml_drop)

        # XML操作按钮组
        xml_frame = Frame(self.xml_group)
        xml_frame.pack(fill=X, pady=5)
        
        xml_buttons = [
            ('反编译', self._decompile_xml),
            ('编译', self._compile_xml)
        ]
        
        for text, command in xml_buttons:
            btn = self.app.button(xml_frame, text, command, width=20)
            btn.pack(side=LEFT, padx=2, expand=True)

        # 转换区域
        convert_group = LabelFrame(self.main_frame, text="格式转换", padx=5, pady=5)
        convert_group.pack(fill=X, padx=5, pady=5)
        
        # DOCX转XML按钮组
        docx2xml_frame = Frame(convert_group)
        docx2xml_frame.pack(fill=X, pady=5)
        
        docx2xml_buttons = [
            ('DOCX转XML(竖向)', self._word2xml_v),
            ('DOCX转XML(横向)', self._word2xml_h)
        ]
        
        for text, command in docx2xml_buttons:
            btn = self.app.button(docx2xml_frame, text, command, width=20)
            btn.pack(side=LEFT, padx=2, expand=True)

        # XML转DOCX按钮组
        xml2docx_frame = Frame(convert_group)
        xml2docx_frame.pack(fill=X, pady=5)
        
        xml2docx_buttons = [
            ('XML转DOCX(竖向)', self._xml2word_v),
            ('XML转DOCX(横向)', self._xml2word_h)
        ]
        
        for text, command in xml2docx_buttons:
            btn = self.app.button(xml2docx_frame, text, command, width=20)
            btn.pack(side=LEFT, padx=2, expand=True)

    def _on_docx_drop(self, event):
        """处理DOCX文件拖拽"""
        file_path = event.data
        # 移除可能存在的花括号
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        if file_path.endswith('.docx'):
            self.current_file = file_path
            self.docx_drop_label.config(text=f"当前文件: {os.path.basename(file_path)}")
        else:
            self.app.alert("错误", "请拖拽DOCX文件(.docx)")

    def _on_xml_drop(self, event):
        """处理XML文件拖拽"""
        file_path = event.data
        # 移除可能存在的花括号
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        if file_path.endswith('.xml'):
            self.current_xml_file = file_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(file_path)}")
        else:
            self.app.alert("错误", "请拖拽XML文件(.xml)")

    # DOCX文件操作方法
    def _get_edit_input(self):
        """获取编辑输入"""
        if not hasattr(self, 'current_file'):
            self.app.alert("错误", "请先拖拽DOCX文件")
            return None, None
            
        folder = os.path.dirname(self.current_file)
        file = os.path.basename(self.current_file)
        return folder, file

    def _extract_document(self):
        """提取document.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            xml_path = SuperWordFile(folder, file).extract('document.xml')
            self.current_xml_file = xml_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")

    def _extract_header(self):
        """提取header.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            xml_path = SuperWordFile(folder, file).extract('header.xml')
            self.current_xml_file = xml_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")

    def _extract_footer(self):
        """提取footer.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            xml_path = SuperWordFile(folder, file).extract('footer.xml')
            self.current_xml_file = xml_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")

    def _decompile_document(self):
        """反编译document.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            xml_path = SuperWordFile(folder, file).extract('document.xml', decompile=True)
            self.current_xml_file = xml_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")

    def _decompile_header(self):
        """反编译header.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            xml_path = SuperWordFile(folder, file).extract('header.xml', decompile=True)
            self.current_xml_file = xml_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")

    def _decompile_footer(self):
        """反编译footer.xml"""
        folder, file = self._get_edit_input()
        if folder and file:
            xml_path = SuperWordFile(folder, file).extract('footer.xml', decompile=True)
            self.current_xml_file = xml_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")

    def _word2xml_h(self):
        """DOCX转XML(横向)"""
        xml_path = SuperWordFile.word2xml('h')
        if xml_path:
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")
            self.current_xml_file = xml_path

    def _word2xml_v(self):
        """DOCX转XML(竖向)"""
        xml_path = SuperWordFile.word2xml('v')
        if xml_path:
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(xml_path)}")
            self.current_xml_file = xml_path

    def _xml2word_h(self):
        """XML转DOCX(横向)"""
        docx_path = SuperWordFile.xml2word('h')
        if docx_path:
            self.docx_drop_label.config(text=f"当前文件: {os.path.basename(docx_path)}")
            self.current_file = docx_path

    def _xml2word_v(self):
        """XML转DOCX(竖向)"""
        docx_path = SuperWordFile.xml2word('v')
        if docx_path:
            self.docx_drop_label.config(text=f"当前文件: {os.path.basename(docx_path)}")
            self.current_file = docx_path

    def _compile_xml(self):
        """编译XML文件"""
        if not hasattr(self, 'current_xml_file'):
            self.app.alert("错误", "请先拖拽XML文件")
            return

        try:
            # 读取XML文件
            with open(self.current_xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()

            # 编译处理
            compiler = XMLCompiler()
            processed_content = compiler.compile_template(xml_content)

            # 保存处理后的文件
            output_path = os.path.join(
                os.path.dirname(self.current_xml_file),
                f'{SuperWordFile.timestamp()}_compiled.xml'
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            # 更新XML拖拽框显示
            self.current_xml_file = output_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(output_path)}")
            
        except Exception as e:
            raise e
            self.app.alert("错误", f"编译失败: {str(e)}")

    def _decompile_xml(self):
        """反编译XML文件"""
        if not hasattr(self, 'current_xml_file'):
            self.app.alert("错误", "请先拖拽XML文件")
            return

        try:
            # 读取XML文件
            with open(self.current_xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()

            compiler = XMLCompiler()
            processed_content = compiler.decompile_template(xml_content)

            # 保存处理后的文件
            output_path = os.path.join(
                os.path.dirname(self.current_xml_file),
                f'{SuperWordFile.timestamp()}_decompiled.xml'
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            # 更新XML拖拽框显示
            self.current_xml_file = output_path
            self.xml_drop_label.config(text=f"当前文件: {os.path.basename(output_path)}")
            
        except Exception as e:
            raise e
            self.app.alert("错误", f"反编译失败: {str(e)}")

    def _open_docx(self):
        """打开当前DOCX文件"""
        if hasattr(self, 'current_file'):
            os.startfile(self.current_file)
        else:
            self.app.alert("错误", "请先拖拽DOCX文件")

    def _open_xml(self):
        """打开当前XML文件"""
        if hasattr(self, 'current_xml_file'):
            os.startfile(self.current_xml_file)
        else:
            self.app.alert("错误", "请先拖拽XML文件")

    def run(self):
        """运行编辑器"""
        self.app.run()


if __name__ == '__main__':
    editor = WordTemplateEditor()
    editor.run()