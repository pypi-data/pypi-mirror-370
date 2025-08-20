import pytest
from xl_docx.compiler.processors.base import BaseProcessor


class TestBaseProcessor:
    """测试BaseProcessor基类的功能"""
    
    def test_retrieve_success(self):
        """测试retrieve方法成功提取字典值"""
        params = {'a': 1, 'b': 2, 'c': 3}
        a, b = BaseProcessor.retrieve(params, ['a', 'b'])
        assert a == 1
        assert b == 2
    
    def test_retrieve_missing_key(self):
        """测试retrieve方法处理缺失的键"""
        params = {'a': 1, 'b': 2}
        a, c = BaseProcessor.retrieve(params, ['a', 'c'])
        assert a == 1
        assert c is None
    
    def test_retrieve_empty_dict(self):
        """测试retrieve方法处理空字典"""
        params = {}
        a, b = BaseProcessor.retrieve(params, ['a', 'b'])
        assert a is None
        assert b is None
    
    def test_extract_attrs_success(self):
        """测试_extract_attrs方法成功提取属性"""
        attrs_str = 'name="test" value="123" type="string"'
        result = BaseProcessor._extract_attrs(attrs_str, ['name', 'value', 'type'])
        assert result == ('test', '123', 'string')
    
    def test_extract_attrs_missing_attr(self):
        """测试_extract_attrs方法处理缺失的属性"""
        attrs_str = 'name="test" value="123"'
        result = BaseProcessor._extract_attrs(attrs_str, ['name', 'missing', 'value'])
        assert result == ('test', None, '123')
    
    def test_extract_attrs_empty_string(self):
        """测试_extract_attrs方法处理空字符串"""
        result = BaseProcessor._extract_attrs('', ['name', 'value'])
        assert result == (None, None)
    
    def test_extract_success(self):
        """测试_extract方法成功提取值"""
        xml = '<tag>content</tag>'
        pattern = r'<tag>(.*?)</tag>'
        result = BaseProcessor._extract(pattern, xml)
        assert result == 'content'
    
    def test_extract_no_match(self):
        """测试_extract方法处理无匹配情况"""
        xml = '<tag>content</tag>'
        pattern = r'<missing>(.*?)</missing>'
        result = BaseProcessor._extract(pattern, xml)
        assert result is None
    
    def test_parse_style_str_valid(self):
        """测试_parse_style_str方法解析有效样式字符串"""
        style_str = "font-size:12px;color:red;margin:10px"
        result = BaseProcessor._parse_style_str(style_str)
        expected = {
            'font-size': '12px',
            'color': 'red',
            'margin': '10px'
        }
        assert result == expected
    
    def test_parse_style_str_empty(self):
        """测试_parse_style_str方法处理空字符串"""
        result = BaseProcessor._parse_style_str('')
        assert result == {}
    
    def test_parse_style_str_none(self):
        """测试_parse_style_str方法处理None"""
        result = BaseProcessor._parse_style_str(None)
        assert result == {}
    
    def test_parse_style_str_with_spaces(self):
        """测试_parse_style_str方法处理带空格的样式"""
        style_str = "font-size: 12px; color: red; margin: 10px"
        result = BaseProcessor._parse_style_str(style_str)
        expected = {
            'font-size': '12px',
            'color': 'red',
            'margin': '10px'
        }
        assert result == expected
    
    def test_build_style_str_valid(self):
        """测试_build_style_str方法构建有效样式字符串"""
        styles = {
            'font-size': '12px',
            'color': 'red',
            'margin': '10px'
        }
        result = BaseProcessor._build_style_str(styles)
        assert result == 'font-size:12px;color:red;margin:10px'
    
    def test_build_style_str_empty_dict(self):
        """测试_build_style_str方法处理空字典"""
        result = BaseProcessor._build_style_str({})
        assert result == ''
    
    def test_build_style_str_none(self):
        """测试_build_style_str方法处理None"""
        result = BaseProcessor._build_style_str(None)
        assert result == ''
    
    def test_build_attr_str_valid(self):
        """测试_build_attr_str方法构建有效属性字符串"""
        attrs = {
            'class': 'container',
            'id': 'main',
            'data-value': '123'
        }
        result = BaseProcessor._build_attr_str(attrs)
        assert result == 'class="container" id="main" data-value="123"'
    
    def test_build_attr_str_empty_dict(self):
        """测试_build_attr_str方法处理空字典"""
        result = BaseProcessor._build_attr_str({})
        assert result == ''
    
    def test_build_attr_str_none(self):
        """测试_build_attr_str方法处理None"""
        result = BaseProcessor._build_attr_str(None)
        assert result == ''
    
    def test_process_tag_simple(self):
        """测试_process_tag方法简单替换"""
        xml = '<tag>content</tag>'
        pattern = r'<tag>(.*?)</tag>'
        
        def process_func(match):
            return f'<div>{match.group(1)}</div>'
        
        result = BaseProcessor._process_tag(xml, pattern, process_func)
        assert result == '<div>content</div>'
    
    def test_process_tag_multiple_matches(self):
        """测试_process_tag方法处理多个匹配"""
        xml = '<tag>content1</tag><tag>content2</tag>'
        pattern = r'<tag>(.*?)</tag>'
        
        def process_func(match):
            return f'<div>{match.group(1)}</div>'
        
        result = BaseProcessor._process_tag(xml, pattern, process_func)
        assert result == '<div>content1</div><div>content2</div>'
    
    def test_process_tag_no_matches(self):
        """测试_process_tag方法处理无匹配情况"""
        xml = '<tag>content</tag>'
        pattern = r'<missing>(.*?)</missing>'
        
        def process_func(match):
            return f'<div>{match.group(1)}</div>'
        
        result = BaseProcessor._process_tag(xml, pattern, process_func)
        assert result == xml
    
    def test_compile_not_implemented(self):
        """测试compile方法抛出NotImplementedError"""
        with pytest.raises(NotImplementedError):
            BaseProcessor.compile("test") 