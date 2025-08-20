from xl_docx.utils.tree import Tree, E
import random
from lxml import etree


class RelationMixin:
    """处理Word文档中的资源关系映射"""

    RELATIONSHIP_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/relationships"
    OFFICE_RELATIONSHIP_PREFIX = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    DEFAULT_RELATIONS_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="{RELATIONSHIP_NAMESPACE}"></Relationships>"""

    def _generate_random_id(self):
        """生成随机的关系ID"""
        return random.randint(1000, 9999)

    def _get_relation_path(self, xml_file):
        """构建关系文件路径
        
        Args:
            xml_file: XML文件名
            
        Returns:
            str: 关系文件完整路径
        """
        return f'word/_rels/{xml_file}.rels'

    def _build_relationship_type(self, relation_type):
        """构建完整的关系类型URI
        
        Args:
            relation_type: 关系类型名称
            
        Returns:
            str: 完整的关系类型URI
        """
        return f"{self.OFFICE_RELATIONSHIP_PREFIX}/{relation_type}"

    def get_relations(self, xml_file):
        """获取指定xml文件的资源映射
        
        Args:
            xml_file: XML文件名,如 'document.xml'
            
        Returns:
            bytes: 关系文件内容
        """
        return self[self._get_relation_path(xml_file)]

    def write_relations(self, xml_file, relations):
        """写入指定xml文件的资源映射
        
        Args:
            xml_file: XML文件名
            relations: 要写入的关系内容
        """
        self[self._get_relation_path(xml_file)] = relations

    def append_relation(self, xml_file, relation_type, relation_target, relation_id=None):
        """添加单条资源映射
        
        Args:
            xml_file: XML文件名,如 'document.xml'
            relation_type: 关系类型,如 'footer'
            relation_target: 目标文件路径
            relation_id: 可选的关系ID
            
        Returns:
            str: 生成的关系ID标识符
        """
        relations = self.get_relations(xml_file) or self.DEFAULT_RELATIONS_XML.encode()
        relation_tree = Tree(relations)
        
        relation_id = relation_id or self._generate_random_id()
        rid = f'rId{relation_id}'
        
        relation_type = self._build_relationship_type(relation_type)
        relation_tree += E.Relationship(Id=rid, Type=relation_type, Target=relation_target)
        
        self.write_relations(xml_file, bytes(relation_tree))
        return rid

    def merge_relations(self, relations_a, relations_b):
        """合并两个关系文件的内容
        
        Args:
            relations_a: 主关系文件内容
            relations_b: 要合并的关系列表
            
        Returns:
            bytes: 合并后的关系文件内容
        """
        relation_tree = etree.fromstring(relations_a)
        for relation in relations_b:
            relation_element = E.Relationship(
                Id=relation['id'],
                Type=relation['type'],
                Target=relation['target']
            )
            relation_tree.append(relation_element)
        return etree.tostring(relation_tree)
