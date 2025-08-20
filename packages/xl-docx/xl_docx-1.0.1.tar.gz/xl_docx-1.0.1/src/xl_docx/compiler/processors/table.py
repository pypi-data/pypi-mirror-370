from xl_docx.compiler.processors.base import BaseProcessor
import re


class TableProcessor(BaseProcessor):
    """处理表格相关的XML标签"""
    
    # 正则表达式模式常量，提高可读性
    XL_TABLE_PATTERN = r'''
        <xl-table                    # 开始标签
        ([^>]*)                     # 所有属性
        >                           # 标签结束
        (.*?)                       # 内容（非贪婪匹配）
        </xl-table>                 # 结束标签
    '''
    
    XL_TH_PATTERN = r'''
        <xl-th                       # 开始标签
        ([^>]*)                     # 属性
        >                           # 标签结束
        (.*?)                       # 内容（非贪婪匹配）
        </xl-th>                    # 结束标签
    '''
    
    XL_TR_PATTERN = r'''
        <xl-tr                       # 开始标签
        ([^>]*)                     # 属性
        >                           # 标签结束
        (.*?)                       # 内容（非贪婪匹配）
        </xl-tr>                    # 结束标签
    '''
    
    XL_TC_PATTERN = r'''
        <xl-tc                       # 开始标签
        ([^>]*)                     # 属性
        >                           # 标签结束
        (.*?)                       # 内容（非贪婪匹配）
        </xl-tc>                    # 结束标签
    '''
    
    XL_P_PATTERN = r'''
        <xl-p                       # 开始标签
        [^>]*>                      # 其他属性
        .*?                         # 内容（非贪婪匹配）
        </xl-p>                     # 结束标签
    '''
    
    # Word文档相关模式
    W_TBL_PATTERN = r'<w:tbl>.*?</w:tbl>'
    W_TR_PATTERN = r'<w:tr(?!Pr)[^>]*>(.*?)</w:tr>'
    W_TC_PATTERN = r'<w:tc>(.*?)</w:tc>'
    W_TBLGRID_PATTERN = r'<w:tblGrid>(.*?)</w:tblGrid>'
    W_GRIDCOL_PATTERN = r'<w:gridCol\s+w:w="([^"]+)"/>'

    # Word文档属性模式
    W_JC_PATTERN = r'<w:jc\s+w:val="([^"]+)"/>'
    W_TBLBORDERS_PATTERN = r'<w:tblBorders>(.*?)</w:tblBorders>'
    W_TRPR_PATTERN = r'<w:trPr>(.*?)</w:trPr>'
    W_TRHEIGHT_PATTERN = r'<w:trHeight[^>]*?w:val="([^"]+)"[^>]*?/>'
    W_TCW_PATTERN = r'<w:tcW.*w:w="([^"]+)".*/>'
    W_GRIDSPAN_PATTERN = r'<w:gridSpan\s+w:val="([^"]+)"/>'
    W_VALIGN_PATTERN = r'<w:vAlign\s+w:val="([^"]+)"/>'
    W_VMERGE_PATTERN = r'<w:vMerge(?:\s+w:val="([^"]+)")?/>'
    W_TCPR_CONTENT_PATTERN = r'<w:tc>.*?<w:tcPr>.*?</w:tcPr>(.*?)</w:tc>'
    
    # 边框相关模式
    BORDER_TOP_PATTERN = r'<w:top[^>]*w:val="([^"]+)"/>'
    BORDER_BOTTOM_PATTERN = r'<w:bottom[^>]*w:val="([^"]+)"/>'
    BORDER_LEFT_PATTERN = r'<w:left[^>]*w:val="([^"]+)"/>'
    BORDER_RIGHT_PATTERN = r'<w:right[^>]*w:val="([^"]+)"/>'
    BORDER_SIZE_ZERO_PATTERN = r'<w:(?:top|bottom|left|right)[^>]*w:sz="0"[^>]*/>'
    
    @classmethod
    def compile(cls, xml: str) -> str:
        xml = cls._process_xl_table(xml)
        xml = cls._process_xl_th(xml)
        xml = cls._process_xl_tr(xml)
        xml = cls._process_xl_tc(xml)
        return xml
        
    @classmethod
    def _process_xl_table(cls, xml: str) -> str:
        def process_table(match):
            attrs, content = match.groups()
            content = content.strip()
            
            # 解析属性
            style_str = None
            grid_str = None
            width_str = None
            
            # 提取 style 属性
            style_match = re.search(r'style="([^"]*)"', attrs)
            if style_match:
                style_str = style_match.group(1)
            
            # 提取 grid 属性
            grid_match = re.search(r'grid="([^"]*)"', attrs)
            if grid_match:
                grid_str = grid_match.group(1)
            
            # 提取 width 属性
            width_match = re.search(r'width="([^"]*)"', attrs)
            if width_match:
                width_str = width_match.group(1)
            
            # 解析样式
            styles = cls._parse_style_str(style_str) if style_str else {}
            tbl_props_str = ''
            
            # 处理对齐方式
            if 'align' in styles:
                tbl_props_str += f'<w:jc w:val="{styles["align"]}"/>'
            
            # 处理边框样式
            if styles.get('border') == 'none':
                tbl_props_str += '''<w:tblBorders>
                <w:top w:color="auto" w:space="0" w:sz="0" w:val="none"/>
                <w:left w:color="auto" w:space="0" w:sz="0" w:val="none"/>
                <w:bottom w:color="auto" w:space="0" w:sz="0" w:val="none"/>
                <w:right w:color="auto" w:space="0" w:sz="0" w:val="none"/>
                <w:insideH w:color="auto" w:space="0" w:sz="0" w:val="none"/>
                <w:insideV w:color="auto" w:space="0" w:sz="0" w:val="none"/>
            </w:tblBorders>'''
            else:
                tbl_props_str += '''<w:tblBorders>
                    <w:top w:color="auto" w:space="0" w:sz="4" w:val="single"/>
                    <w:left w:color="auto" w:space="0" w:sz="4" w:val="single"/>
                    <w:bottom w:color="auto" w:space="0" w:sz="4" w:val="single"/>
                    <w:right w:color="auto" w:space="0" w:sz="4" w:val="single"/>
                    <w:insideH w:color="auto" w:space="0" w:sz="4" w:val="single"/>
                    <w:insideV w:color="auto" w:space="0" w:sz="4" w:val="single"/>
                </w:tblBorders>'''
            
            # 处理左边距设置
            margin_left = styles.get('margin-left', '0')
            tbl_props_str += f'<w:tblInd w:w="{margin_left}" w:type="dxa"/>'
            
            # 处理表格宽度
            if width_str:
                tbl_props_str += f'<w:tblW w:w="{width_str}" w:type="dxa"/>'
            else:
                tbl_props_str += '<w:tblW w:type="auto" w:w="0"/>'
            
            # 添加单元格边距设置
            tbl_props_str += '''
                <w:tblCellMar>
                    <w:top w:type="dxa" w:w="0"/>
                    <w:left w:type="dxa" w:w="0"/>
                    <w:bottom w:type="dxa" w:w="0"/>
                    <w:right w:type="dxa" w:w="0"/>
                </w:tblCellMar>
            '''
            
            # 处理列宽设置
            tbl_grid_str = ''
            if grid_str:
                col_widths = grid_str.split('/')
                tbl_grid_str = '<w:tblGrid>'
                for width in col_widths:
                    tbl_grid_str += f'<w:gridCol w:w="{width}"/>'
                tbl_grid_str += '</w:tblGrid>'
            
            return f'''<w:tbl><w:tblPr>{tbl_props_str}</w:tblPr>{tbl_grid_str}{content}</w:tbl>'''
            
        return cls._process_tag(xml, cls.XL_TABLE_PATTERN, process_table)

    @classmethod
    def _process_xl_th(cls, xml: str) -> str:
        def process_th(match):
            attrs, content = match.groups()
            return f'<xl-tr header="1" {attrs}>{content}</xl-tr>'
            
        return cls._process_tag(xml, cls.XL_TH_PATTERN, process_th)
    
    @classmethod
    def _process_xl_tr(cls, xml: str) -> str:
        def process_tr(match):
            attrs, content = match.groups()
            tr_props_str = ''
            
            # 处理表头属性
            tr_props_str += '<w:tblHeader/>' if 'header' in attrs else ''
            # 处理不可分割属性
            tr_props_str += '<w:cantSplit/>' if 'cant-split' in attrs else ''
            
            # 处理高度属性
            height_match = re.search(r'height="([\d.]+[a-zA-Z]*)"', attrs)
            if height_match:
                height = height_match.group(1)
                tr_props_str += f'<w:trHeight w:val="{height}"/>'
            
            # 过滤掉已处理的属性
            other_attrs = re.findall(r'(\w+)="([^"]*)"', attrs)
            filtered_attrs = [(k, v) for k, v in other_attrs if k not in ['header', 'cant-split']]
            attrs_str = ' '.join([f'{k}="{v}"' for k, v in filtered_attrs])
            tr_props_str = f'<w:trPr>{tr_props_str}</w:trPr>'
            
            return f'<w:tr{" " + attrs_str if attrs_str else ""}>{tr_props_str}{content}</w:tr>'
            
        return cls._process_tag(xml, cls.XL_TR_PATTERN, process_tr)

    @classmethod
    def _process_xl_tc(cls, xml: str) -> str:
        def process_tc(match):
            attrs, content = match.groups()
            width, span, align, merge, border_top, border_bottom, border_left, border_right = cls._extract_attrs(
                attrs, ['width', 'span', 'align', 'merge', 'border-top', 'border-bottom', 'border-left', 'border-right']
            )

            # 如果align为None，设置默认值为center
            if align is None:
                align = 'center'

            # 如果内容不包含标签，包装为段落
            if not re.search(r'<[^>]+>', content):
                content = f'<xl-p>{content}</xl-p>'

            tc_props_str = ''
            # 添加各种单元格属性
            tc_props_str += f'<w:tcW w:type="dxa" w:w="{width}"/>' if width else ''
            tc_props_str += f'<w:gridSpan w:val="{span}"/>' if span else ''
            tc_props_str += f'<w:vAlign w:val="{align}"/>' if align else ''
            tc_props_str += '<w:vMerge w:val="restart"/>' if merge == 'start' else ('<w:vMerge/>' if merge else '')
            tc_props_str += f'<w:top w:val="nil"/>' if border_top == 'none' else ''
            tc_props_str += f'<w:bottom w:val="nil"/>' if border_bottom == 'none' else ''
            tc_props_str += f'<w:left w:val="nil"/>' if border_left == 'none' else ''
            tc_props_str += f'<w:right w:val="nil"/>' if border_right == 'none' else ''
            
            return f'<w:tc>\n                    <w:tcPr>{tc_props_str}</w:tcPr>{content}</w:tc>'
        
        data = cls._process_tag(xml, cls.XL_TC_PATTERN, process_tc)
        return data
    
    @classmethod
    def decompile(cls, xml: str) -> str:
        """将w:tbl标签转换为xl-table标签"""
        xml = cls.decompile_tbl(xml)
        xml = cls.decompile_tr(xml)
        xml = cls.decompile_tblgrid(xml)
        return xml

    @classmethod
    def decompile_tbl(cls, xml: str) -> str:
        def process_word_table(match):
            full_tbl = match.group(0)
            styles = {}
            grid_str = ''
            width_str = ''
            
            # 提取对齐方式
            align_match = re.search(cls.W_JC_PATTERN, full_tbl)
            if align_match:
                styles['align'] = align_match.group(1)
            
            # 提取边框样式
            border_match = re.search(cls.W_TBLBORDERS_PATTERN, full_tbl, re.DOTALL)
            if border_match:
                border_content = border_match.group(1)
                # 检查是否所有边框都是none
                if re.search(r'w:val="none"', border_content) and not re.search(r'w:val="single"', border_content):
                    styles['border'] = 'none'
            
            # 提取左边距设置
            tbl_ind_match = re.search(r'<w:tblInd\s+w:w="([^"]+)"\s+w:type="dxa"/>', full_tbl)
            if tbl_ind_match:
                margin_left = tbl_ind_match.group(1)
                if margin_left != '0':
                    styles['margin-left'] = margin_left
            
            # 提取表格宽度
            tbl_w_match = re.search(r'<w:tblW\s+w:w="([^"]+)"\s+w:type="dxa"/>', full_tbl)
            if tbl_w_match:
                width_str = tbl_w_match.group(1)
            
            # 提取列宽设置
            grid_match = re.search(cls.W_TBLGRID_PATTERN, full_tbl, re.DOTALL)
            if grid_match:
                grid_content = grid_match.group(1)
                col_widths = re.findall(cls.W_GRIDCOL_PATTERN, grid_content)
                if col_widths:
                    grid_str = '/'.join(col_widths)
            
            # 提取表格内容
            content_match = re.search(r'<w:tbl>.*?<w:tblPr>.*?</w:tblPr>(.*?)</w:tbl>', full_tbl, re.DOTALL)
            content = content_match.group(1) if content_match else ""
            
            # 移除tblGrid内容，避免重复处理
            content = re.sub(cls.W_TBLGRID_PATTERN, '', content, flags=re.DOTALL)
            
            style_str = cls._build_style_str(styles)
            grid_attr = f' grid="{grid_str}"' if grid_str else ""
            width_attr = f' width="{width_str}"' if width_str else ""
            style_attr = f' style="{style_str}"' if style_str else ""
            return f'<xl-table{width_attr}{grid_attr}{style_attr}>{content}</xl-table>'
        
        return cls._process_tag(xml, cls.W_TBL_PATTERN, process_word_table)

    @classmethod
    def decompile_tblgrid(cls, xml: str) -> str:
        """将单独的w:tblGrid标签转换为xl-table标签"""
        def process_tblgrid(match):
            grid_content = match.group(0)
            col_widths = re.findall(cls.W_GRIDCOL_PATTERN, grid_content)
            if col_widths:
                grid_str = '/'.join(col_widths)
                return f'<xl-table grid="{grid_str}"/>'
            return match.group(0)
        
        return cls._process_tag(xml, cls.W_TBLGRID_PATTERN, process_tblgrid)

    @classmethod
    def decompile_tr(cls, xml: str) -> str:
        def process_w_tr(match):
            full_tr = match.group(0)
            content = match.group(1)
            attrs = {}

            # 提取行属性
            tr_pr_match = re.search(cls.W_TRPR_PATTERN, full_tr, flags=re.DOTALL)
            tr_pr_str = tr_pr_match.group(1) if tr_pr_match else ''

            # 检查表头属性
            if '<w:tblHeader/>' in tr_pr_str:
                attrs['header'] = '1'
            
            # 检查不可分割属性
            if '<w:cantSplit/>' in tr_pr_str:
                attrs['cant-split'] = '1'
            
            # 提取高度属性
            height_match = re.search(cls.W_TRHEIGHT_PATTERN, tr_pr_str)
            if height_match:
                attrs['height'] = height_match.group(1)

            # 提取对齐属性
            align_match = re.search(cls.W_JC_PATTERN, tr_pr_str)
            if align_match:
                attrs['align'] = align_match.group(1)
            
            attrs_str = cls._build_attr_str(attrs)

            def process_w_tc(match):
                full_tc = match.group(0)

                tc_pr_match = re.search(r'<w:tcPr>(.*?)</w:tcPr>', full_tc, re.DOTALL)
                tc_pr_str = tc_pr_match.group(1) if tc_pr_match else ''

                attrs = {}
                
                width_match = re.search(r'<w:tcW.*w:w="([^"]+)".*/>', tc_pr_str)
                if width_match:
                    attrs['width'] = width_match.group(1)

                # 提取边框属性
                border_top = cls._extract(cls.BORDER_TOP_PATTERN, tc_pr_str)
                if border_top in ['nil', 'none'] or re.search(cls.BORDER_SIZE_ZERO_PATTERN, tc_pr_str):
                    attrs['border-top'] = 'none'

                border_bottom = cls._extract(cls.BORDER_BOTTOM_PATTERN, tc_pr_str)
                if border_bottom in ['nil', 'none'] or re.search(cls.BORDER_SIZE_ZERO_PATTERN, tc_pr_str):
                    attrs['border-bottom'] = 'none'

                border_left = cls._extract(cls.BORDER_LEFT_PATTERN, tc_pr_str)
                if border_left in ['nil', 'none'] or re.search(cls.BORDER_SIZE_ZERO_PATTERN, tc_pr_str):
                    attrs['border-left'] = 'none'

                border_right = cls._extract(cls.BORDER_RIGHT_PATTERN, tc_pr_str)
                if border_right in ['nil', 'none'] or re.search(cls.BORDER_SIZE_ZERO_PATTERN, tc_pr_str):
                    attrs['border-right'] = 'none'

                span_match = re.search(r'<w:gridSpan\s+w:val="([^"]+)"/>', tc_pr_str)
                if span_match:
                    attrs['span'] = span_match.group(1)
                
                align_match = re.search(r'<w:vAlign\s+w:val="([^"]+)"/>', tc_pr_str)
                if align_match:
                    attrs['align'] = align_match.group(1)
                
                vmerge_match = re.search(r'<w:vMerge(?:\s+w:val="([^"]+)")?/>', tc_pr_str)
                if vmerge_match:
                    val = vmerge_match.group(1)
                    if val == "restart":
                        attrs['merge'] = 'start'
                    else:
                        attrs['merge'] = 'continue'
                
                content_match = re.search(r'<w:tc>.*?<w:tcPr>.*?</w:tcPr>(.*?)</w:tc>', full_tc, re.DOTALL)
                content = content_match.group(1) if content_match else ""
                
                attrs_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items()]) if attrs else ""
                if attrs_str:
                    return f'<xl-tc {attrs_str}>{content}</xl-tc>'
                else:
                    return f'<xl-tc>{content}</xl-tc>'
        
            # 处理所有表格单元格
            matches = list(re.finditer(cls.W_TC_PATTERN, content, re.DOTALL))
            content = ''
            for match in matches:
                full_tc = match.group(0)
                full_tc = cls._process_tag(full_tc, cls.W_TC_PATTERN, process_w_tc)
                content += full_tc
            
            # 根据是否为表头返回不同的标签
            if 'header' in attrs:
                if attrs_str:
                    return f'<xl-th {attrs_str}>{content}</xl-th>'
                else:
                    return f'<xl-th>{content}</xl-th>'
            else:
                if attrs_str:
                    return f'<xl-tr {attrs_str}>{content}</xl-tr>'
                else:
                    return f'<xl-tr>{content}</xl-tr>'
        
        return cls._process_tag(xml, cls.W_TR_PATTERN, process_w_tr)
