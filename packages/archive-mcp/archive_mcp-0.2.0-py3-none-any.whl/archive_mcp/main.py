#!/usr/bin/env python3
"""
压缩与解压 MCP 服务器

一个功能全面的MCP服务器，用于文件压缩和解压操作。
支持多种格式：ZIP, 7Z, TAR, TAR.GZ，并支持密码保护。
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Any, List, Optional, Union

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent
)
from pydantic import BaseModel, Field

from .utils.compression import CompressionUtils, CompressionError, format_size


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompressRequest(BaseModel):
    """压缩请求"""
    input: Union[str, List[str]] = Field(..., description="File(s) or directory(ies) to compress")
    output: Optional[str] = Field(None, description="Output archive path")
    format: str = Field("zip", description="Archive format (zip/7z/tar/tar.gz)")
    password: Optional[str] = Field(None, description="Password for encryption")
    compression_level: int = Field(5, description="Compression level (0-9)")
    overwrite: bool = Field(False, description="Whether to overwrite existing files")
    header_encryption: Optional[bool] = Field(
        False,
        description="7Z: encrypt file names (may cause system prompts)"
    )


class ExtractRequest(BaseModel):
    """压缩请求"""
    input: Union[str, List[str]] = Field(..., description="Archive file(s) to extract")
    output: Optional[str] = Field(None, description="Output directory path")
    password: Optional[str] = Field(None, description="Password for encrypted ZIP archives (7Z encryption not supported)")
    overwrite: bool = Field(True, description="Whether to overwrite existing files")


class ArchiveInfoRequest(BaseModel):
    """获取压缩包信息的请求"""
    input: str = Field(..., description="Archive file path")
    password: Optional[str] = Field(None, description="Password for encrypted archives")


class ArchiveMCPServer:
    """用于压缩和解压操作的MCP服务器。"""
    
    def __init__(self):
        self.server = Server("archive-mcp")
        self._setup_tools()
    
    def _setup_tools(self):
        """设置MCP工具。"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """返回可用工具列表。"""
            return [
                Tool(
                    name="compress",
                    description="将文件或文件夹压缩为压缩包",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": ["string", "array"],
                                "items": {"type": "string"},
                                "description": "待压缩的文件或文件夹路径"
                            },
                            "output": {
                                "type": "string",
                                "description": "输出压缩包路径（可选，默认自动生成）"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["zip", "7z", "tar", "tar.gz"],
                                "default": "zip",
                                "description": "压缩格式"
                            },
                            "password": {
                                "type": "string",
                                "description": "压缩密码（仅支持 ZIP 和 7Z 格式）"
                            },
                            "header_encryption": {
                                "type": "boolean",
                                "default": False,
                                "description": "7Z是否加密文件名列表（True=完全加密但可能导致macOS反复弹窗，False=仅加密内容）"
                            },
                            "compression_level": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 9,
                                "default": 5,
                                "description": "压缩级别 0-9（TAR 格式不适用）"
                            },
                            "overwrite": {
                                "type": "boolean",
                                "default": False,
                                "description": "是否覆盖已存在的文件"
                            }
                        },
                        "required": ["input"]
                    }
                ),
                Tool(
                    name="extract",
                    description="解压缩文件工具，支持多种压缩格式（ZIP、7Z、TAR、TAR.GZ）。支持批量解压多个压缩包。注意：仅支持未加密的7Z文件。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": ["string", "array"],
                                "items": {"type": "string"},
                                "description": "要解压的压缩文件路径或路径数组"
                            },
                            "output": {
                                "type": "string",
                                "description": "输出目录路径（可选，默认为源文件所在目录）"
                            },
                            "password": {
                                "type": "string",
                                "description": "加密ZIP压缩包的密码（可选，仅支持ZIP格式，不支持加密7Z文件）"
                            },
                            "overwrite": {
                                "type": "boolean",
                                "default": True,
                                "description": "是否自动覆盖已存在的文件（可选，默认为true）"
                            }
                        },
                        "required": ["input"]
                    }
                ),
                Tool(
                    name="list_archive",
                    description="列出压缩包内容而不解压，支持 ZIP、7Z、TAR、TAR.GZ 格式。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "string",
                                "description": "要查看的压缩文件路径"
                            },
                            "password": {
                                "type": "string",
                                "description": "加密压缩包的密码"
                            }
                        },
                        "required": ["input"]
                    }
                ),
                Tool(
                    name="get_archive_info",
                    description="获取压缩包文件的详细信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "string",
                                "description": "压缩包文件路径"
                            },
                            "password": {
                                "type": "string",
                                "description": "加密压缩包的密码"
                            }
                        },
                        "required": ["input"]
                    }
                ),
                Tool(
                    name="echo",
                    description="回显输入的消息（用于测试连接）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "要回显的消息内容"
                            }
                        },
                        "required": ["message"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            """处理工具调用，返回内容块或结构化结果。"""
            try:
                result = None
                if name == "compress":
                    result = await self._handle_compress(arguments)
                elif name == "extract":
                    result = await self._handle_extract(arguments)
                elif name == "list_archive":
                    result = await self._handle_list_archive(arguments)
                elif name == "get_archive_info":
                    result = await self._handle_get_archive_info(arguments)
                elif name == "echo":
                    result = await self._handle_echo(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                # 适配低层 Server.call_tool 的返回约定
                if isinstance(result, dict):
                    return result
                if hasattr(result, "content"):
                    return result.content
                return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error handling {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_compress(self, arguments: dict) -> CallToolResult:
        """处理压缩请求"""
        try:
            request = CompressRequest(**arguments)
            
            # 将输入规范化为列表
            input_paths = [request.input] if isinstance(request.input, str) else request.input
            
            # 验证输入路径
            for path in input_paths:
                if not os.path.exists(path):
                    raise CompressionError(f"Input path not found: {path}")
            
            # 如果未提供输出路径，则自动生成
            if not request.output:
                first_path = Path(input_paths[0])
                if len(input_paths) == 1:
                    if first_path.is_file():
                        base_name = first_path.stem
                    else:
                        base_name = first_path.name
                else:
                    base_name = "archive"
                
                # Get extension for format
                if request.format == "zip":
                    ext = ".zip"
                elif request.format == "7z":
                    ext = ".7z"
                elif request.format == "tar":
                    ext = ".tar"
                elif request.format == "tar.gz":
                    ext = ".tar.gz"
                else:
                    ext = ".zip"
                
                output_path = str(first_path.parent / f"{base_name}{ext}")
            else:
                output_path = request.output
            
            # Check if output file exists
            if os.path.exists(output_path) and not request.overwrite:
                raise CompressionError(f"Output file already exists: {output_path}. Use overwrite=true to replace.")
            
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Get all files
            files = CompressionUtils.get_all_files(input_paths)
            
            # Perform compression based on format
            if request.format == "zip":
                if request.password and (request.format in ["tar", "tar.gz"]):
                    raise CompressionError("TAR formats do not support password protection")
                CompressionUtils.create_zip(
                    files, output_path, 
                    password=request.password,
                    compression_level=request.compression_level
                )
            elif request.format == "7z":
                # 如果使用密码，给出系统兼容性警告
                warning_msg = ""
                if request.password:
                    warning_msg = "\n⚠️  注意：macOS系统可能对加密7Z文件反复弹出密码提示。如遇此问题，建议使用ZIP格式的AES加密。"
                
                CompressionUtils.create_7z(
                    files, output_path,
                    password=request.password,
                    compression_level=request.compression_level,
                    header_encryption=bool(request.header_encryption)
                )
            elif request.format == "tar":
                if request.password:
                    raise CompressionError("TAR format does not support password protection")
                CompressionUtils.create_tar(files, output_path)
            elif request.format == "tar.gz":
                if request.password:
                    raise CompressionError("TAR.GZ format does not support password protection")
                CompressionUtils.create_tar(files, output_path, compression='gz')
            else:
                raise CompressionError(f"Unsupported format: {request.format}")
            
            # Get file size info
            output_size = os.path.getsize(output_path)
            
            # 构建响应消息
            success_msg = (f"✅ 压缩完成!\n"
                         f"📁 输入: {len(input_paths)} 个路径，共 {len(files)} 个文件\n"
                         f"📦 输出: {output_path}\n"
                         f"🗜️ 格式: {request.format.upper()}\n"
                         f"📏 大小: {format_size(output_size)}\n"
                         f"🔒 加密: {'是' if request.password else '否'}")
            
            # 添加7Z密码警告（如果适用）
            if request.format == "7z" and request.password:
                if request.header_encryption:
                    success_msg += "\n🔒 7Z完全加密：文件内容和文件名列表都已加密"
                    success_msg += "\n⚠️  注意：macOS系统可能反复弹出密码提示，这是正常现象"
                else:
                    success_msg += "\n🔒 7Z部分加密：文件内容已加密，文件名列表可见"
                    success_msg += "\n💡 如需完全加密，设置header_encryption=true"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=success_msg
                )]
            )
            
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"❌ 压缩失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_extract(self, arguments: dict) -> CallToolResult:
        """Handle extraction requests."""
        try:
            request = ExtractRequest(**arguments)
            
            # Normalize input to list
            archive_paths = [request.input] if isinstance(request.input, str) else request.input
            
            results = []
            total_extracted = 0
            
            for archive_path in archive_paths:
                # Check if archive exists
                if not os.path.exists(archive_path):
                    results.append({
                        'archive': archive_path,
                        'success': False,
                        'error': f'压缩文件未找到: {archive_path}'
                    })
                    continue
                
                # Determine output path
                if request.output:
                    output_path = request.output
                else:
                    output_path = os.path.dirname(archive_path)
                
                # Ensure output directory exists
                os.makedirs(output_path, exist_ok=True)
                
                # Detect format and extract
                format_type = CompressionUtils.detect_format(archive_path)
                
                try:
                    if format_type == "zip":
                        result = CompressionUtils.extract_zip(archive_path, output_path, request.password)
                    elif format_type == "7z":
                        # 7Z只支持未加密文件解压，不传递password参数
                        result = CompressionUtils.extract_7z(archive_path, output_path)
                    elif format_type == "tar":
                        result = CompressionUtils.extract_tar(archive_path, output_path)
                    elif format_type == "tar.gz":
                        result = CompressionUtils.extract_tar(archive_path, output_path, compression="gz")
                    else:
                        raise CompressionError(f"Unsupported format: {format_type}")
                    
                    result['archive'] = archive_path
                    result['output_path'] = output_path
                    results.append(result)
                    
                    if result['success']:
                        total_extracted += result['count']
                        
                except Exception as e:
                    results.append({
                        'archive': archive_path,
                        'success': False,
                        'error': str(e),
                        'output_path': output_path
                    })
            
            # Generate summary
            successful = [r for r in results if r.get('success', False)]
            failed = [r for r in results if not r.get('success', False)]
            
            summary_text = f"解压缩完成\n"
            summary_text += f"{'=' * 40}\n"
            summary_text += f"处理的压缩文件总数: {len(archive_paths)}\n"
            summary_text += f"成功解压: {len(successful)}\n"
            summary_text += f"解压失败: {len(failed)}\n"
            summary_text += f"解压文件总数: {total_extracted}\n\n"
            
            for result in results:
                archive_name = os.path.basename(result['archive'])
                if result.get('success', False):
                    summary_text += f"✅ {archive_name}\n"
                    summary_text += f"   格式: {result['format']}\n"
                    summary_text += f"   解压到: {result['output_path']}\n"
                    summary_text += f"   文件数: {result['count']}\n\n"
                else:
                    summary_text += f"❌ {archive_name}\n"
                    summary_text += f"   错误: {result['error']}\n\n"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=summary_text
                )]
            )
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"❌ 解压失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_list_archive(self, arguments: dict) -> CallToolResult:
        """Handle list archive contents requests."""
        try:
            archive_path = arguments["input"]
            password = arguments.get("password")
            
            if not os.path.exists(archive_path):
                raise CompressionError(f"Archive file not found: {archive_path}")
            
            result = CompressionUtils.list_archive_contents(archive_path, password)
            
            if result['success']:
                summary_text = f"压缩包内容预览\n"
                summary_text += f"{'=' * 40}\n"
                summary_text += f"文件: {os.path.basename(archive_path)}\n"
                summary_text += f"格式: {result['format']}\n"
                summary_text += f"文件数: {result['file_count']}\n"
                summary_text += f"总大小: {result['total_size']}\n\n"
                summary_text += "文件列表（前100个）:\n"
                
                for file_info in result['files']:
                    # 规范字段名：工具层统一返回 'filename' 与 'size'
                    name = file_info.get('filename') or file_info.get('name') or ''
                    size = file_info.get('size', 0)
                    summary_text += f"  - {name} ({format_size(size)})\n"
            else:
                summary_text = f"❌ 预览失败: {result['error']}"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=summary_text
                )]
            )
            
        except Exception as e:
            logger.error(f"List archive failed: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"❌ 列出内容失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_get_archive_info(self, arguments: dict) -> CallToolResult:
        """Handle archive info requests."""
        try:
            request = ArchiveInfoRequest(**arguments)
            
            # Check if input file exists
            if not os.path.exists(request.input):
                raise CompressionError(f"Archive file not found: {request.input}")
            
            # Detect format
            format_type = CompressionUtils.detect_format(request.input)
            if not format_type:
                raise CompressionError(f"Unsupported or unrecognized archive format: {request.input}")
            
            # Get archive info based on format
            if format_type == "zip":
                info = CompressionUtils.get_zip_info(request.input, password=request.password)
            elif format_type == "7z":
                info = CompressionUtils.get_7z_info(request.input, password=request.password)
            elif format_type in ["tar", "tar.gz"]:
                info = CompressionUtils.get_tar_info(request.input)
            else:
                raise CompressionError(f"Unsupported format: {format_type}")
            
            # Calculate compression ratio
            if info['total_size'] > 0:
                compression_ratio = (1 - info['compressed_size'] / info['total_size']) * 100
            else:
                compression_ratio = 0
            
            # Format file list
            file_details = "\n".join([
                f"  📄 {file['filename']}: {format_size(file['size'])} "
                f"({'🔒' if file['is_encrypted'] else '🔓'})"
                for file in info['files'][:10]  # Limit to first 10 files
            ])
            
            if len(info['files']) > 10:
                file_details += f"\n  ... 还有 {len(info['files']) - 10} 个文件"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"📊 压缩包信息: {os.path.basename(request.input)}\n\n"
                         f"🗜️ 格式: {info['format'].upper()}\n"
                         f"📄 文件总数: {info['total_files']}\n"
                         f"📏 原始大小: {format_size(info['total_size'])}\n"
                         f"📦 压缩大小: {format_size(info['compressed_size'])}\n"
                         f"📉 压缩率: {compression_ratio:.1f}%\n\n"
                         f"📋 文件列表:\n{file_details}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to get archive info: {str(e)}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"❌ 获取压缩包信息失败: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_echo(self, arguments: dict) -> CallToolResult:
        """Handle echo requests for testing."""
        message = arguments.get("message", "")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Echo: {message}"
            )]
        )
    
    async def run(self):
        """Run the MCP server with proper initialization options."""
        async with stdio_server() as (read_stream, write_stream):
            init_options = self.server.create_initialization_options()
            await self.server.run(
                read_stream,
                write_stream,
                init_options,
            )


async def main():

    server = ArchiveMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
