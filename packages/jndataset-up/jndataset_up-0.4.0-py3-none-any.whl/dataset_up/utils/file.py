import os
import hashlib
from pathlib import Path
import platform
import magic


def list_files_in_folder(folder_path: str):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise Exception(f"path {folder_path} is not a dir or does not exist")
    folder_path = os.path.abspath(folder_path)
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not is_hidden(os.path.join(root, d))]
        for file in files:
            file_path = os.path.join(root, file)
            if not is_hidden(file_path):
                file_list.append(file_path)
    return file_list
            
        
    

def get_file_content(file_name):
    with open(file_name, encoding='utf-8') as f:
        content = f.read()
    return content


def sha256(file_path: str, buf_size: int = 131072):
    if not Path(file_path).is_file():
        raise Exception(f"file {file_path} does not exist")
    sha256_obj = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            sha256_obj.update(data)
    return sha256_obj.hexdigest()


def is_hidden(filepath):
    """
    跨平台判断文件是否为隐藏文件
    """
    path = Path(filepath)
    
    # Unix/Linux/macOS: 检查文件名是否以.开头
    if platform.system() != 'Windows':
        return path.name.startswith('.')
    
    # Windows: 检查文件属性
    else:
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            return attrs != -1 and bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN = 2
        except (ImportError, AttributeError):
            # 如果无法使用Windows API，则回退到检查文件名
            return path.name.startswith('.')
        




def get_file_type_by_magic(file_path):
    import locale
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
        
    # 创建 magic 对象
    mime = magic.Magic(mime=True)
    
    try:
        # 首先尝试直接使用文件路径
        file_type = mime.from_file(file_path)
        if 'cannot open' in file_type or not file_type:
            raise Exception(f"magic无法读取文件: {file_path}")
        if file_type == 'text/plain':
            if file_path.endswith('.json') or file_path.endswith('.jsonl'):
                file_type = 'application/json'
            if file_path.endswith('.csv'):
                file_type = 'text/csv'
        return file_type
    except Exception as e:
        print(f"magic 获取文件MIME出错: {e}")
        return get_file_type_by_header(file_path)
    
    

