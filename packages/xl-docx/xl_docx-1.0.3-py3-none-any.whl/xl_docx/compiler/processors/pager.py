from xl_docx.compiler.processors.base import BaseProcessor
import re


class PagerProcessor(BaseProcessor):
    """处理页码相关的XML标签"""
    
    # 正则表达式模式常量，提高可读性
    XL_PAGER_PATTERN = r'''
        <xl-pager                     # 开始标签
        .*?                          # 任意属性（非贪婪匹配）
        />                           # 自闭合标签
    '''
    
    def compile(self, xml: str) -> str:
        def process_pager(match):
            style, = self._extract_attrs(match.group(0), ['style'])
            styles = self._parse_style_str(style)
            
            # 获取样式属性，使用默认值
            font_size = styles.get('font-size', '21')
            english_font = styles.get('english', 'Times New Roman')
            chinese_font = styles.get('chinese', 'SimSun')

            return f'''<w:sdt>
						<w:sdtPr>
							<w:id w:val="98381352"/>
							<w:docPartObj>
								<w:docPartGallery w:val="Page Numbers (Top of Page)"/>
								<w:docPartUnique/>
							</w:docPartObj>
						</w:sdtPr>
						<w:sdtEndPr>
							<w:rPr>
								<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
								<w:szCs w:val="{font_size}"/>
							</w:rPr>
						</w:sdtEndPr>
						<w:sdtContent>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="宋体" w:hint="eastAsia"/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:t>第</w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:szCs w:val="{font_size}"/>
									<w:lang w:val="zh-CN"/>
								</w:rPr>
								<w:t xml:space="preserve"> </w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:fldChar w:fldCharType="begin"/>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:instrText>PAGE</w:instrText>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:fldChar w:fldCharType="separate"/>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:noProof/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:t>2</w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:fldChar w:fldCharType="end"/>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:szCs w:val="{font_size}"/>
									<w:lang w:val="zh-CN"/>
								</w:rPr>
								<w:t xml:space="preserve"> </w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="宋体" w:hint="eastAsia"/>
									<w:szCs w:val="{font_size}"/>
									<w:lang w:val="zh-CN"/>
								</w:rPr>
								<w:t>页</w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:szCs w:val="{font_size}"/>
									<w:lang w:val="zh-CN"/>
								</w:rPr>
								<w:t xml:space="preserve"> </w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="宋体" w:hint="eastAsia"/>
									<w:szCs w:val="{font_size}"/>
									<w:lang w:val="zh-CN"/>
								</w:rPr>
								<w:t>共</w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:szCs w:val="{font_size}"/>
									<w:lang w:val="zh-CN"/>
								</w:rPr>
								<w:t xml:space="preserve"> </w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:fldChar w:fldCharType="begin"/>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:instrText>NUMPAGES</w:instrText>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:fldChar w:fldCharType="separate"/>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:noProof/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:t>2</w:t>
							</w:r>
							<w:r>
								<w:rPr>
									<w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
									<w:b/>
									<w:bCs/>
									<w:szCs w:val="{font_size}"/>
								</w:rPr>
								<w:fldChar w:fldCharType="end"/>
							</w:r>
                            <w:r>
                                <w:rPr>
                                    <w:rFonts w:ascii="{english_font}" w:hAnsi="{chinese_font}"/>
                                    <w:szCs w:val="{font_size}"/>
                                </w:rPr>
                                <w:t xml:space="preserve"> </w:t>
                            </w:r>
                            <w:r>
                                <w:rPr>
                                    <w:rFonts w:ascii="{english_font}" w:hAnsi="宋体" w:hint="eastAsia"/>
                                    <w:szCs w:val="{font_size}"/>
                                </w:rPr>
                                <w:t>页</w:t>
                            </w:r>
						</w:sdtContent>
					</w:sdt>'''

        return self._process_tag(xml, self.XL_PAGER_PATTERN, process_pager, flags=re.VERBOSE)
