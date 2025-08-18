"""
开发者工具 MCP 服务器

提供代码格式化、文件操作和项目分析等开发者常用功能
运行命令: python main.py
"""

import os
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器
mcp = FastMCP("开发者工具助手")


@mcp.tool()
def format_json(json_string: str) -> str:
    """格式化JSON字符串，使其更易读"""
    try:
        parsed = json.loads(json_string)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        return f"JSON格式错误: {str(e)}"


@mcp.tool()
def count_lines(file_path: str) -> dict:
    """统计文件行数、字符数等信息"""
    try:
        # 处理相对路径和绝对路径
        path = Path(file_path)
        if not path.is_absolute():
            # 如果是相对路径，基于当前工作目录
            path = Path.cwd() / path
        
        if not path.exists():
            # 提供更详细的错误信息和建议
            current_dir = Path.cwd()
            available_files = [f.name for f in current_dir.iterdir() if f.is_file()]
            return {
                "error": f"文件不存在: {file_path}",
                "当前目录": str(current_dir),
                "可用文件": available_files[:10],  # 显示前10个文件
                "建议": "请使用完整路径或确认文件名正确"
            }
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        return {
            "文件路径": str(path),
            "文件名": path.name,
            "总行数": len(lines),
            "非空行数": len([line for line in lines if line.strip()]),
            "字符数": len(content),
            "文件大小": f"{path.stat().st_size} bytes"
        }
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}


@mcp.tool()
def list_files(directory: str = ".", extension: str = "") -> list:
    """列出目录下的文件，可按扩展名过滤"""
    try:
        path = Path(directory)
        if not path.is_absolute():
            path = Path.cwd() / path
            
        if not path.exists():
            return [{
                "error": f"目录不存在: {directory}",
                "当前目录": str(Path.cwd())
            }]
        
        files = []
        for file in path.iterdir():
            if file.is_file():
                if not extension or file.suffix == extension:
                    files.append({
                        "名称": file.name,
                        "路径": str(file),
                        "大小": f"{file.stat().st_size} bytes",
                        "类型": file.suffix or "无扩展名"
                    })
        
        return files[:20]  # 限制返回前20个文件
    except Exception as e:
        return [{"error": f"读取目录失败: {str(e)}"}]


@mcp.resource("project://info")
def get_project_info() -> str:
    """获取当前项目基本信息"""
    cwd = Path.cwd()
    info = {
        "项目路径": str(cwd),
        "项目名称": cwd.name,
        "Python文件数": len(list(cwd.glob('**/*.py'))),
        "配置文件": [f.name for f in cwd.iterdir() if f.name in ['pyproject.toml', 'requirements.txt', 'setup.py']]
    }
    return json.dumps(info, indent=2, ensure_ascii=False)


@mcp.prompt()
def code_review_prompt(file_path: str) -> str:
    """生成代码审查提示词"""
    return f"请审查以下文件的代码质量、安全性和最佳实践: {file_path}。重点关注代码结构、错误处理、性能优化和可维护性。"


def main() -> None:
    mcp.run(transport="stdio")