def get_file_type_by_header(file_path):
    """
    通过读取文件前几个字节来判断文件类型
    """
    try:
        with open(file_path, 'rb') as f:
            # 读取文件前16个字节用于判断文件类型
            header = f.read(16)
            
        # 定义常见文件类型的签名
        file_signatures = {
            b'\x89PNG\r\n\x1a\n': 'image/png',
            b'\xff\xd8\xff': 'image/jpeg',
            b'GIF87a': 'image/gif',
            b'GIF89a': 'image/gif',
            b'RIFF': 'audio/x-wav',
            b'PK\x03\x04': 'application/zip',
            b'PK\x05\x06': 'application/zip',
            b'PK\x07\x08': 'application/zip',
            b'%PDF': 'application/pdf',
            b'\x1f\x8b': 'application/gzip',
            b'BZh': 'application/x-bzip2',
            b'7z\xbc\xaf\x27\x1c': 'application/x-7z-compressed',
            b'\x00\x00\x00\x18ftypmp4': 'video/mp4',
            b'\x00\x00\x00\x20ftypmp4': 'video/mp4',
            b'ftypqt': 'video/quicktime',  # MOV文件
            b'ftyp': 'video/mp4',
            b'\x1aE\xdf\xa3': 'video/x-matroska',
            b'FLV\x01': 'video/x-flv',
            b'\x00\x00\x01\xba': 'video/mpeg',
            b'RIFF....AVI ': 'video/x-msvideo',
            b'\x30\x26\xb2\x75\x8e\x66\xcf\x11': 'video/x-ms-wmv',
            b'ID3': 'audio/mpeg',
            b'\xff\xfb': 'audio/mpeg',
            b'\xff\xf3': 'audio/mpeg',
            b'\xff\xf2': 'audio/mpeg',
            b'OTTO': 'application/font-sfnt',  # OpenType font
            b'\x00\x01\x00\x00': 'application/font-sfnt',  # TrueType font
            b'wOFF': 'application/font-woff',
            b'wOF2': 'application/font-woff2',
            b'\x00\x00\x01\x00': 'image/x-icon',  # ICO file
            b'CWS': 'application/x-shockwave-flash',
            b'FWS': 'application/x-shockwave-flash',
            b'ZWS': 'application/x-shockwave-flash',
        }
        
        # 检查匹配的文件签名
        for signature, mime_type in file_signatures.items():
            if header.startswith(signature):
                return mime_type
                
        # 对于某些特定格式需要更复杂的检查
        if header.startswith(b'RIFF') and len(header) >= 12:
            if header[8:12] == b'WEBP':
                return 'image/webp'
            elif header[8:12] == b'AVI ':
                return 'video/x-msvideo'
                
        # 检查是否为MOV文件（更详细的检查）
        if header.startswith(b'\x00\x00\x00') and b'ftypqt' in header:
            return 'video/quicktime'
            
        # 检查更多字节以识别MOV文件
        # MOV文件通常在前几个字节包含特定的box结构
        if len(header) >= 4:
            # 检查是否有moov或mdat等MOV文件特有的box标识
            with open(file_path, 'rb') as f:
                more_data = f.read(256)  # 读取更多数据来检查MOV标识
            if b'moov' in more_data or b'mdat' in more_data:
                # 进一步确认是MOV文件
                if b'free' in more_data or b'wide' in more_data or b'cmov' in more_data:
                    return 'video/quicktime'
                
        # 检查是否为文本文件
        try:
            # 尝试将前1024字节解码为文本
            text_header = header.decode('utf-8')
            if text_header.isprintable() or all(c.isprintable() or c in '\n\r\t' for c in text_header):
                return 'text/plain'
        except UnicodeDecodeError:
            pass
            
        # 默认返回二进制流类型
        return 'application/octet-stream'
        
    except Exception as e:
        print(f"通过文件头获取文件类型出错: {e}")
        return 'application/octet-stream'

def get_file_extension_by_header(file_path):
    """
    通过读取文件前几个字节来判断文件扩展名
    """
    mime_type = get_file_type_by_header(file_path)
    
    # MIME类型到扩展名的映射
    mime_to_extension = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/gif': 'gif',
        'audio/x-wav': 'wav',
        'application/zip': 'zip',
        'application/pdf': 'pdf',
        'application/gzip': 'gz',
        'application/x-bzip2': 'bz2',
        'application/x-7z-compressed': '7z',
        'video/mp4': 'mp4',
        'video/x-matroska': 'mkv',
        'video/x-flv': 'flv',
        'video/mpeg': 'mpeg',
        'video/x-msvideo': 'avi',
        'video/x-ms-wmv': 'wmv',
        'audio/mpeg': 'mp3',
        'application/font-sfnt': 'ttf',
        'application/font-woff': 'woff',
        'application/font-woff2': 'woff2',
        'image/x-icon': 'ico',
        'application/x-shockwave-flash': 'swf',
        'image/webp': 'webp',
        'text/plain': 'txt',
        'video/quicktime': 'mov'
    }
    
    return mime_to_extension.get(mime_type, '')


if __name__ == '__main__':
    #print(get_file_type_by_magic('D:\\test_dest_file\\676369Qt5.9c++开发指南.pdf'))
    #print(get_file_type_by_magic('C:\\Users\\zheny\\Downloads\\aaa.csv'))
    #print(get_file_type_by_magic('C:\\Users\\zheny\\Downloads\\datasets_115472737719332865_v1_aaa_a.jsonl'))
    #print(get_file_type_by_magic('C:\\Users\\zheny\\Downloads\\datasets_115157531155804180_v2_json_part_14a4edfaaacdefcacccd5d1193cdfde1.json'))
    print(get_file_type_by_magic('D:\\test_dest_file2\\jsonl\\1\\part_14a4edfaaacdefcacccd5d1193cdfde1.jsonl'))
