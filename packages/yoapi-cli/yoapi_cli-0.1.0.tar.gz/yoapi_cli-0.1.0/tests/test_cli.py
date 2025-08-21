"""
yoapi-cli 测试模块
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from yoapi_cli.cli import YoAPICLI


class TestYoAPICLI:
    """YoAPICLI 测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.cli = YoAPICLI()
        # 修改项目根目录为临时目录
        self.cli.project_root = self.test_dir
        self.cli.plugins_dir = self.test_dir / "plugins"
        self.cli.venv_dir = self.test_dir / ".venv"
    
    def teardown_method(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_check_uv_available_available(self):
        """测试uv可用时的检测"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            result = self.cli.check_uv_available()
            assert result is True
    
    def test_check_uv_available_unavailable(self):
        """测试uv不可用时的检测"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = self.cli.check_uv_available()
            assert result is False
    
    @patch('builtins.input', return_value='y')
    def test_get_package_manager_pip_fallback(self, mock_input):
        """测试pip回退机制"""
        with patch.object(self.cli, 'check_uv_available', return_value=False):
            name, cmd = self.cli.get_package_manager()
            assert name == "pip"
            assert cmd == "pip"
    
    @patch('builtins.input', return_value='n')
    def test_get_package_manager_exit_on_no_pip(self, mock_input):
        """测试拒绝pip时的退出"""
        with patch.object(self.cli, 'check_uv_available', return_value=False):
            with pytest.raises(SystemExit):
                self.cli.get_package_manager()
    
    @patch.dict('os.environ', {}, clear=True)
    @patch.object(sys, 'base_prefix', 'C:\\Python313')
    @patch.object(sys, 'prefix', 'C:\\Python313')
    def test_ensure_venv_activated_no_venv(self):
        """测试无虚拟环境时的检测"""
        # 临时修改项目根目录为不存在的虚拟环境路径
        original_venv_dir = self.cli.venv_dir
        self.cli.venv_dir = self.test_dir / "nonexistent_venv"
        
        result = self.cli.ensure_venv_activated()
        
        # 恢复原始虚拟环境目录
        self.cli.venv_dir = original_venv_dir
        assert result is False
    
    @patch.dict('os.environ', {}, clear=True)
    @patch.object(sys, 'base_prefix', 'C:\\Python313')
    @patch.object(sys, 'prefix', 'C:\\Python313')
    def test_ensure_venv_activated_venv_exists_not_activated(self):
        """测试虚拟环境存在但未激活时的检测"""
        # 创建虚拟环境目录
        venv_dir = self.test_dir / ".venv"
        venv_dir.mkdir()
        
        # 临时修改虚拟环境目录路径
        original_venv_dir = self.cli.venv_dir
        self.cli.venv_dir = venv_dir
        
        result = self.cli.ensure_venv_activated()
        
        # 恢复原始虚拟环境目录
        self.cli.venv_dir = original_venv_dir
        assert result is False
    
    @patch.dict('os.environ', {'VIRTUAL_ENV': '/some/path'}, clear=True)
    def test_ensure_venv_activated_env_variable(self):
        """测试VIRTUAL_ENV环境变量检测"""
        result = self.cli.ensure_venv_activated()
        assert result is True
    
    @patch('git.Repo.clone_from')
    def test_init_project_success(self, mock_clone):
        """测试项目初始化成功"""
        project_name = "test-project"
        target_dir = self.test_dir / project_name
        
        # 确保目录不存在，让克隆操作可以正常进行
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # 模拟克隆操作创建目录结构
        def mock_clone_side_effect(*args, **kwargs):
            target_dir.mkdir()
            (target_dir / "README.md").touch()
            (target_dir / "requirements.txt").touch()
            (target_dir / "core").mkdir()
            (target_dir / "plugins").mkdir()
            return Mock()
        
        mock_clone.side_effect = mock_clone_side_effect
        
        result = self.cli.init_project(project_name)
        
        assert result == 0
        mock_clone.assert_called_once_with(
            "https://github.com/WaveYo/WaveYo-API.git",
            target_dir,
            branch="main"
        )
    
    def test_init_project_directory_exists(self):
        """测试目录已存在时的初始化"""
        project_name = "existing-project"
        (self.test_dir / project_name).mkdir()
        
        result = self.cli.init_project(project_name)
        assert result == 1
    
    @patch('git.Repo.clone_from')
    def test_init_project_git_error(self, mock_clone):
        """测试Git错误时的初始化"""
        from git.exc import GitCommandError
        mock_clone.side_effect = GitCommandError("clone", "error")
        
        result = self.cli.init_project("test-project")
        assert result == 1
    
    @patch('git.Repo.clone_from')
    def test_init_project_general_error(self, mock_clone):
        """测试一般错误时的初始化"""
        mock_clone.side_effect = Exception("general error")
        
        result = self.cli.init_project("test-project")
        assert result == 1


def test_version_command(capsys):
    """测试版本命令"""
    from yoapi_cli.cli import version
    result = version()
    
    captured = capsys.readouterr()
    assert result == 0
    assert "yoapi-cli v0.1.0" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
