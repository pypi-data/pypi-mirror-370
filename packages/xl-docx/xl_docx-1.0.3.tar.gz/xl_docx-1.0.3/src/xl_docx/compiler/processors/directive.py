from xl_docx.compiler.processors.base import BaseProcessor
import re


class DirectiveProcessor(BaseProcessor):
    """处理Vue指令相关的XML标签"""
    
    # 正则表达式模式常量，提高可读性
    V_IF_PATTERN = r'<([^\s>]+)[^>]*v-if="([^"]*)"[^>]*>'
    V_FOR_PATTERN = r'<([^\s>]+)[^>]*v-for="([^"]*)"[^>]*>'
    
    # Jinja2模板模式
    JINJA_IF_PATTERN = r'''
        {%\s*if\s+                   # 开始if标签
        ([^%]+)                      # 条件表达式
        \s*%}                        # 结束标签
        (.*?)                        # 内容（非贪婪匹配）
        {%\s*endif\s*%}              # 结束if标签
    '''
    
    JINJA_FOR_PATTERN = r'''
        {%\s*for\s+                  # 开始for标签
        ([^%]+)                      # 循环表达式
        \s*%}                        # 结束标签
        (.*?)                        # 内容（非贪婪匹配）
        {%\s*endfor\s*%}             # 结束for标签
    '''
    
    # 标签匹配模式
    TAG_WITH_ATTRS_PATTERN = r'''
        <([^\s>]+)                   # 标签名
        ([^>]*)>                     # 属性
        (.*)                         # 内容
        </\1>                        # 结束标签
    '''
    
    @classmethod
    def compile(cls, xml: str) -> str:
        xml = cls._process_v_if(xml)
        xml = cls._process_v_for(xml)
        return xml
        
    @classmethod
    def _process_v_if(cls, xml: str) -> str:
        result = xml
        for match in re.finditer(cls.V_IF_PATTERN, xml):
            tag_name, condition = match.groups()
            start_pos = match.end()
            
            # 找到匹配的结束标签
            stack = 1
            pos = start_pos
            while stack > 0 and pos < len(xml):
                if xml[pos:pos+2] == '</' and xml[pos:pos+len(tag_name)+3] == f'</{tag_name}>':
                    stack -= 1
                    if stack == 0:
                        end_pos = pos + len(tag_name) + 3
                        break
                elif xml[pos] == '<' and not xml[pos:pos+2].startswith('</'):
                    # 找到开始标签
                    tag_end = xml.find('>', pos)
                    if tag_end != -1:
                        inner_tag = xml[pos:tag_end+1]
                        if inner_tag.startswith(f'<{tag_name}') or inner_tag.startswith(f'<{tag_name} '):
                            stack += 1
                pos += 1
            else:
                # 没有找到匹配的结束标签，跳过这个匹配
                continue
            
            # 提取内容
            content = xml[start_pos:pos]
            
            # 提取原始标签的属性（除了v-if）
            original_tag = match.group(0)
            # 移除v-if指令
            tag_without_v_if = re.sub(r'\s+v-if="[^"]*"', '', original_tag)
            
            # 构建新的标签
            new_tag = f'{tag_without_v_if}{content}</{tag_name}>'
            replacement = f'{{% if {condition} %}}{new_tag}{{% endif %}}'
            
            # 替换整个匹配的部分
            result = result.replace(xml[match.start():end_pos], replacement)
            
        return result

    @classmethod
    def _process_v_for(cls, xml: str) -> str:
        result = xml
        for match in re.finditer(cls.V_FOR_PATTERN, xml):
            tag_name, loop_expr = match.groups()
            start_pos = match.end()
            
            # 找到匹配的结束标签
            stack = 1
            pos = start_pos
            while stack > 0 and pos < len(xml):
                if xml[pos:pos+2] == '</' and xml[pos:pos+len(tag_name)+3] == f'</{tag_name}>':
                    stack -= 1
                    if stack == 0:
                        end_pos = pos + len(tag_name) + 3
                        break
                elif xml[pos] == '<' and not xml[pos:pos+2].startswith('</'):
                    # 找到开始标签
                    tag_end = xml.find('>', pos)
                    if tag_end != -1:
                        inner_tag = xml[pos:tag_end+1]
                        if inner_tag.startswith(f'<{tag_name}') or inner_tag.startswith(f'<{tag_name} '):
                            stack += 1
                pos += 1
            else:
                # 没有找到匹配的结束标签，跳过这个匹配
                continue
            
            # 提取内容
            content = xml[start_pos:pos]
            
            # 解析循环表达式：item in items
            item, items = loop_expr.split(' in ')
            item = item.strip()
            items = items.strip()
            
            # 提取原始标签的属性（除了v-for）
            original_tag = match.group(0)
            # 移除v-for指令
            tag_without_v_for = re.sub(r'\s+v-for="[^"]*"', '', original_tag)
            
            # 构建新的标签
            new_tag = f'{tag_without_v_for}{content}</{tag_name}>'
            replacement = f'{{% for {item} in {items} %}}{new_tag}{{% endfor %}}'
            
            # 替换整个匹配的部分
            result = result.replace(xml[match.start():end_pos], replacement)
            
        return result

    @classmethod
    def decompile2222222222222222222222(cls, xml: str) -> str:
        """将Jinja2模板转换回Vue指令"""
        xml = cls._decompile_v_if(xml)
        xml = cls._decompile_v_for(xml)
        return xml

    @classmethod
    def _decompile_v_if(cls, xml: str) -> str:
        def process_if(match):
            condition, tag_content = match.groups()
            # 清理条件表达式中的前后空格
            condition = condition.strip()
            # 提取标签名和属性
            tag_match = re.match(cls.TAG_WITH_ATTRS_PATTERN, tag_content, flags=re.VERBOSE)
            if tag_match:
                tag_name, attrs, content = tag_match.groups()
                # 清理属性中的前导空格
                attrs = attrs.strip()
                # 如果有属性，添加空格分隔符
                attrs_str = f' {attrs}' if attrs else ''
                return f'<{tag_name} v-if="{condition}"{attrs_str}>{content}</{tag_name}>'
            return match.group(0)

        return cls._process_tag(xml, cls.JINJA_IF_PATTERN, process_if)

    @classmethod
    def _decompile_v_for(cls, xml: str) -> str:
        def process_for(match):
            loop_expr, tag_content = match.groups()
            # 清理循环表达式中的前后空格
            loop_expr = loop_expr.strip()
            # 提取标签名和属性
            tag_match = re.match(cls.TAG_WITH_ATTRS_PATTERN, tag_content, flags=re.VERBOSE)
            if tag_match:
                tag_name, attrs, content = tag_match.groups()
                # 清理属性中的前导空格
                attrs = attrs.strip()
                # 如果有属性，添加空格分隔符
                attrs_str = f' {attrs}' if attrs else ''
                # 解析循环表达式
                item, items = loop_expr.split(' in ')
                return f'<{tag_name} v-for="{item.strip()} in {items.strip()}"{attrs_str}>{content}</{tag_name}>'
            return match.group(0)

        return cls._process_tag(xml, cls.JINJA_FOR_PATTERN, process_for)
