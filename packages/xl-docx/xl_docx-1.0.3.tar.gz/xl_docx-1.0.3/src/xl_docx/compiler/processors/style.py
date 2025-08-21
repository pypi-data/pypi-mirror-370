from xl_docx.compiler.processors.base import BaseProcessor
import re
from lxml import etree
from cssselect import GenericTranslator


class StyleProcessor(BaseProcessor):
    """处理样式相关的XML标签"""
    
    # 正则表达式模式常量，提高可读性
    STYLE_TAG_PATTERN = r'''
        <style>                       # 开始标签
        (.*?)                         # 样式内容（非贪婪匹配）
        </style>                      # 结束标签
    '''
    
    TEMPLATE_TAG_PATTERN = r'{%.*?%}'  # Jinja2模板标签
    
    def __init__(self):
        self.styles = {}
        
    def compile(self, xml: str) -> str:
        xml = self._parse_styles(xml)
        xml = self._apply_styles(xml)
        return xml
        
    def _parse_styles(self, xml: str) -> str:
        def process_style_match(match):
            style_content = match.group(1)
            # 按大括号分割CSS规则
            rules = [rule.strip() for rule in style_content.split('}') if rule.strip()]
            for rule in rules:
                if '{' in rule:
                    # 分离选择器和样式声明
                    selector, styles = rule.split('{')
                    selector = selector.strip()
                    # 清理样式声明中的换行符和空格
                    styles = ''.join([style.strip() for style in styles.strip().split('\n')])
                    # 移除每个样式声明后的空格
                    styles = re.sub(r'(\w+):\s*', r'\g<1>:', styles)
                    if styles.endswith(';'):
                        styles = styles[:-1]
                    self.styles[selector] = styles
            return ''
            
        return self._process_tag(xml, r'<style>(.*?)</style>', process_style_match)

    def _apply_styles(self, xml: str) -> str:
        # 移除XML声明
        xml = re.sub(r'<\?xml[^>]*\?>', '', xml)
        
        # 保护Jinja2模板标签
        template_tags = []
        def replace_template_tag(match):
            tag = match.group(0)
            template_tags.append(tag)
            return f"<!--TEMPLATE_TAG_{len(template_tags)-1}-->"
            
        xml = re.sub(self.TEMPLATE_TAG_PATTERN, replace_template_tag, xml)
        
        try:
            # 解析XML
            parser = etree.XMLParser(remove_blank_text=True)
            xml =xml.replace(' < ', 'LESSTHAN')
            xml =xml.replace(' > ', 'GREATERTHAN')
            xml =xml.replace(' == ', 'EQUALTO')
            root = etree.fromstring(xml.encode(), parser)
            translator = GenericTranslator()
            
            # 应用CSS样式到匹配的元素
            for selector, style_str in self.styles.items():
                xpath_expr = translator.css_to_xpath(selector)
                matched_elements = root.xpath(xpath_expr)
                
                for elem in matched_elements:
                    current_style = elem.get('style', '')
                    # 合并现有样式和新样式
                    current_styles = self._parse_style_str(current_style)
                    new_styles = self._parse_style_str(style_str)
                    for key, value in new_styles.items():
                        if key not in current_styles: # current styles优先级更高
                            current_styles[key] = value
                    merged_style = self._build_style_str(current_styles)
                    elem.set('style', merged_style)
            
            # 转换回字符串
            result = etree.tostring(root, method='html', encoding='unicode')
            result = result.replace('LESSTHAN', ' < ')
            result = result.replace('GREATERTHAN', ' > ')
            result = result.replace('EQUALTO', ' == ')
            # 恢复Jinja2模板标签
            for i, tag in enumerate(template_tags):
                result = result.replace(f"<!--TEMPLATE_TAG_{i}-->", tag)
            return result
            
        except etree.XMLSyntaxError as e:
            raise e