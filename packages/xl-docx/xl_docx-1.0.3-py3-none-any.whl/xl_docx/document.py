from xl_docx.sheet import Sheet
from pathlib import Path


class Document(Sheet):
    """Word表单对象，用于处理组件化的Word文档渲染"""

    # 自定义语法映射到Jinja2语法
    SYNTAX_MAP = {
        r'($': '{%',
        r'$)': '%}', 
        r'((': '{{',
        r'))': '}}',
    }

    def __init__(self, tpl_path, component_folder=None, xml_folder=None):
        super().__init__(tpl_path, xml_folder)
        self.component_folder = component_folder

    def _build_component_template(self):
        """构建组件模板字符串
        
        Args:
            component_files: 组件文件列表
            
        Returns:
            str: 组合后的模板字符串
        """
        component_files = self._get_component_files()

        template_parts = ['($ for item in data $)']
        
        for index, filepath in enumerate(component_files):
            component_type = filepath.stem
            component_content = self._read_component_file(filepath)
            condition = 'if' if index == 0 else 'elif'
            template_parts.append(
                f"($ {condition} item['component']=='{component_type}' $){component_content}"
            )

        template_parts.extend(['($ endif $)', '($ endfor $)'])
        return ''.join(template_parts)
    
    def _read_component_file(self, filepath):
        """读取组件文件内容
        
        Args:
            filepath: 组件文件路径
            
        Returns:
            str: 组件文件内容
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()

    def _convert_syntax(self, content):
        """转换自定义语法为Jinja2语法
        
        Args:
            content: 包含自定义语法的内容
            
        Returns:
            str: 转换后的内容
        """
        for custom, jinja in self.SYNTAX_MAP.items():
            content = content.replace(custom, jinja)
        return content

    def render(self, data):
        """渲染文档
        
        Args:
            data: 渲染数据
        """
        template_xml = self._build_component_template()
        
        document_xml = self.render_xml('document', dict(document=template_xml)).decode()
        document_xml = self._convert_syntax(document_xml)
        
        self['word/document.xml'] = document_xml.encode('utf-8')
        super().render_xml('document', data)
