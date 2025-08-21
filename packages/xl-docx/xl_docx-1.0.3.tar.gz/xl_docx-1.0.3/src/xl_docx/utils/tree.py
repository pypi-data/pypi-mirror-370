from lxml import etree
from lxml.builder import E


class Tree:
    def __init__(self, data):
        self.instance = etree.fromstring(data)

    def __add__(self, other):
        self.instance.append(other)
        return self
        
    def __bytes__(self):
        return etree.tostring(self.instance)
    
    def xpath(self, xpath):
        return self.instance.xpath(xpath)
        
    def find(self, xpath):
        """查找匹配xpath的第一个元素"""
        return self.instance.find(xpath)
        
    def findall(self, xpath):
        """查找所有匹配xpath的元素"""
        return self.instance.findall(xpath)
        
    def get_attr(self, xpath, attr):
        """获取指定xpath元素的属性值"""
        elem = self.find(xpath)
        return elem.get(attr) if elem is not None else None
        
    def set_attr(self, xpath, attr, value):
        """设置指定xpath元素的属性值"""
        elem = self.find(xpath)
        if elem is not None:
            elem.set(attr, value)
            
    def get_text(self, xpath):
        """获取指定xpath元素的文本内容"""
        elem = self.find(xpath)
        return elem.text if elem is not None else None
        
    def set_text(self, xpath, text):
        """设置指定xpath元素的文本内容"""
        elem = self.find(xpath)
        if elem is not None:
            elem.text = text
            
    def remove(self, xpath):
        """删除指定xpath的元素"""
        elem = self.find(xpath)
        if elem is not None:
            elem.getparent().remove(elem)
            
    def insert(self, xpath, element, position=0):
        """在指定xpath的元素下插入新元素"""
        parent = self.find(xpath)
        if parent is not None:
            parent.insert(position, element)
