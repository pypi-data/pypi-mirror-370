import re


class BaseProcessor:
    """XML处理器基类"""
    
    # 正则表达式模式常量，提高可读性
    ATTR_VALUE_PATTERN = r'''
        {attr_name}="              # 属性名和等号
        ([^"]*)                    # 属性值（不包含引号）
        "                          # 结束引号
    '''
    
    @classmethod
    def compile(cls, xml):
        raise NotImplementedError

    @staticmethod
    def retrieve(dict_, keys):
        """字典解构赋值
        params = {'a': 1, 'b': 2}
        a, b = get(params, ['a', 'b'])
        a, c = get(params, ['a', 'c'])
        """
        tmp = ()
        for key in keys:
            tmp += (dict_.get(key),)
        return tmp

    @classmethod
    def _process_tag(cls, xml, pattern, process_func, flags=re.DOTALL | re.VERBOSE):
        """通用标签处理方法"""
        return re.sub(pattern, process_func, xml, flags=flags)

    @classmethod
    def _extract_attrs(cls, attrs_str, attr_names):
        """提取属性值"""
        result = []
        for name in attr_names:
            # 构建动态正则表达式模式
            pattern = cls.ATTR_VALUE_PATTERN.format(attr_name=re.escape(name))
            match = re.search(pattern, attrs_str, flags=re.VERBOSE)
            result.append(match.group(1) if match else None)
        return tuple(result)
    
    @classmethod
    def _extract(cls, pattern, xml):
        """使用正则表达式提取值"""
        match = re.search(pattern, xml)
        return match.group(1) if match else None
    
    @classmethod
    def _parse_style_str(cls, style_str):
        """解析样式字符串为字典
        例如: "font-size:12px;color:red" -> {"font-size": "12px", "color": "red"}
        支持带空格的样式字符串，如"font-size: 12px; color: red; margin: 10px"
        """
        if not style_str:
            return {}
        result = {}
        for pair in style_str.split(';'):
            if pair.strip():
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    result[key.strip()] = value.strip()
        return result
    @classmethod
    def _build_style_str(cls, styles):
        """将样式字典转换为字符串
        例如: {"font-size": "12px", "color": "red"} -> "font-size:12px;color:red"
        """
        if not styles:
            return ''
        return ';'.join(f"{k.strip()}:{v.strip()}" for k, v in styles.items())

    @classmethod
    def _build_attr_str(cls, attrs):
        """将属性字典转换为字符串
        例如: {"font-size": "12px", "color": "red"} -> "font-size:12px;color:red"
        """
        if not attrs:
            return ''
        return ' '.join(f'{k}="{v}"' for k, v in attrs.items())