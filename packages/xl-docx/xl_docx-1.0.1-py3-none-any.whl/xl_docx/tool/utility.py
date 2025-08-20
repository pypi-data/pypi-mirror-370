from xl_docx.word_file import WordFile 
from xl_docx.sheet import Sheet
from xl_docx.compiler.processors.paragraph import ParagraphProcessor
from xl_docx.compiler.processors.table import TableProcessor
from lxml import etree
import os
import json
import time
import re
import sys
from pathlib import Path

class SuperWordFile(WordFile):
    testing_word = ''  
    testing_xml = ''  

    def __init__(self, folder, file):
        path = os.path.join(folder, file)
        super().__init__(path)
        self.folder = folder

    @staticmethod
    def timestamp():
        return str(int(time.time()))

    def super_replace(self, file):
        path = os.path.join(self.folder, file)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                file_bytes = f.read()
                self.replace(f'word/{file}', file_bytes)

    def super_save(self, file):
        path = os.path.join(self.folder, file)
        self.save(path)

    def test(self):
        """测试文件"""
        python_file_path = os.path.join(self.folder, 'test.py')
        print(f'python {python_file_path}')
        os.system(f'python {python_file_path}')

    def extract(self, res_path, decompile=False):
        """提取XML文件"""
        dst_path = os.path.join(self.folder, f'{self.timestamp()}{res_path}')
        with open(dst_path, 'wb') as f:
            xml_string = self[f'word/{res_path}']
            root = etree.fromstring(xml_string)
            pretty_xml = etree.tostring(root, pretty_print=True, encoding='unicode')
            pretty_xml = pretty_xml.replace('\t', '    ')
            body_content = pretty_xml
            
            if decompile:
                # 反编译处理
                from xl_docx.compiler import XMLCompiler
                compiler = XMLCompiler()
                body_content = compiler.decompile_template(body_content)
            else:
                # 普通提取处理
                body_content = TableProcessor.compile(body_content)
                body_content = ParagraphProcessor.compile(body_content)
            
            f.write(body_content.encode())
        
        return dst_path  # 返回生成的文件路径

    @staticmethod
    def get_resource_path(relative_path):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).parent / relative_path

    @classmethod
    def word2xml(cls, orientation='h'):
        if cls.testing_word:
            return cls.extract_document(orientation)
        else:
            return cls.new_word(orientation)

    @classmethod
    def xml2word(cls, orientation='h'):
        if cls.testing_xml:
            return cls.create_word(orientation)
        else:
            return cls.new_xml(orientation)

    @classmethod
    def new_word(cls, orientation):
        docx_file = 'h.docx' if orientation == 'h' else 'v.docx'
        docx_path = cls.get_resource_path(docx_file)
        save_path = f'd:/tmp/{cls.timestamp()}test.docx'
        wf = WordFile(docx_path)
        wf.save(save_path)
        os.startfile(save_path)
        cls.testing_word = save_path

    @classmethod
    def extract_document(cls, orientation):
        wf = WordFile(cls.testing_word)
        save_path = f'd:/tmp/{cls.timestamp()}document.xml'
        with open(save_path, 'wb') as f:
            content = wf['word/document.xml'].decode()
            f.write(content.encode())
        os.startfile(save_path)
        cls.testing_word = ''
        return save_path

    @classmethod
    def new_xml(cls, orientation):
        docx_file = 'h.docx' if orientation == 'h' else 'v.docx'
        docx_path = cls.get_resource_path(docx_file)
        wf = WordFile(docx_path)
        save_path = f'd:/tmp/{cls.timestamp()}document.xml'
        with open(save_path, 'wb') as f:
            content = wf['word/document.xml']
            f.write(content)
        os.startfile(save_path)
        cls.testing_xml = save_path 

    @classmethod
    def create_word(cls, orientation):
        docx_file = 'h.docx' if orientation == 'h' else 'v.docx'
        docx_path = cls.get_resource_path(docx_file)
        wf = WordFile(docx_path)
        with open(cls.testing_xml, 'rb') as f:
            content = f.read().decode()
            
            # 添加编译处理
            from xl_docx.compiler import XMLCompiler
            compiler = XMLCompiler()
            content = compiler.compile_template(content)
            
            wf['word/document.xml'] = content.encode()
            save_path = f'd:/tmp/{cls.timestamp()}test.docx'
            wf.save(save_path)
            os.startfile(save_path)
            cls.testing_xml = ''
            return save_path

    

    
    
if __name__ == '__main__':
    wf = SuperWordFile(r'd:\git\lims\template\inspect\record - 副本','template.docx')
    wf.extract('document.xml')
    exit()
    wf = SuperWordFile('.','123.docx')
    # wf.extract('document.xml')
    # wf.write('document.xml', 'document2.xml')