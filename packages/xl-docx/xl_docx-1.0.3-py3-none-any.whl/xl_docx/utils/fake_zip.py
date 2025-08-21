from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from typing import Union, Dict, BinaryIO, List, Optional
import os


class FakeZip:
    """伪Zip对象，用于在内存中存储和修改ZIP文件内容
    
    这个类提供了一个字典式接口来存储和修改ZIP文件的内容，解决了ZipFile无法直接替换文件的限制。
    所有文件内容都存储在内存中，方便随时修改。
    
    Attributes:
        _contents: 存储文件内容的字典，key为文件名，value为文件内容
    """

    def __init__(self, file_path: Union[str, bytes]):
        """初始化FakeZip对象
        
        Args:
            file_path: ZIP文件路径或ZIP文件的二进制内容
        """
        self._contents: Dict[str, bytes] = {}
        self._load_zip(file_path)

    def _load_zip(self, file_path: Union[str, bytes]) -> None:
        """从ZIP文件加载内容
        
        Args:
            file_path: ZIP文件路径或ZIP文件的二进制内容
        """
        zip_file = ZipFile(BytesIO(file_path), 'r') if isinstance(file_path, bytes) else ZipFile(file_path)
        with zip_file:
            for file_info in zip_file.infolist():
                self._contents[file_info.filename] = zip_file.open(file_info).read()

    def __getitem__(self, filename: str) -> bytes:
        """获取指定文件的内容
        
        Args:
            filename: 文件名
            
        Returns:
            文件的二进制内容
        """
        return self._contents.get(filename)

    def __setitem__(self, filename: str, content: bytes) -> None:
        """设置或更新文件内容
        
        Args:
            filename: 文件名
            content: 文件的二进制内容
        """
        self._contents[filename] = content

    def __bytes__(self) -> bytes:
        """将整个ZIP内容转换为字节串
        
        Returns:
            ZIP文件的二进制内容
        """
        with BytesIO() as buffer:
            self.write(buffer)
            return buffer.getvalue()

    def write_to_buffer(self):
        buffer = BytesIO()
        self.write(buffer)
        return buffer

    def write(self, file_obj: BinaryIO) -> None:
        """将内容写入到文件对象
        
        Args:
            file_obj: 要写入的二进制文件对象
        """
        with ZipFile(file_obj, mode='w', compression=ZIP_DEFLATED) as zip_file:
            for filename, content in self._contents.items():
                zip_file.writestr(filename, content)

    def save(self, path: str) -> None:
        """保存为ZIP文件
        
        Args:
            path: 目标文件路径
        """
        with open(path, 'wb') as f:
            self.write(f)

    def list_files(self) -> List[str]:
        """列出ZIP中的所有文件
        
        Returns:
            文件名列表
        """
        return list(self._contents.keys())

    def extract(self, filename: str, path: Optional[str] = None) -> Union[bytes, str]:
        """提取指定文件
        
        Args:
            filename: 要提取的文件名
            path: 可选的保存路径。如果提供，文件将被保存到该路径
            
        Returns:
            如果未提供path，返回文件的二进制内容；否则返回保存的文件路径
        """
        content = self._contents.get(filename)
        if content is None:
            raise KeyError(f"File {filename} not found in zip")
            
        if path:
            full_path = os.path.join(path, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f:
                f.write(content)
            return full_path
        return content

    def add_file(self, filename: str, content: Union[str, bytes]) -> None:
        """添加文件到ZIP
        
        Args:
            filename: 文件名
            content: 文件内容，可以是字符串或字节串
        """
        if isinstance(content, str):
            content = content.encode('utf-8')
        self._contents[filename] = content

    def remove_file(self, filename: str) -> None:
        """从ZIP中删除文件
        
        Args:
            filename: 要删除的文件名
        """
        if filename in self._contents:
            del self._contents[filename]

    def clear(self) -> None:
        """清空ZIP中的所有内容"""
        self._contents.clear()
