import pytest
from xl_docx.compiler.processors.table import TableProcessor


class TestTableProcessor:
    """测试TableProcessor类的功能"""

    def test_decompile_table_with_width(self):
        """测试反编译带宽度的表格"""
        xml = '''
        <w:tbl>
            <w:tblPr>
                <w:tblW w:w="525.05pt" w:type="dxa"/>
                <w:jc w:val="center"/>
            </w:tblPr>
        </w:tbl>
        '''
        result = TableProcessor.decompile(xml)
        assert '<xl-table width="525.05pt"' in result

    def test_compile_table_with_width(self):
        """测试编译带宽度的表格"""
        xml = '<xl-table width="525.05pt"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblW w:w="525.05pt" w:type="dxa"/>' in result
    
    def test_decompile_table_with_margin(self):
        """测试反编译带高度的表格"""
        xml = '''
        <w:tbl>
            <w:tblPr>
                <w:tblInd w:w="19.60pt" w:type="dxa"/>
            </w:tblPr>
        </w:tbl>
        '''
        result = TableProcessor.decompile(xml)
        assert 'margin-left:19.60pt' in result

    def test_compile_table_with_margin(self):
        """测试编译带高度的表格"""
        xml = '<xl-table style="margin-left:19.60pt"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblInd w:w="19.60pt" w:type="dxa"/>' in result

    def test_compile_table_with_grid_column(self):
        """测试编译网格列的表格"""
        xml = '<xl-table grid="592/779/192"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblGrid>' in result
        assert '<w:gridCol w:w="592"/>' in result
        assert '<w:gridCol w:w="779"/>' in result
        assert '<w:gridCol w:w="192"/>' in result
        xml = '<xl-table style="align:center" grid="592/779/192"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblGrid>' in result
        assert '<w:jc w:val="center"/>' in result
        xml = '<xl-table grid="592/779/192" style="align:center"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tblGrid>' in result


    def test_decompile_table_with_grid_column(self):
        """测试反编译网格列的表格"""
        xml = '<w:tblGrid><w:gridCol w:w="592"/><w:gridCol w:w="779"/><w:gridCol w:w="192"/></w:tblGrid>'
        result = TableProcessor.decompile(xml)
        assert '<xl-table grid="592/779/192"/>' in result
        xml = '''<w:tblGrid>
            <w:gridCol w:w="592"/>
            <w:gridCol w:w="779"/>
            <w:gridCol w:w="192"/>
            </w:tblGrid>'''
        result = TableProcessor.decompile(xml)
        assert '<xl-table grid="592/779/192"/>' in result

    
    def test_compile_simple_table(self):
        """测试编译简单表格"""
        xml = '<xl-table><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tbl>' in result
        assert '<w:tblPr>' in result
        assert '<w:tr>' in result
        assert '<w:tc>' in result
    
    def test_compile_table_with_alignment(self):
        """测试编译带对齐的表格"""
        xml = '<xl-table style="align:center"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:jc w:val="center"/>' in result
    
    def test_compile_table_with_border_none(self):
        """测试编译无边框的表格"""
        xml = '<xl-table style="border:none"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert 'w:val="none"' in result
        assert 'w:sz="0"' in result
    
    def test_compile_table_with_default_border(self):
        """测试编译默认边框的表格"""
        xml = '<xl-table><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert 'w:val="single"' in result
        assert 'w:sz="4"' in result
    
    def test_compile_table_with_custom_border(self):
        """测试编译自定义边框的表格"""
        xml = '<xl-table style="border:double"><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        # 应该使用默认边框，因为只支持none
        assert 'w:val="single"' in result
    
    def test_compile_table_structure(self):
        """测试表格结构完整性"""
        xml = '<xl-table><xl-tr><xl-tc>content</xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        
        # 检查基本结构
        assert '<w:tbl>' in result
        assert '<w:tblPr>' in result
        assert '<w:tblBorders>' in result
        assert '<w:tblW w:type="auto" w:w="0"/>' in result
        assert '<w:tblInd w:w="0" w:type="dxa"/>' in result
        assert '<w:tblCellMar>' in result
    
    def test_compile_table_header(self):
        """测试编译表格头部"""
        xml = '<xl-th><xl-tc>header</xl-tc></xl-th>'
        result = TableProcessor.compile(xml)
        assert '<w:trPr>' in result
        assert '<w:tblHeader/>' in result
    
    def test_compile_table_header_with_attributes(self):
        """测试编译带属性的表格头部"""
        xml = '<xl-th height="500"><xl-tc>header</xl-tc></xl-th>'
        result = TableProcessor.compile(xml)
        assert '<w:trHeight w:val="500"/>' in result
        assert '<w:tblHeader/>' in result
    
    def test_compile_table_row(self):
        """测试编译表格行"""
        xml = '<xl-tr><xl-tc>content</xl-tc></xl-tr>'
        result = TableProcessor.compile(xml)
        assert '<w:tr>' in result
        assert '<w:trPr>' in result
    
    def test_compile_table_row_with_header(self):
        """测试编译带表头属性的行"""
        xml = '<xl-tr header="1"><xl-tc>content</xl-tc></xl-tr>'
        result = TableProcessor.compile(xml)
        assert '<w:tblHeader/>' in result
    
    def test_compile_table_row_with_cant_split(self):
        """测试编译不可分割的行"""
        xml = '<xl-tr cant-split="1"><xl-tc>content</xl-tc></xl-tr>'
        result = TableProcessor.compile(xml)
        assert '<w:cantSplit/>' in result
    
    def test_compile_table_row_with_height(self):
        """测试编译带高度的行"""
        xml = '<xl-tr height="300"><xl-tc>content</xl-tc></xl-tr>'
        result = TableProcessor.compile(xml)
        assert '<w:trHeight w:val="300"/>' in result
        xml = '''
        <xl-tr height="38pt">
        <xl-tc width="70.85pt">
          <xl-p style="align:start;font-size:24">
            <xl-span style="">电话：</xl-span>
          </xl-p>
        </xl-tc>
        <xl-tc width="402.25pt">
          <xl-p style="align:start;font-size:24">
            <xl-span style="">021-62859662/15921778068</xl-span>
          </xl-p>
        </xl-tc>
      </xl-tr>
        '''
        result = TableProcessor.compile(xml)
        assert '<w:trHeight w:val="38pt"/>' in result
    
    def test_compile_table_row_with_multiple_attributes(self):
        """测试编译带多个属性的行"""
        xml = '<xl-tr header="1" cant-split="1" height="400" class="test"><xl-tc>content</xl-tc></xl-tr>'
        result = TableProcessor.compile(xml)
        assert '<w:tblHeader/>' in result
        assert '<w:cantSplit/>' in result
        assert '<w:trHeight w:val="400"/>' in result
        assert 'class="test"' in result
    
    def test_compile_table_cell(self):
        """测试编译表格单元格"""
        xml = '<xl-tc>content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:tc>' in result
        assert '<w:tcPr>' in result
    
    def test_compile_table_cell_with_width(self):
        """测试编译带宽度的单元格"""
        xml = '<xl-tc width="2000">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:tcW w:type="dxa" w:w="2000"/>' in result
    
    def test_compile_table_cell_with_span(self):
        """测试编译带跨列的单元格"""
        xml = '<xl-tc span="2">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:gridSpan w:val="2"/>' in result
    
    def test_compile_table_cell_with_align(self):
        """测试编译带对齐的单元格"""
        xml = '<xl-tc align="center">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vAlign w:val="center"/>' in result
        xml = '<xl-tc>content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vAlign w:val="center"/>' in result
    
    def test_compile_table_cell_with_merge(self):
        """测试编译带合并的单元格"""
        xml = '<xl-tc merge="start">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vMerge w:val="restart"/>' in result
    
    def test_compile_table_cell_with_continue_merge(self):
        """测试编译继续合并的单元格"""
        xml = '<xl-tc merge="continue">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:vMerge/>' in result  # 没有val属性
    
    def test_compile_table_cell_with_borders(self):
        """测试编译带边框的单元格"""
        xml = '<xl-tc border-top="none" border-bottom="none" border-left="none" border-right="none">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:top w:val="nil"/>' in result
        assert '<w:bottom w:val="nil"/>' in result
        assert '<w:left w:val="nil"/>' in result
        assert '<w:right w:val="nil"/>' in result
    
    def test_compile_table_cell_with_content_tags(self):
        """测试编译包含标签内容的单元格"""
        xml = '<xl-tc><xl-p>paragraph content</xl-p></xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<xl-p>paragraph content</xl-p>' in result  # 内容应该保持不变
    
    def test_compile_table_cell_complex_attributes(self):
        """测试编译带复杂属性的单元格"""
        xml = '<xl-tc width="1500" span="3" align="center" merge="start" border-top="none">content</xl-tc>'
        result = TableProcessor.compile(xml)
        assert '<w:tcW w:type="dxa" w:w="1500"/>' in result
        assert '<w:gridSpan w:val="3"/>' in result
        assert '<w:vAlign w:val="center"/>' in result
        assert '<w:vMerge w:val="restart"/>' in result
        assert '<w:top w:val="nil"/>' in result
    
    def test_compile_complex_table(self):
        """测试编译复杂表格"""
        xml = '''
        <xl-table style="align:center;border:none">
            <xl-th height="500">
                <xl-tc width="1000" align="center">Header 1</xl-tc>
                <xl-tc width="1000" align="center">Header 2</xl-tc>
            </xl-th>
            <xl-tr>
                <xl-tc span="2" align="center">Content</xl-tc>
            </xl-tr>
        </xl-table>
        '''
        result = TableProcessor.compile(xml)
        
        # 检查表格属性
        assert '<w:jc w:val="center"/>' in result
        assert 'w:val="none"' in result
        
        # 检查表头
        assert '<w:tblHeader/>' in result
        assert '<w:trHeight w:val="500"/>' in result
        
        # 检查单元格
        assert '<w:tcW w:type="dxa" w:w="1000"/>' in result
        assert '<w:gridSpan w:val="2"/>' in result
    
    def test_decompile_simple_table(self):
        """测试反编译简单表格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert '<xl-table' in result
        assert '<xl-tr>' in result
        assert '<xl-tc>' in result
        assert 'content' in result
    
    def test_decompile_table_with_alignment(self):
        """测试反编译带对齐的表格"""
        xml = '''<w:tbl><w:tblPr><w:jc w:val="center"/></w:tblPr><w:tr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'align:center' in result
    
    def test_decompile_table_with_borders(self):
        """测试反编译带边框的表格"""
        xml = '''<w:tbl><w:tblPr><w:tblBorders><w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders></w:tblPr><w:tr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'border:none' in result
    
    def test_decompile_table_with_header(self):
        """测试反编译带表头的表格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:trPr><w:tblHeader/></w:trPr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>header</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'header="1"' in result
    
    def test_decompile_table_with_cant_split(self):
        """测试反编译不可分割的表格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:trPr><w:cantSplit/></w:trPr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'cant-split="1"' in result
    
    def test_decompile_table_with_height(self):
        """测试反编译带高度的表格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:trPr><w:trHeight w:val="300"/></w:trPr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'height="300"' in result
    
    def test_decompile_table_cell_with_width(self):
        """测试反编译带宽度的单元格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2000"/></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'width="2000"' in result
    
    def test_decompile_table_cell_with_span(self):
        """测试反编译带跨列的单元格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr><w:gridSpan w:val="3"/></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'span="3"' in result
    
    def test_decompile_table_cell_with_align(self):
        """测试反编译带对齐的单元格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr><w:vAlign w:val="center"/></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'align="center"' in result
    
    def test_decompile_table_cell_with_merge(self):
        """测试反编译带合并的单元格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr><w:vMerge w:val="restart"/></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'merge="start"' in result
    
    def test_decompile_table_cell_with_continue_merge(self):
        """测试反编译继续合并的单元格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'merge="continue"' in result
    
    def test_decompile_table_cell_with_borders(self):
        """测试反编译带边框的单元格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr><w:tcBorders><w:top w:val="nil"/><w:bottom w:val="nil"/></w:tcBorders></w:tcPr><w:p><w:r><w:t>content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert 'border-top="none"' in result
        assert 'border-bottom="none"' in result
    
    def test_decompile_complex_table(self):
        """测试反编译复杂表格"""
        xml = '''<w:tbl><w:tblPr><w:jc w:val="center"/><w:tblBorders><w:top w:val="none"/></w:tblBorders></w:tblPr><w:tr><w:trPr><w:tblHeader/><w:trHeight w:val="500"/></w:trPr><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="1000"/><w:vAlign w:val="center"/></w:tcPr><w:p><w:r><w:t>header</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        
        # 检查表格属性
        assert 'align:center' in result
        assert 'border:none' in result
        
        # 检查行属性
        assert 'header="1"' in result
        assert 'height="500"' in result
        
        # 检查单元格属性
        assert 'width="1000"' in result
        assert 'align="center"' in result
    
    def test_compile_table_empty_cells(self):
        """测试编译空单元格的表格"""
        xml = '<xl-table><xl-tr><xl-tc></xl-tc></xl-tr></xl-table>'
        result = TableProcessor.compile(xml)
        assert '<w:tc>' in result
        assert '<xl-p>' in result  # 空内容应该被包装为段落
    
    def test_decompile_table_empty_cells(self):
        """测试反编译空单元格的表格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr></w:tcPr><w:p></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert '<xl-tc>' in result
    
    def test_compile_table_multiple_rows(self):
        """测试编译多行表格"""
        xml = '''
        <xl-table>
            <xl-tr><xl-tc>row1</xl-tc></xl-tr>
            <xl-tr><xl-tc>row2</xl-tc></xl-tr>
        </xl-table>
        '''
        result = TableProcessor.compile(xml)
        assert result.count('<w:tr>') == 2
        assert 'row1' in result
        assert 'row2' in result
    
    def test_decompile_table_multiple_rows(self):
        """测试反编译多行表格"""
        xml = '''<w:tbl><w:tblPr></w:tblPr><w:tr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>row1</w:t></w:r></w:p></w:tc></w:tr><w:tr><w:tc><w:tcPr></w:tcPr><w:p><w:r><w:t>row2</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'''
        result = TableProcessor.decompile(xml)
        assert result.count('<xl-tr>') == 2
        assert 'row1' in result
        assert 'row2' in result 