import os
from typing import List, Dict
from datetime import datetime
def print_file_list(files: List[Dict[str, any]]):
    """
    美观地打印文件列表信息
    
    参数:
        files (List[Dict]): 文件信息列表，每个元素包含"path"、"size"和"last_modified"键
    """
    if not files:
        print("没有文件需要显示")
        return
    
    # 计算列宽
    max_path_length = max(len(file["relPath"]) for file in files)
    max_path_length = max(max_path_length, len("路径"))
    
    max_type_length = max(len(file["contentType"]) for file in files if file["contentType"] is not None)
    max_type_length = max(max_type_length, len("类型"))
    
    # 表头
    header = f"{'路径':<{max_path_length}} | {'类型':<{max_type_length}} | {'大小':<10} | {'最后修改时间':<20}"
    print(header)
    print("-" * len(header))
    
    # 文件信息
    for file in files:
        path = file["relPath"]
        size = file["size"]
        content_type = file["contentType"]
        last_modified = datetime.fromtimestamp(file["lastModified"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        # 格式化文件大小
        size_str = format_file_size(size)
        
        print(f"{path:<{max_path_length}} | {content_type:<{max_type_length}} | {size_str:<10} | {last_modified:<20}")

def format_file_size(size_bytes: int) -> str:
    """
    将字节大小格式化为人类可读的格式
    
    参数:
        size_bytes (int): 文件大小（字节）
        
    返回:
        str: 格式化后的文件大小
    """
    if size_bytes == 0:
        return "0B"
    
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_units) - 1:
        size /= 1024.0
        i += 1
        
    return f"{size:.1f}{size_units[i]}"