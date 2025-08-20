import pytest
from xl_docx.compiler.processors.pager import PagerProcessor


class TestPagerProcessor:
    """测试PagerProcessor类的功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.processor = PagerProcessor()
    
    def test_init(self):
        """测试初始化"""
        processor = PagerProcessor()
        assert isinstance(processor, PagerProcessor)
    
    def test_compile_simple_pager(self):
        """测试编译简单页码"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        assert '<w:sdt>' in result
        assert '<w:sdtPr>' in result
        assert '<w:sdtContent>' in result
        assert '第' in result
        assert '页' in result
        assert '共' in result
        assert 'PAGE' in result
        assert 'NUMPAGES' in result
    
    def test_compile_pager_with_style(self):
        """测试编译带样式的页码"""
        xml = '<xl-pager style="font-size:18px;english:Arial;chinese:SimSun" />'
        result = self.processor.compile(xml)
        assert 'w:szCs w:val="18px"' in result
        assert 'w:ascii="Arial"' in result
        assert 'w:hAnsi="SimSun"' in result
    
    def test_compile_pager_default_font_size(self):
        """测试编译页码使用默认字体大小"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        assert 'w:szCs w:val="21"' in result
    
    def test_compile_pager_default_fonts(self):
        """测试编译页码使用默认字体"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        assert 'w:ascii="Times New Roman"' in result
        assert 'w:hAnsi="SimSun"' in result
    
    def test_compile_pager_custom_font_size(self):
        """测试编译页码使用自定义字体大小"""
        xml = '<xl-pager style="font-size:24px" />'
        result = self.processor.compile(xml)
        assert 'w:szCs w:val="24px"' in result
    
    def test_compile_pager_custom_english_font(self):
        """测试编译页码使用自定义英文字体"""
        xml = '<xl-pager style="english:Calibri" />'
        result = self.processor.compile(xml)
        assert 'w:ascii="Calibri"' in result
    
    def test_compile_pager_custom_chinese_font(self):
        """测试编译页码使用自定义中文字体"""
        xml = '<xl-pager style="chinese:微软雅黑" />'
        result = self.processor.compile(xml)
        assert 'w:hAnsi="微软雅黑"' in result
    
    def test_compile_pager_all_custom_styles(self):
        """测试编译页码使用所有自定义样式"""
        xml = '<xl-pager style="font-size:20px;english:Verdana;chinese:黑体" />'
        result = self.processor.compile(xml)
        assert 'w:szCs w:val="20px"' in result
        assert 'w:ascii="Verdana"' in result
        assert 'w:hAnsi="黑体"' in result
    
    def test_compile_pager_structure(self):
        """测试页码结构完整性"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        
        # 检查基本结构
        assert '<w:sdt>' in result
        assert '<w:sdtPr>' in result
        assert '<w:sdtEndPr>' in result
        assert '<w:sdtContent>' in result
        assert '</w:sdt>' in result
        
        # 检查页码字段
        assert '<w:fldChar w:fldCharType="begin"/>' in result
        assert '<w:instrText>PAGE</w:instrText>' in result
        assert '<w:fldChar w:fldCharType="separate"/>' in result
        assert '<w:fldChar w:fldCharType="end"/>' in result
        
        # 检查总页数字段
        assert '<w:instrText>NUMPAGES</w:instrText>' in result
    
    def test_compile_pager_text_content(self):
        """测试页码文本内容"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        
        # 检查中文文本
        assert '第' in result
        assert '页' in result
        assert '共' in result
        
        # 检查空格
        assert 'xml:space="preserve"' in result
    
    def test_compile_pager_multiple_instances(self):
        """测试编译多个页码实例"""
        xml = '''
        <xl-pager style="font-size:16px" />
        <xl-pager style="font-size:20px" />
        '''
        result = self.processor.compile(xml)
        
        # 检查是否包含两个页码实例
        assert result.count('<w:sdt>') == 2
        assert result.count('w:szCs w:val="16px"') == 1
        assert result.count('w:szCs w:val="20px"') == 1
    
    def test_compile_pager_with_other_content(self):
        """测试页码与其他内容混合"""
        xml = '''
        <div>content before</div>
        <xl-pager style="font-size:18px" />
        <div>content after</div>
        '''
        result = self.processor.compile(xml)
        
        assert 'content before' in result
        assert 'content after' in result
        assert '<w:sdt>' in result
        assert 'w:szCs w:val="18px"' in result
    
    def test_compile_pager_no_style(self):
        """测试编译无样式的页码"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        
        # 应该使用默认值
        assert 'w:szCs w:val="21"' in result
        assert 'w:ascii="Times New Roman"' in result
        assert 'w:hAnsi="SimSun"' in result
    
    def test_compile_pager_partial_style(self):
        """测试编译部分样式的页码"""
        xml = '<xl-pager style="font-size:16px" />'
        result = self.processor.compile(xml)
        
        # 自定义字体大小，其他使用默认值
        assert 'w:szCs w:val="16px"' in result
        assert 'w:ascii="Times New Roman"' in result
        assert 'w:hAnsi="SimSun"' in result
    
    def test_compile_pager_empty_style(self):
        """测试编译空样式的页码"""
        xml = '<xl-pager style="" />'
        result = self.processor.compile(xml)
        
        # 应该使用默认值
        assert 'w:szCs w:val="21"' in result
        assert 'w:ascii="Times New Roman"' in result
        assert 'w:hAnsi="SimSun"' in result
    
    def test_compile_pager_invalid_style(self):
        """测试编译无效样式的页码"""
        xml = '<xl-pager style="invalid:value" />'
        result = self.processor.compile(xml)
        
        # 应该使用默认值
        assert 'w:szCs w:val="21"' in result
        assert 'w:ascii="Times New Roman"' in result
        assert 'w:hAnsi="SimSun"' in result
    
    def test_compile_pager_large_font_size(self):
        """测试编译大字体大小的页码"""
        xml = '<xl-pager style="font-size:36px" />'
        result = self.processor.compile(xml)
        assert 'w:szCs w:val="36px"' in result
    
    def test_compile_pager_small_font_size(self):
        """测试编译小字体大小的页码"""
        xml = '<xl-pager style="font-size:8px" />'
        result = self.processor.compile(xml)
        assert 'w:szCs w:val="8px"' in result
    
    def test_compile_pager_special_fonts(self):
        """测试编译特殊字体的页码"""
        xml = '<xl-pager style="english:Courier New;chinese:楷体" />'
        result = self.processor.compile(xml)
        assert 'w:ascii="Courier New"' in result
        assert 'w:hAnsi="楷体"' in result
    
    def test_compile_pager_field_structure(self):
        """测试页码字段结构"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        
        # 检查页码字段的完整结构
        assert '<w:fldChar w:fldCharType="begin"/>' in result
        assert '<w:instrText>PAGE</w:instrText>' in result
        assert '<w:fldChar w:fldCharType="separate"/>' in result
        assert '<w:t>2</w:t>' in result  # 默认显示值
        assert '<w:fldChar w:fldCharType="end"/>' in result
        
        # 检查总页数字段的完整结构
        assert '<w:instrText>NUMPAGES</w:instrText>' in result
    
    def test_compile_pager_rpr_structure(self):
        """测试页码运行属性结构"""
        xml = '<xl-pager style="font-size:18px;english:Arial;chinese:SimSun" />'
        result = self.processor.compile(xml)
        
        # 检查运行属性
        assert '<w:rPr>' in result
        assert '<w:rFonts' in result
        assert '<w:szCs' in result
        assert '<w:b/>' in result  # 页码数字应该是粗体
        assert '<w:bCs/>' in result
    
    def test_compile_pager_language_settings(self):
        """测试页码语言设置"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        
        # 检查中文语言设置
        assert 'w:lang w:val="zh-CN"' in result
        assert 'w:hint="eastAsia"' in result
    
    def test_compile_pager_no_proof_settings(self):
        """测试页码校对设置"""
        xml = '<xl-pager />'
        result = self.processor.compile(xml)
        
        # 检查校对设置
        assert '<w:noProof/>' in result 