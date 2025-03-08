"""
SyncTime 打包脚本
这个脚本使用PyInstaller将SyncTime应用程序打包为可执行文件。
基于py-to-exe.json的配置生成。
支持标准虚拟环境(venv)和Conda虚拟环境，ntp_servers.json将在运行时生成，不打包进可执行文件。
"""

import os
import sys
import subprocess
import json
import platform
import venv
import shutil

def get_script_dir():
    """获取当前脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))

def load_config():
    """加载打包配置"""
    config_path = os.path.join(get_script_dir(), "py-to-exe.json")
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 配置文件 {config_path} 不存在")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: 配置文件 {config_path} 格式无效")
        sys.exit(1)

def is_conda_env():
    """检查是否在Conda环境中"""
    return 'CONDA_PREFIX' in os.environ

def is_in_venv():
    """检查是否已经在虚拟环境中"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def create_standard_venv():
    """创建标准虚拟环境（如果不存在）"""
    venv_dir = os.path.join(get_script_dir(), "venv")
    
    if not os.path.exists(venv_dir):
        print("创建标准虚拟环境(venv)...")
        venv.create(venv_dir, with_pip=True)
        return True
    return False

def get_python_path():
    """获取当前环境的Python路径"""
    if is_conda_env():
        # Conda环境
        if os.name == 'nt':  # Windows
            return os.path.join(os.environ['CONDA_PREFIX'], "python.exe")
        else:  # Linux/Mac
            return os.path.join(os.environ['CONDA_PREFIX'], "bin", "python")
    elif is_in_venv():
        # 已经在标准虚拟环境中
        if os.name == 'nt':  # Windows
            return sys.executable
        else:  # Linux/Mac
            return sys.executable
    else:
        # 使用在当前目录创建的标准虚拟环境
        venv_dir = os.path.join(get_script_dir(), "venv")
        if os.name == 'nt':  # Windows
            return os.path.join(venv_dir, "Scripts", "python.exe")
        else:  # Linux/Mac
            return os.path.join(venv_dir, "bin", "python")

def get_pip_command(python_path):
    """获取pip安装命令"""
    if is_conda_env():
        return ["conda", "install", "-y"]
    else:
        return [python_path, "-m", "pip", "install"]

def install_requirements(python_path):
    """安装依赖"""
    requirements = ["pyinstaller", "pillow", "ttkbootstrap", "ntplib", "requests"]
    
    if is_conda_env():
        print("检测到Conda环境，使用conda安装依赖...")
        # 对于conda环境，一次性安装多个包
        cmd = get_pip_command(python_path) + requirements
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode != 0:
            print(f"警告: 安装依赖失败: {process.stderr}")
            print("尝试使用pip安装...")
            for req in requirements:
                cmd = [python_path, "-m", "pip", "install", req]
                process = subprocess.run(cmd, capture_output=True, text=True)
                if process.returncode != 0:
                    print(f"警告: 安装 {req} 失败: {process.stderr}")
                else:
                    print(f"  成功安装 {req}")
        else:
            print("  成功安装依赖库")
    else:
        print("使用pip安装依赖...")
        for req in requirements:
            print(f"  安装 {req}...")
            cmd = get_pip_command(python_path) + [req]
            process = subprocess.run(cmd, capture_output=True, text=True)
            if process.returncode != 0:
                print(f"警告: 安装 {req} 失败: {process.stderr}")
            else:
                print(f"  成功安装 {req}")

def build_command(config, python_path):
    """根据配置构建PyInstaller命令"""
    # 获取主Python文件
    main_file = os.path.join(get_script_dir(), "main.py")
    
    # 构建命令
    if is_conda_env() or is_in_venv():
        # 如果在conda环境或已存在虚拟环境中，直接使用pyinstaller命令
        pyinstaller_cmd = "pyinstaller"
    else:
        # 否则使用标准虚拟环境中的pyinstaller
        if os.name == 'nt':  # Windows
            pyinstaller_cmd = os.path.join(os.path.dirname(python_path), "pyinstaller.exe")
        else:  # Linux/Mac
            pyinstaller_cmd = os.path.join(os.path.dirname(python_path), "pyinstaller")
    
    cmd = [pyinstaller_cmd]
    
    # 添加标准选项
    cmd.append("--noconfirm")  # 不询问确认
    cmd.append("--windowed")  # 窗口模式
    
    # 添加图标
    icon_path = os.path.join(get_script_dir(), "app.ico")
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
        # 添加图标文件数据
        cmd.append(f"--add-data={icon_path}{os.pathsep}.")
    
    # 添加管理员权限
    cmd.append("--uac-admin")
    
    # 排除不需要的模块
    cmd.append("--exclude-module=numpy")
    
    # 添加主文件
    cmd.append(main_file)
    
    return cmd

def run_command(cmd):
    """运行命令"""
    print("执行命令:", " ".join(cmd))
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # 实时显示输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return process.poll()
    except FileNotFoundError:
        print("错误: 未找到PyInstaller。请确保已安装 PyInstaller")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1

def main():
    """主函数"""
    print("=" * 60)
    print("SyncTime 应用打包工具")
    print("=" * 60)
    
    # 检查是否在Conda环境
    if is_conda_env():
        print(f"检测到Conda环境: {os.environ['CONDA_PREFIX']}")
    elif is_in_venv():
        print(f"检测到已在虚拟环境中: {sys.prefix}")
    else:
        print(f"系统Python版本: {platform.python_version()}")
        # 创建标准虚拟环境
        is_new_venv = create_standard_venv()
    
    # 获取环境中的Python路径
    python_path = get_python_path()
    print(f"使用的Python路径: {python_path}")
    
    # 安装依赖（如果是新创建的环境或用户选择重新安装）
    if 'is_new_venv' in locals() and is_new_venv or input("是否安装依赖库? (y/n): ").lower() == 'y':
        install_requirements(python_path)
    
    # 加载配置
    config = load_config()
    print("已加载配置文件")
    
    # 构建命令
    cmd = build_command(config, python_path)
    
    # 提示用户
    print("\n即将执行以下命令打包应用:")
    print(" ".join(cmd))
    print("\n这可能需要几分钟时间，请耐心等待...")
    print("注意: ntp_servers.json 将不会被打包，会在首次运行时自动生成\n")
    
    # 询问是否继续
    if input("是否继续? (y/n): ").lower() != 'y':
        print("已取消打包操作")
        return
    
    # 运行命令
    print("\n开始打包...")
    result = run_command(cmd)
    
    # 显示结果
    if result == 0:
        dist_dir = os.path.join(get_script_dir(), "dist", "main")
        print(f"\n打包成功! 可执行文件位于目录: {dist_dir}")
        
        # 创建启动器批处理文件
        launcher_path = os.path.join(dist_dir, "启动SyncTime.bat")
        with open(launcher_path, 'w') as f:
            f.write('@echo off\n')
            f.write('cd /d "%~dp0"\n')
            f.write('start "" "main.exe"\n')
        
        print(f"已创建启动器: {launcher_path}")
    else:
        print("\n打包失败! 请查看上方错误信息")

if __name__ == "__main__":
    main() 