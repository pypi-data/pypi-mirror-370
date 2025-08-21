"""
内置组件库
提供xl-docx的内置Word组件模板
"""

from pathlib import Path

# 获取内置组件库的根目录
COMPONENTS_DIR = Path(__file__).parent

def get_builtin_components():
    """获取所有内置组件文件"""
    return [f for f in COMPONENTS_DIR.rglob('*.xml')]

def get_component_content(component_name):
    """获取指定组件的XML内容
    
    Args:
        component_name: 组件名称
        
    Returns:
        str: 组件XML内容，如果组件不存在则返回None
    """
    components = get_builtin_components()
    if component_name in components:
        with open(components[component_name], 'r', encoding='utf-8') as f:
            return f.read()
    return None 