import pytest
from xl_docx.compiler.processors.paragraph import ParagraphProcessor


class TestParagraphProcessor:
    """测试ParagraphProcessor类的功能"""

    def test_decompile_with_color(self):
        xml = '''
        <w:p>
            <w:r>
                <w:rPr>
                    <w:color w:val="D7D7D7"/>
                </w:rPr>
                <w:t>content</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'color:D7D7D7' in result

    def test_compile_with_color(self):
        xml = '''
        <xl-p style="font-size:12px;color:D7D7D7">content</xl-p>
        '''
        result = ParagraphProcessor.compile(xml)
        assert '<w:color w:val="D7D7D7"/>' in result
        xml = '''
        <xl-p style="color:D7D7D7;font-size:12px;">content</xl-p>
        '''
        result = ParagraphProcessor.compile(xml)
        assert '<w:color w:val="D7D7D7"/>' in result

    def test_decompile_margin(self):
        xml = '''
        <w:p>
            <w:pPr>
                <w:ind w:start="21pt"/>
            </w:pPr>
            <w:r>
                <w:t>This is a paragraph with left indentation of 21pt.</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-left:21pt' in result
        xml = '''
        <w:p>
            <w:pPr>
                <w:ind w:end="21pt"/>
            </w:pPr>
            <w:r>
                <w:t>This is a paragraph with right indentation of 21pt.</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-right:21pt' in result
        xml = '''
        <w:p>
            <w:pPr>
                <w:ind w:start="21pt" w:end="22pt"/>
            </w:pPr>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-left:21pt' in result
        assert 'margin-right:22pt' in result

    def test_compile_margin(self):
        xml = '<xl-p style="margin-left:21pt">This is a paragraph with left indentation of 21pt.</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:ind w:start="21pt"/>' in result
        xml = '<xl-p style="margin-right:21pt">This is a paragraph with right indentation of 21pt.</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:ind w:end="21pt"/>' in result
        xml = '<xl-p style="margin-left:21pt;margin-right:22pt">This is a paragraph with left and right indentation of 21pt and 22pt.</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:ind w:start="21pt" w:end="22pt"/>' in result
    
    def test_compile_simple_paragraph(self):
        """测试编译简单段落"""
        xml = '<xl-p style="align:center;english:SimSun;chinese:SimSun">检件名称</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:p>' in result
        assert '<w:r>' in result
        assert '<w:t' in result
        assert '检件名称' in result
    
    def test_compile_paragraph_with_style(self):
        """测试编译带样式的段落"""
        xml = '<xl-p style="align:center;margin-top:10px;line-height:14pt;font-size:14px">content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:jc w:val="center"/>' in result
        assert 'w:before="10px"' in result
        assert 'w:line="14pt"' in result
        assert 'w:val="14px"' in result
    
    def test_compile_paragraph_with_fonts(self): 
        """测试编译带字体的段落"""
        xml = '<xl-p style="english:Arial;chinese:SimSun;font-size:12px">content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert 'w:ascii="Arial"' in result
        assert 'w:cs="SimSun"' in result
        assert 'w:val="12px"' in result
    
    def test_compile_paragraph_with_bold(self):
        """测试编译粗体段落"""
        xml = '<xl-p style="font-weight:bold">content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:b/>' in result
    
    def test_compile_paragraph_with_span(self):
        """测试编译包含span的段落"""
        xml = '<xl-p>text<xl-span style="underline:single;font-size:16px">span content</xl-span>more text</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:u w:val="single"/>' in result
        assert 'w:val="16px"' in result
        assert 'span content' in result
    
    def test_compile_paragraph_complex_style(self):
        """测试编译复杂样式的段落"""
        xml = '''<xl-p style="align:right;margin-top:20px;margin-bottom:10px;english:Times New Roman;chinese:宋体;font-size:16px;font-weight:bold">content</xl-p>'''
        result = ParagraphProcessor.compile(xml)
        assert '<w:jc w:val="right"/>' in result
        assert 'w:before="20px"' in result
        assert 'w:after="10px"' in result
        assert 'w:ascii="Times New Roman"' in result
        assert 'w:cs="宋体"' in result
        assert 'w:val="16px"' in result
        assert '<w:b/>' in result
    
    def test_compile_paragraph_no_style(self):
        """测试编译无样式的段落"""
        xml = '<xl-p>content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:p>' in result
        assert '<w:r>' in result
        assert '<w:t' in result
        assert 'content' in result
    
    def test_compile_paragraph_empty_content(self):
        """测试编译空内容的段落"""
        xml = '<xl-p></xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:p>' in result
        assert '<w:r>' in result
        assert '<w:t' in result
    
    def test_compile_paragraph_with_nested_spans(self):
        """测试编译包含嵌套span的段落"""
        xml = '''<xl-p><xl-span style="underline:double">span1</xl-span><xl-span style="font-weight:bold">span2</xl-span><xl-span>more text</xl-span></xl-p>'''
        result = ParagraphProcessor.compile(xml)
        assert '<w:u w:val="double"/>' in result
        assert '<w:b/>' in result
        assert 'span1' in result
        assert 'span2' in result
    
    def test_decompile_simple_paragraph(self):
        """测试反编译简单段落"""
        xml = '''<w:p><w:r><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-p>' in result
        assert 'content' in result
    
    def test_decompile_paragraph_with_alignment(self):
        """测试反编译带对齐的段落"""
        xml = '''<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'align:center' in result
    
    def test_decompile_paragraph_with_spacing(self):
        """测试反编译带间距的段落"""
        xml = '''<w:p><w:pPr><w:spacing w:before="20px" w:after="10px"/></w:pPr><w:r><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-top:20px' in result
        assert 'margin-bottom:10px' in result
        xml = '''
        <w:p>
            <w:pPr>
                <w:spacing w:before="240" w:line="18pt" w:lineRule="auto"/>
            </w:pPr>
            <w:r>
                <w:t>This is a paragraph with 12pt spacing above.</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'line-height:18pt' in result
    
    def test_decompile_paragraph_with_fonts(self):
        """测试反编译带字体的段落"""
        xml = '''<w:p><w:r><w:rPr><w:rFonts w:ascii="Arial" w:cs="SimSun"/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'english:Arial' in result
        assert 'chinese:SimSun' in result
    
    def test_decompile_paragraph_with_font_size(self):
        """测试反编译带字体大小的段落"""
        xml = '''<w:p><w:r><w:rPr><w:sz w:val="16px"/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'font-size:16px' in result
    
    def test_decompile_paragraph_with_bold(self):
        """测试反编译粗体段落"""
        xml = '''<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'font-weight:bold' in result
    
    def test_decompile_paragraph_with_underline(self):
        """测试反编译带下划线的段落"""
        xml = '''<w:p><w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'underline:single' in result
    
    def test_decompile_paragraph_with_span(self):
        """测试反编译包含span的段落"""
        xml = '''<w:p><w:r><w:t>text</w:t></w:r><w:r><w:rPr><w:u w:val="double"/></w:rPr><w:t>span content</w:t></w:r><w:r><w:t>more text</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-span' in result
        assert 'underline:double' in result
        assert 'span content' in result
    
    def test_decompile_paragraph_complex(self):
        """测试反编译复杂段落"""
        xml = '''<w:p><w:pPr><w:jc w:val="right"/><w:spacing w:before="20px" w:after="10px"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:cs="SimSun"/><w:sz w:val="16px"/><w:b/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'align:right' in result
        assert 'margin-top:20px' in result
        assert 'margin-bottom:10px' in result
        assert 'english:Arial' in result
        assert 'chinese:SimSun' in result
        assert 'font-size:16px' in result
        assert 'font-weight:bold' in result
    
    def test_decompile_paragraph_no_runs(self):
        """测试反编译没有运行标签的段落"""
        xml = '''<w:p><w:pPr><w:jc w:val="center"/></w:pPr></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-p style="align:center"></xl-p>' in result  # 应该转换为xl-p格式
    
    def test_decompile_paragraph_with_empty_runs(self):
        """测试反编译包含空运行的段落"""
        xml = '''<w:p><w:r><w:t></w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-p><xl-span style=""></xl-span></xl-p>' in result
    
    def test_decompile_paragraph_with_multiple_runs(self):
        """测试反编译包含多个运行的段落"""
        xml = '''<w:p><w:r><w:t>part1</w:t></w:r><w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>part2</w:t></w:r><w:r><w:t>part3</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'part1' in result
        assert 'part2' in result
        assert 'part3' in result
        assert '<xl-span' in result
        assert 'underline:single' in result
    
    def test_decompile_paragraph_with_nested_spans(self):
        """测试反编译包含嵌套span的段落"""
        xml = '''<w:p><w:r><w:t>text</w:t></w:r><w:r><w:rPr><w:u w:val="double"/></w:rPr><w:t>span1</w:t></w:r><w:r><w:rPr><w:u w:val="double"/><w:b/></w:rPr><w:t>span2</w:t></w:r><w:r><w:rPr><w:u w:val="double"/></w:rPr><w:t>span3</w:t></w:r><w:r><w:t>more text</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'text' in result
        assert 'span1' in result
        assert 'span2' in result
        assert 'span3' in result
        assert 'more text' in result
        assert '<xl-span' in result
        assert 'underline:double' in result
        assert 'font-weight:bold' in result
    
    def test_compile_paragraph_with_whitespace(self):
        """测试编译包含空白字符的段落"""
        xml = '<xl-p>  content with spaces  </xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert 'content with spaces' in result
    
    def test_decompile_paragraph_with_whitespace(self):
        """测试反编译包含空白字符的段落"""
        xml = '''<w:p><w:r><w:t xml:space="preserve">  content with spaces  </w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'content with spaces' in result
    
    def test_compile_paragraph_with_special_characters(self):
        """测试编译包含特殊字符的段落"""
        xml = '<xl-p>content with &lt;tags&gt; and "quotes"</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert 'content with &lt;tags&gt; and "quotes"' in result
    
    def test_decompile_paragraph_with_special_characters(self):
        """测试反编译包含特殊字符的段落"""
        xml = '''<w:p><w:r><w:t>content with &lt;tags&gt; and "quotes"</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'content with &lt;tags&gt; and "quotes"' in result 