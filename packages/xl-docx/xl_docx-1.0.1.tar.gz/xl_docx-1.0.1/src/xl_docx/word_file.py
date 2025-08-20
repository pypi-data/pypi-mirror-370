from xl_docx.utils.fake_zip import FakeZip
from xl_docx.utils.tree import Tree, E
from xl_docx.mixins import RelationMixin


class WordFile(RelationMixin, FakeZip):
    '''Word文档对象'''
    def __init__(self, file_path):
        super().__init__(file_path)

    def add_image(self, image_bytes, filename=None, xml_filename='document.xml'):
        image_id = self._generate_random_id()
        image_filename = filename or f'{image_id}.jpeg'
        self[f'word/media/{image_filename}'] = image_bytes
        
        rid = self.append_relation(
            xml_filename,
            'image',
            f'media/{image_filename}',
            image_id
        )
        return rid
    
    def add_xml(self, xml_type, xml_content, relation_id=None):
        '''添加xml文件
        
        Args:
            xml_type: xml文件类型
            xml_content: xml文件内容
            relation_id: 关系ID，如果为None则自动生成
            
        Returns:
            str: 生成的关系ID，格式为'rId{xml_id}'
        '''
        xml_id = relation_id or self._generate_random_id()
        xml_filename = f'{xml_type}{xml_id}.xml'
        self.register_xml(xml_type, xml_filename)
        self[f'word/{xml_filename}'] = xml_content
        self.append_relation('document.xml', xml_type, xml_filename, xml_id)
        return f'rId{xml_id}'

    def register_xml(self, xml_type, xml_filename):
        '''注册xml类型到Content_Types.xml
        
        Args:
            xml_type: xml文件类型
            xml_filename: xml文件名
            
        Returns:
            self: 返回实例本身以支持链式调用
        '''
        content_type_tree = Tree(self['[Content_Types].xml'])
        content_type_tree += E.Override(
            ContentType=f'application/vnd.openxmlformats-officedocument.wordprocessingml.{xml_type}+xml',
            PartName=f'/word/{xml_filename}'
        )
        self['[Content_Types].xml'] = bytes(content_type_tree)
        return 

    def register_img(self):
        content_type_tree = Tree(self['[Content_Types].xml'])

        for elem in content_type_tree.xpath('//*[local-name()="Default" and (@Extension="jpeg" or @Extension="png" or @Extension="jpg")]'):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

        content_type_tree += E.Default(
            ContentType=f'image/jpeg',
            Extension=f'jpeg', 
        )
        content_type_tree += E.Default(
            ContentType=f'image/jpeg',
            Extension=f'jpg', 
        )
        content_type_tree += E.Default(
            ContentType=f'image/png',
            Extension=f'png', 
        )
        self['[Content_Types].xml'] = bytes(content_type_tree)
        return self
