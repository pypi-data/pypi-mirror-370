"""
插件管理命令模块
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import git
import requests

from yoapi_cli.cli import YoAPICLI

console = Console()
app = typer.Typer(help="插件管理命令")

class PluginManager:
    """插件管理器"""
    
    def __init__(self, cli: YoAPICLI):
        self.cli = cli
        self.plugins_dir = cli.plugins_dir
    
    def validate_plugin_name(self, name: str) -> bool:
        """验证插件名称是否符合 yoapi-plugin-xxx 规范"""
        return name.startswith("yoapi-plugin-")
    
    def normalize_plugin_name(self, repo_name: str) -> str:
        """规范化插件名称"""
        if repo_name.startswith("yoapi-plugin-"):
            return repo_name
        return f"yoapi-plugin-{repo_name}"
    
    def get_github_repo_url(self, repo_name: str) -> str:
        """获取GitHub仓库URL"""
        normalized_name = self.normalize_plugin_name(repo_name)
        return f"https://github.com/{normalized_name}.git"
    
    def check_plugin_exists(self, plugin_name: str) -> bool:
        """检查插件是否已存在"""
        plugin_dir = self.plugins_dir / plugin_name
        return plugin_dir.exists()
    
    def download_plugin(self, repo_name: str, force: bool = False) -> int:
        """
        从GitHub下载插件
        
        Args:
            repo_name: GitHub仓库名称（如 WaveYo/yoapi-plugin-mysql-database）
            force: 是否强制覆盖已存在的插件
            
        Returns:
            int: 退出代码
        """
        try:
            # 解析仓库名称
            if "/" not in repo_name:
                console.print("❌ 仓库名称格式错误，应为: 用户名/仓库名", style="red")
                return 1
            
            user_name, repo_base_name = repo_name.split("/", 1)
            plugin_name = self.normalize_plugin_name(repo_base_name)
            
            # 验证插件名称
            if not self.validate_plugin_name(plugin_name):
                console.print(f"❌ 插件名称 '{plugin_name}' 不符合 yoapi-plugin-xxx 规范", style="red")
                return 1
            
            # 检查插件是否已存在
            if self.check_plugin_exists(plugin_name) and not force:
                console.print(f"❌ 插件 '{plugin_name}' 已存在，使用 --force 覆盖", style="red")
                return 1
            
            # 创建插件目录
            self.plugins_dir.mkdir(exist_ok=True)
            plugin_dir = self.plugins_dir / plugin_name
            
            # 如果强制覆盖，先删除现有目录
            if plugin_dir.exists() and force:
                shutil.rmtree(plugin_dir)
            
            # 构建GitHub URL
            repo_url = f"https://github.com/{user_name}/{plugin_name}.git"
            
            console.print(f"🔌 正在下载插件: {plugin_name}", style="blue")
            console.print(f"📦 仓库地址: {repo_url}", style="blue")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="正在克隆插件仓库...", total=None)
                
                # 克隆插件仓库
                git.Repo.clone_from(repo_url, plugin_dir)
            
            console.print(f"✅ 插件下载成功: {plugin_name}", style="green")
            
            # 检查插件结构
            self._validate_plugin_structure(plugin_dir)
            
            # 安装插件依赖
            self._install_plugin_dependencies(plugin_dir, plugin_name)
            
            return 0
            
        except git.exc.GitCommandError as e:
            console.print(f"❌ 下载插件失败: {e}", style="red")
            # 清理创建的文件
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            return 1
        except Exception as e:
            console.print(f"❌ 下载插件时出错: {e}", style="red")
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            return 1
    
    def _validate_plugin_structure(self, plugin_dir: Path):
        """验证插件结构"""
        required_files = ["__init__.py", "requirements.txt"]
        
        for file in required_files:
            if not (plugin_dir / file).exists():
                console.print(f"⚠️  警告: 插件缺少必要文件 {file}", style="yellow")
    
    def _install_plugin_dependencies(self, plugin_dir: Path, plugin_name: str):
        """安装插件依赖"""
        requirements_file = plugin_dir / "requirements.txt"
        
        if not requirements_file.exists():
            console.print(f"ℹ️  插件 {plugin_name} 没有依赖需要安装", style="blue")
            return
        
        console.print(f"📦 正在安装插件 {plugin_name} 的依赖...", style="blue")
        
        pkg_manager, pkg_cmd = self.cli.get_package_manager()
        
        try:
            if pkg_manager == "uv":
                cmd = ["uv", "pip", "install", "-r", str(requirements_file)]
            else:
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print(f"✅ 插件 {plugin_name} 依赖安装成功", style="green")
            else:
                console.print(f"❌ 插件 {plugin_name} 依赖安装失败", style="red")
                console.print(result.stderr, style="red")
                
        except Exception as e:
            console.print(f"❌ 安装依赖时出错: {e}", style="red")
    
    def list_plugins(self) -> int:
        """列出所有已安装的插件"""
        if not self.plugins_dir.exists():
            console.print("ℹ️  没有安装任何插件", style="blue")
            return 0
        
        plugins = []
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and self.validate_plugin_name(item.name):
                plugins.append({
                    'name': item.name,
                    'path': item,
                    'has_init': (item / "__init__.py").exists(),
                    'has_requirements': (item / "requirements.txt").exists(),
                })
        
        if not plugins:
            console.print("ℹ️  没有安装任何插件", style="blue")
            return 0
        
        table = Table(title="📦 已安装插件列表")
        table.add_column("插件名称", style="cyan")
        table.add_column("状态", style="green")
        table.add_column("依赖文件", style="yellow")
        table.add_column("主文件", style="yellow")
        
        for plugin in plugins:
            status = "✅ 正常" if plugin['has_init'] else "❌ 无效"
            deps = "✅ 有" if plugin['has_requirements'] else "❌ 无"
            main_file = "✅ 有" if plugin['has_init'] else "❌ 无"
            
            table.add_row(plugin['name'], status, deps, main_file)
        
        console.print(table)
        return 0
    
    def remove_plugin(self, plugin_name: str) -> int:
        """移除插件"""
        normalized_name = self.normalize_plugin_name(plugin_name)
        
        if not self.validate_plugin_name(normalized_name):
            console.print(f"❌ 插件名称 '{plugin_name}' 不符合 yoapi-plugin-xxx 规范", style="red")
            return 1
        
        plugin_dir = self.plugins_dir / normalized_name
        
        if not plugin_dir.exists():
            console.print(f"❌ 插件 '{normalized_name}' 不存在", style="red")
            return 1
        
        try:
            shutil.rmtree(plugin_dir)
            console.print(f"✅ 插件 '{normalized_name}' 已成功移除", style="green")
            return 0
        except Exception as e:
            console.print(f"❌ 移除插件失败: {e}", style="red")
            return 1
    
    def create_new_plugin(self, plugin_name: str) -> int:
        """创建新插件模板"""
        normalized_name = self.normalize_plugin_name(plugin_name)
        
        if not self.validate_plugin_name(normalized_name):
            console.print(f"❌ 插件名称 '{plugin_name}' 不符合 yoapi-plugin-xxx 规范", style="red")
            return 1
        
        if self.check_plugin_exists(normalized_name):
            console.print(f"❌ 插件 '{normalized_name}' 已存在", style="red")
            return 1
        
        plugin_dir = self.plugins_dir / normalized_name
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建插件模板文件
        self._create_plugin_template(plugin_dir, normalized_name)
        
        console.print(f"✅ 插件模板 '{normalized_name}' 创建成功", style="green")
        console.print(f"📁 位置: {plugin_dir}", style="blue")
        return 0
    
    def _create_plugin_template(self, plugin_dir: Path, plugin_name: str):
        """创建插件模板文件"""
        # __init__.py
        init_content = f'''"""
{plugin_name} - WaveYo-API 插件
"""

import os
from dotenv import load_dotenv
from fastapi import APIRouter
from plugins.log import get_log_service

# 加载环境变量
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

router = APIRouter(prefix="/{plugin_name.replace('yoapi-plugin-', '')}", tags=["{plugin_name.replace('yoapi-plugin-', '')}"])

@router.get("/")
async def root():
    """插件根端点"""
    logger = get_log_service().get_logger(__name__)
    logger.info("插件端点被调用")
    return {{"message": "Hello from {plugin_name}", "status": "ok"}}

def register(app, **dependencies):
    """插件注册函数"""
    logger = get_log_service().get_logger(__name__)
    app.include_router(router)
    logger.info("插件 {plugin_name} 已成功注册")
'''
        
        with open(plugin_dir / "__init__.py", "w", encoding="utf-8") as f:
            f.write(init_content)
        
        # requirements.txt
        with open(plugin_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("# 插件依赖声明\n# fastapi>=0.104.0\n# python-dotenv>=1.0.0\n")
        
        # README.md
        readme_content = f'''# {plugin_name}

WaveYo-API 插件

## 功能描述

[在这里描述插件的功能]

## 安装

插件会自动被WaveYo-API核心检测和加载

## 配置

在插件目录下创建 `.env` 文件配置环境变量：

```env
# 插件配置示例
PLUGIN_CONFIG_KEY=value
```

## API端点

- `GET /{plugin_name.replace('yoapi-plugin-', '')}/` - 插件根端点

## 开发说明

[在这里添加开发说明]
'''
        
        with open(plugin_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # .env.example
        env_example = '''# 插件环境变量示例
# PLUGIN_CONFIG_KEY=your_value_here
'''
        
        with open(plugin_dir / ".env.example", "w", encoding="utf-8") as f:
            f.write(env_example)

# 创建插件管理器实例
plugin_manager = PluginManager(YoAPICLI())

@app.command()
def download(
    repo_name: str = typer.Argument(..., help="GitHub仓库名称（如 WaveYo/yoapi-plugin-mysql-database）"),
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖已存在的插件")
):
    """从GitHub下载插件"""
    return plugin_manager.download_plugin(repo_name, force)

@app.command()
def list():
    """列出所有已安装的插件"""
    return plugin_manager.list_plugins()

@app.command()
def remove(
    plugin_name: str = typer.Argument(..., help="插件名称")
):
    """移除插件"""
    return plugin_manager.remove_plugin(plugin_name)

@app.command()
def new(
    plugin_name: str = typer.Argument(..., help="插件名称（会自动添加yoapi-plugin-前缀）")
):
    """创建新插件模板"""
    return plugin_manager.create_new_plugin(plugin_name)
