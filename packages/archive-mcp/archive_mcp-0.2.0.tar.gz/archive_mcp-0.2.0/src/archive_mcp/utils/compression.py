"""
Compression utilities for creating and handling different archive formats.
"""

import os
import tarfile
import zipfile
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import py7zr
from datetime import datetime
import shutil
import logging

# 尝试导入pyzipper用于ZIP密码支持（推荐方案）
try:
    import pyzipper
    PYZIPPER_AVAILABLE = True
except ImportError:
    PYZIPPER_AVAILABLE = False

# 备用方案：pyminizip（有路径问题）
try:
    import pyminizip
    PYMINIZIP_AVAILABLE = True
except ImportError:
    PYMINIZIP_AVAILABLE = False


class CompressionError(Exception):
    """Custom exception for compression operations."""
    pass


class CompressionUtils:
    """Utility class for compression and extraction operations."""
    
    SUPPORTED_FORMATS = {
        'zip': ['.zip'],
        '7z': ['.7z'],
        'tar': ['.tar'],
        'tar.gz': ['.tar.gz', '.tgz']
    }
    
    @staticmethod
    def detect_format(file_path: str) -> Optional[str]:
        """Detect archive format from file extension."""
        file_path = file_path.lower()
        
        for format_name, extensions in CompressionUtils.SUPPORTED_FORMATS.items():
            if any(file_path.endswith(ext) for ext in extensions):
                return format_name
        return None
    
    @staticmethod
    def get_all_files(paths: List[str]) -> List[Dict[str, Union[str, bytes]]]:
        """Get all files from given paths (files and directories)."""
        files = []
        
        for input_path in paths:
            path_obj = Path(input_path)
            
            if not path_obj.exists():
                raise CompressionError(f"Path not found: {input_path}")
            
            if path_obj.is_file():
                # Single file
                with open(path_obj, 'rb') as f:
                    files.append({
                        'name': path_obj.name,
                        'data': f.read(),
                        'path': str(path_obj)
                    })
            elif path_obj.is_dir():
                # Directory
                base_name = path_obj.name
                for file_path in path_obj.rglob('*'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(path_obj.parent)
                        with open(file_path, 'rb') as f:
                            files.append({
                                'name': str(rel_path),
                                'data': f.read(),
                                'path': str(file_path)
                            })
        
        return files
    
    @staticmethod
    def create_zip(files: List[Dict[str, Union[str, bytes]]], 
                   output_path: str,
                   password: Optional[str] = None,
                   compression_level: int = 5) -> None:
        """
        Create ZIP archive with optional password encryption.
        
        使用pyzipper库实现标准ZIP密码加密，文件路径结构完全正常。
        """
        try:
            if password:
                # 优先使用pyzipper（推荐方案）
                if PYZIPPER_AVAILABLE:
                    # 使用pyzipper创建加密ZIP - 完美的解决方案
                    with pyzipper.AESZipFile(output_path, 'w', 
                                            compression=pyzipper.ZIP_DEFLATED,
                                            compresslevel=compression_level) as zipf:
                        # 设置密码和加密方式
                        zipf.setpassword(password.encode())
                        zipf.setencryption(pyzipper.WZ_AES, nbits=256)  # 使用AES-256加密
                        
                        # 写入文件
                        for file_info in files:
                            zipf.writestr(file_info['name'], file_info['data'])
                    
                    return  # 成功使用pyzipper，直接返回
                
                # 备用方案：pyminizip（有路径嵌套问题）
                elif PYMINIZIP_AVAILABLE:
                    import warnings
                    warnings.warn(
                        "使用pyminizip创建加密ZIP，文件路径会有额外层级。"
                        "建议安装pyzipper (pip install pyzipper) 或使用7Z格式。",
                        UserWarning
                    )
                    
                    # 使用pyminizip创建加密ZIP（保留原有实现）
                    temp_files = []
                    try:
                        for i, file_info in enumerate(files):
                            # 创建临时文件
                            temp_path = f"/tmp/zip_temp_{os.getpid()}_{i}.tmp"
                            with open(temp_path, 'wb') as f:
                                f.write(file_info['data'])
                            temp_files.append((temp_path, file_info['name']))
                        
                        # 创建加密ZIP
                        if len(temp_files) == 1:
                            pyminizip.compress(
                                temp_files[0][0], 
                                temp_files[0][1], 
                                output_path, 
                                password, 
                                compression_level
                            )
                        else:
                            file_paths = [tf[0] for tf in temp_files]
                            arc_names = [tf[1] for tf in temp_files]
                            pyminizip.compress_multiple(
                                file_paths, 
                                arc_names, 
                                output_path, 
                                password, 
                                compression_level
                            )
                    
                    finally:
                        # 清理临时文件
                        for temp_path, _ in temp_files:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                else:
                    # 没有任何ZIP密码库可用
                    raise CompressionError(
                        "ZIP密码保护需要额外的库支持。\n"
                        "解决方案：\n"
                        "1. 安装pyzipper（推荐）: pip install pyzipper\n"
                        "2. 或安装pyminizip: pip install pyminizip\n"
                        "3. 或使用format='7z'进行密码保护（最简单）"
                    )
            else:
                # 无密码时使用标准zipfile
                with zipfile.ZipFile(output_path, 'w', 
                                   compression=zipfile.ZIP_DEFLATED,
                                   compresslevel=compression_level) as zipf:
                    
                    for file_info in files:
                        zipf.writestr(file_info['name'], file_info['data'])
                    
        except CompressionError:
            raise  # 重新抛出我们自定义的错误
        except Exception as e:
            raise CompressionError(f"ZIP compression failed: {str(e)}")
    
    @staticmethod
    def create_7z(files: List[Dict[str, Union[str, bytes]]], 
                  output_path: str,
                  password: Optional[str] = None,
                  compression_level: int = 5,
                  header_encryption: bool = False) -> None:
        """Create 7Z archive with proper password encryption.

        IMPORTANT: When password is set, files are encrypted even if header_encryption=False.
        However, setting header_encryption=False allows file listing without password,
        which may cause macOS system services to prompt repeatedly.
        
        Args:
            password: Password for file content encryption
            header_encryption: Whether to encrypt the file list (filename headers)
                             - True: Encrypt everything (more secure, may cause macOS prompts)
                             - False: Only encrypt file content, not filenames
        """
        try:
            # 如果有密码但用户明确设置header_encryption=False，给出警告
            if password and not header_encryption:
                import warnings
                warnings.warn(
                    "7Z文件内容已加密，但文件列表未加密。这可能导致macOS系统反复弹窗。"
                    "如需完全加密，设置header_encryption=True。",
                    UserWarning
                )
            
            # 使用用户的header_encryption设置，不强制覆盖
            he = bool(password) and bool(header_encryption)
            
            with py7zr.SevenZipFile(
                output_path,
                'w',
                password=password,
                header_encryption=he,
            ) as archive:
                for file_info in files:
                    # py7zr.writestr accepts data first then arcname
                    archive.writestr(file_info['data'], file_info['name'])
        except Exception as e:
            raise CompressionError(f"7Z compression failed: {str(e)}")
    
    @staticmethod
    def create_tar(files: List[Dict[str, Union[str, bytes]]], 
                   output_path: str,
                   compression: Optional[str] = None) -> None:
        """Create TAR archive."""
        try:
            mode = 'w'
            if compression == 'gz':
                mode = 'w:gz'
            elif compression == 'bz2':
                mode = 'w:bz2'
            elif compression == 'xz':
                mode = 'w:xz'
            
            with tarfile.open(output_path, mode) as tar:
                for file_info in files:
                    import io
                    tarinfo = tarfile.TarInfo(name=file_info['name'])
                    tarinfo.size = len(file_info['data'])
                    tarinfo.mtime = int(datetime.now().timestamp())
                    
                    tar.addfile(tarinfo, io.BytesIO(file_info['data']))
                    
        except Exception as e:
            raise CompressionError(f"TAR compression failed: {str(e)}")
    
    
    
    
    @staticmethod
    def get_zip_info(archive_path: str, 
                    password: Optional[str] = None) -> Dict[str, Any]:
        """Get ZIP archive information, supporting both standard and encrypted ZIPs."""
        try:
            info = {
                'format': 'zip',
                'files': [],
                'total_files': 0,
                'total_size': 0,
                'compressed_size': 0
            }
            
            # 尝试使用pyzipper（支持AES加密）
            if password and PYZIPPER_AVAILABLE:
                try:
                    with pyzipper.AESZipFile(archive_path, 'r') as zipf:
                        zipf.setpassword(password.encode())
                        
                        for file_info in zipf.infolist():
                            if not file_info.is_dir():
                                info['files'].append({
                                    'filename': file_info.filename,
                                    'size': file_info.file_size,
                                    'compressed_size': file_info.compress_size,
                                    'modified_date': datetime(*file_info.date_time),
                                    'is_encrypted': file_info.flag_bits & 0x1 != 0
                                })
                                info['total_size'] += file_info.file_size
                                info['compressed_size'] += file_info.compress_size
                        
                        info['total_files'] = len(info['files'])
                    return info
                except Exception:
                    # 如果pyzipper失败，尝试标准zipfile
                    pass
            
            # 使用标准zipfile
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                if password:
                    zipf.setpassword(password.encode())
                
                for file_info in zipf.infolist():
                    if not file_info.is_dir():
                        info['files'].append({
                            'filename': file_info.filename,
                            'size': file_info.file_size,
                            'compressed_size': file_info.compress_size,
                            'modified_date': datetime(*file_info.date_time),
                            'is_encrypted': file_info.flag_bits & 0x1 != 0
                        })
                        info['total_size'] += file_info.file_size
                        info['compressed_size'] += file_info.compress_size
                
                info['total_files'] = len(info['files'])
            
            return info
            
        except Exception as e:
            raise CompressionError(f"Failed to get ZIP info: {str(e)}")
    
    @staticmethod
    def get_7z_info(archive_path: str, 
                   password: Optional[str] = None) -> Dict[str, Any]:
        """Get 7Z archive information."""
        try:
            info = {
                'format': '7z',
                'files': [],
                'total_files': 0,
                'total_size': 0,
                'compressed_size': 0
            }
            
            with py7zr.SevenZipFile(archive_path, 'r', password=password) as archive:
                for file_info in archive.list():
                    # Check if it's a file (not directory)
                    if not (hasattr(file_info, 'is_dir') and file_info.is_dir):
                        uncompressed_size = getattr(file_info, 'uncompressed', 0) or 0
                        compressed_size = getattr(file_info, 'compressed', 0) or 0
                        
                        info['files'].append({
                            'filename': file_info.filename,
                            'size': uncompressed_size,
                            'compressed_size': compressed_size,
                            'modified_date': getattr(file_info, 'creationtime', datetime.now()),
                            'is_encrypted': getattr(file_info, 'is_encrypted', False)
                        })
                        info['total_size'] += uncompressed_size
                        info['compressed_size'] += compressed_size
                
                info['total_files'] = len(info['files'])
            
            return info
            
        except Exception as e:
            raise CompressionError(f"Failed to get 7Z info: {str(e)}")
    
    @staticmethod
    def get_tar_info(archive_path: str) -> Dict[str, Any]:
        """Get TAR archive information."""
        try:
            info = {
                'format': 'tar',
                'files': [],
                'total_files': 0,
                'total_size': 0,
                'compressed_size': 0
            }
            
            with tarfile.open(archive_path, 'r:*') as tar:
                members = tar.getmembers()
                
                for member in members:
                    if member.isfile():
                        info['files'].append({
                            'filename': member.name,
                            'size': member.size,
                            'compressed_size': member.size,  # TAR doesn't compress
                            'modified_date': datetime.fromtimestamp(member.mtime),
                            'is_encrypted': False
                        })
                        info['total_size'] += member.size
                        info['compressed_size'] += member.size
                
                info['total_files'] = len(info['files'])
            
            # Check if it's compressed TAR
            if archive_path.lower().endswith('.gz') or archive_path.lower().endswith('.tgz'):
                info['format'] = 'tar.gz'
                # For compressed TAR, get actual file size
                file_size = os.path.getsize(archive_path)
                info['compressed_size'] = file_size
            
            return info
            
        except Exception as e:
            raise CompressionError(f"Failed to get TAR info: {str(e)}")


    # ================== EXTRACTION METHODS ==================
    
    @staticmethod
    def is_safe_path(base_path: str, target_path: str) -> bool:
        """Check if the target path is safe (prevents path traversal attacks)."""
        base = os.path.abspath(base_path)
        target = os.path.abspath(os.path.join(base_path, target_path))
        return target.startswith(base)
    
    @staticmethod
    def extract_zip(archive_path: str, output_path: str, password: Optional[str] = None) -> Dict[str, Any]:
        """Extract ZIP archive, supporting AES encryption via pyzipper when available."""
        try:
            extracted_files = []

            # 优先尝试 pyzipper 以兼容 AES 加密
            if password and PYZIPPER_AVAILABLE:
                try:
                    with pyzipper.AESZipFile(archive_path, 'r') as zipf:
                        zipf.setpassword(password.encode('utf-8'))
                        for info in zipf.infolist():
                            if not CompressionUtils.is_safe_path(output_path, info.filename):
                                continue
                            zipf.extract(info, output_path)
                            extracted_files.append(os.path.join(output_path, info.filename))
                    return {
                        'success': True,
                        'format': 'ZIP',
                        'extracted_files': extracted_files,
                        'count': len(extracted_files)
                    }
                except Exception:
                    # 回退到标准库处理
                    extracted_files = []

            with zipfile.ZipFile(archive_path, 'r') as zipf:
                if password:
                    zipf.setpassword(password.encode('utf-8'))
                for file_info in zipf.filelist:
                    if not CompressionUtils.is_safe_path(output_path, file_info.filename):
                        continue
                    zipf.extract(file_info, output_path)
                    extracted_files.append(os.path.join(output_path, file_info.filename))

            return {
                'success': True,
                'format': 'ZIP',
                'extracted_files': extracted_files,
                'count': len(extracted_files)
            }
        except Exception as e:
            raise CompressionError(f"ZIP extraction failed: {str(e)}")
    
    @staticmethod
    def extract_7z(archive_path: str, output_path: str) -> Dict[str, Any]:
        """Extract 7Z archive. Only supports unencrypted 7Z files."""
        try:
            extracted_files = []
            
            # 只支持未加密的7Z文件解压
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(path=output_path)
                for info in archive.list():
                    name = getattr(info, 'filename', None) or getattr(info, 'name', '')
                    if name and not str(name).endswith('/'):
                        full = os.path.join(output_path, name)
                        if os.path.exists(full):
                            extracted_files.append(full)
            
            return {
                'success': True,
                'format': '7Z',
                'extracted_files': extracted_files,
                'count': len(extracted_files)
            }
        except Exception as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise CompressionError("不支持加密的7Z文件解压。请使用未加密的7Z文件。")
            raise CompressionError(f"7Z extraction failed: {str(e)}")
    
    @staticmethod
    def extract_tar(archive_path: str, output_path: str, compression: Optional[str] = None) -> Dict[str, Any]:
        """Extract TAR archive."""
        try:
            extracted_files = []
            mode = 'r'
            if compression == 'gz':
                mode = 'r:gz'
            elif compression == 'bz2':
                mode = 'r:bz2'
            elif compression == 'xz':
                mode = 'r:xz'
            
            with tarfile.open(archive_path, mode) as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        if not CompressionUtils.is_safe_path(output_path, member.name):
                            continue
                        
                        tar.extract(member, output_path)
                        extracted_files.append(os.path.join(output_path, member.name))
            
            return {
                'success': True,
                'format': 'TAR',
                'extracted_files': extracted_files,
                'count': len(extracted_files)
            }
        except Exception as e:
            raise CompressionError(f"TAR extraction failed: {str(e)}")
    
    @staticmethod
    def list_archive_contents(archive_path: str, password: Optional[str] = None) -> Dict[str, Any]:
        """List contents of an archive without extracting."""
        try:
            format_type = CompressionUtils.detect_format(archive_path)
            if not format_type:
                raise CompressionError("Unsupported archive format")
            
            files = []
            total_size = 0
            
            if format_type == 'zip':
                info = CompressionUtils.get_zip_info(archive_path, password)
            elif format_type == '7z':
                info = CompressionUtils.get_7z_info(archive_path, password)
            elif format_type in ['tar', 'tar.gz']:
                info = CompressionUtils.get_tar_info(archive_path)
            else:
                raise CompressionError(f"Unsupported format: {format_type}")
            
            return {
                'success': True,
                'format': format_type.upper(),
                'file_count': info['total_files'],
                'total_size': format_size(info['total_size']),
                'files': info['files'][:100]  # Limit to first 100 files
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


