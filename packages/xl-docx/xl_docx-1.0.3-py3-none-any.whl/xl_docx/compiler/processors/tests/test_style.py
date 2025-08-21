import pytest
from xl_docx.compiler.processors.style import StyleProcessor


class TestStyleProcessor:
    """测试StyleProcessor类的功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.processor = StyleProcessor()
    
    def test_init(self):
        """测试初始化"""
        processor = StyleProcessor()
        assert processor.styles == {}
    
    def test_parse_styles_simple(self):
        """测试解析简单样式"""
        xml = '''
        <style>
        xl-p {
            font-size: 12px;
            color: red;
        }

        .container{
            font-size: 12px;
            color: red;
        }
        </style>
        <div class="container">content</div>
        '''
        result = self.processor._parse_styles(xml)
        assert '.container' in self.processor.styles
        assert 'font-size:12px;color:red' in self.processor.styles['.container']
        assert '<style>' not in result
    
    def test_parse_styles_multiple_rules(self):
        """测试解析多个CSS规则"""
        xml = '''
        <style>
        .header {
            font-size: 16px;
            font-weight: bold;
        }
        .content {
            font-size: 12px;
            color: black;
        }
        </style>
        '''
        result = self.processor._parse_styles(xml)
        assert '.header' in self.processor.styles
        assert '.content' in self.processor.styles
        assert 'font-size:16px;font-weight:bold' in self.processor.styles['.header']
        assert 'font-size:12px;color:black' in self.processor.styles['.content']
    
    def test_parse_styles_with_newlines(self):
        """测试解析带换行符的样式"""
        xml = '''
        <style>
        .test {
            font-size: 12px;
            color: red;
            margin: 10px;
        }
        </style>
        '''
        result = self.processor._parse_styles(xml)
        assert '.test' in self.processor.styles
        # 检查换行符是否被清理
        style_content = self.processor.styles['.test']
        assert '\n' not in style_content
    
    def test_parse_styles_empty_style_tag(self):
        """测试解析空的style标签"""
        xml = '<style></style><div>content</div>'
        result = self.processor._parse_styles(xml)
        assert self.processor.styles == {}
        assert '<style></style>' not in result
    
    def test_parse_styles_no_style_tag(self):
        """测试没有style标签的情况"""
        xml = '<div>content</div>'
        result = self.processor._parse_styles(xml)
        assert self.processor.styles == {}
        assert result == xml
    
    def test_apply_styles_simple(self):
        """测试应用简单样式"""
        self.processor.styles = {
            'xl-p': 'font-size: 12px; color: red'
            # '.test': 'font-size: 12px; color: red'
        }
        # xml = '<div class="test">content</div>'
        xml = '<xl-p>content</xl-p>'
        result = self.processor._apply_styles(xml)
        assert 'style="font-size:12px;color:red"' in result
    
    def test_apply_styles_existing_style(self):
        """测试应用样式到已有style属性的元素"""
        self.processor.styles = {
            '.test': 'color: blue'
        }
        xml = '<div class="test" style="font-size: 12px">content</div>'
        result = self.processor._apply_styles(xml)

        # 检查样式是否合并
        assert 'style="font-size:12px;color:blue"' in result
    
    def test_apply_styles_multiple_elements(self):
        """测试应用样式到多个元素"""
        self.processor.styles = {
            '.header': 'font-size: 16px',
            '.content': 'font-size: 12px'
        }
        # 修改为单一根节点，保证etree.fromstring可以解析
        xml = '''
        <root>
            <div class="header">Header</div>
            <div class="content">Content</div>
        </root>
        '''
        result = self.processor._apply_styles(xml)
        assert 'style="font-size:16px"' in result
        assert 'style="font-size:12px"' in result
    
    def test_apply_styles_no_matching_elements(self):
        """测试没有匹配元素的情况"""
        self.processor.styles = {
            '.test': 'font-size: 12px'
        }
        xml = '<div class="other">content</div>'
        result = self.processor._apply_styles(xml)
        assert result == xml
    
    def test_apply_styles_protect_template_tags(self):
        """测试保护Jinja2模板标签"""
        self.processor.styles = {
            '.test': 'font-size: 12px'
        }
        xml = '<div class="test">{% if condition %}content{% endif %}</div>'
        result = self.processor._apply_styles(xml)
        assert 'style="font-size:12px"' in result
        assert '{% if condition %}' in result
        assert '{% endif %}' in result
    
    def test_apply_styles_invalid_xml(self):
        """测试处理无效XML"""
        self.processor.styles = {
            '.test': 'font-size: 12px'
        }
        xml = '<div class="test">content<div>'  # 缺少结束标签
        with pytest.raises(Exception):  # 应该抛出XMLSyntaxError
            self.processor._apply_styles(xml)
    
    def test_compile_full_process(self):
        """测试完整的编译过程"""
        xml = '''
        <style>
        .test {
            font-size: 12px;
            color: red;
        }
        </style>
        <div class="test">content</div>
        '''
        result = self.processor.compile(xml)
        assert '<style>' not in result
        assert 'style="font-size:12px;color:red"' in result
    
    def test_compile_no_styles(self):
        """测试没有样式的编译"""
        xml = '<div>content</div>'
        result = self.processor.compile(xml)
        assert result == xml
    
    def test_compile_with_xml_declaration(self):
        """测试处理XML声明"""
        self.processor.styles = {
            '.test': 'font-size: 12px'
        }
        xml = '<?xml version="1.0" encoding="UTF-8"?><div class="test">content</div>'
        result = self.processor._apply_styles(xml)
        assert '<?xml' not in result
        assert 'style="font-size:12px"' in result
    
    def test_compile_complex_css_selectors(self):
        """测试复杂CSS选择器"""
        self.processor.styles = {
            'div.container p': 'font-size: 12px',
            '#main .item': 'color: blue'
        }
        xml = '''
        <root>
            <div class="container">
                <p>paragraph</p>
            </div>
            <div id="main">
                <div class="item">item</div>
            </div>
        </root>
        '''
        result = self.processor._apply_styles(xml)
        assert 'style="font-size:12px"' in result
        assert 'style="color:blue"' in result
    
    def test_compile_nested_styles(self):
        """测试嵌套样式"""
        self.processor.styles = {
            '.outer': 'margin: 10px',
            '.outer .inner': 'padding: 5px'
        }
        xml = '''
        <div class="outer">
            <div class="inner">nested</div>
        </div>
        '''
        result = self.processor._apply_styles(xml)
        assert 'style="margin:10px"' in result
        assert 'style="padding:5px"' in result
    
    def test_compile_style_override(self):
        """测试样式覆盖"""
        self.processor.styles = {
            '.test': 'color: blue'
        }
        xml = '<div class="test" style="color: red">content</div>'
        result = self.processor._apply_styles(xml)
        # 新样式应该覆盖旧样式
        assert 'style="color:blue"' in result
        assert 'style="color:red"' not in result 