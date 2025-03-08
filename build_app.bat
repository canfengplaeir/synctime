@echo off
echo ===============================================
echo SyncTime 应用打包脚本
echo ===============================================
echo.

REM 检查是否在Conda环境中
if "%CONDA_PREFIX%" NEQ "" (
    echo 检测到Conda环境: %CONDA_PREFIX%
    goto conda_env
)

REM 检查是否已经在虚拟环境中 (VIRTUAL_ENV 环境变量)
if "%VIRTUAL_ENV%" NEQ "" (
    echo 检测到已在虚拟环境中: %VIRTUAL_ENV%
    goto venv_ready
)

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python。请确保已安装Python并添加到PATH环境变量。
    goto end
)

echo 未检测到虚拟环境，将询问使用何种方式创建环境。
echo.
echo 请选择虚拟环境类型:
echo 1. 标准虚拟环境 (venv)
echo 2. Conda虚拟环境
echo 3. 使用系统Python (不推荐)
set /p env_choice=请选择 (1-3): 

if "%env_choice%"=="1" goto standard_venv
if "%env_choice%"=="2" goto check_conda
if "%env_choice%"=="3" goto using_system_python

echo 无效的选择，使用默认选项(标准虚拟环境)...
goto standard_venv

:check_conda
REM 检查conda是否安装
conda --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Conda。请确保已安装Conda并添加到PATH环境变量。
    echo 将使用标准虚拟环境(venv)代替。
    goto standard_venv
)

echo 创建Conda环境...
conda create -y -n synctime_env python=3.9
if %errorlevel% neq 0 (
    echo 创建Conda环境失败！
    goto end
)

echo 激活Conda环境...
call conda activate synctime_env
if %errorlevel% neq 0 (
    echo 激活Conda环境失败！
    goto end
)

echo Conda环境激活成功！
goto conda_env

:standard_venv
REM 创建标准虚拟环境（如果不存在）
if not exist venv (
    echo 创建标准虚拟环境(venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 创建虚拟环境失败！
        goto end
    )
)

REM 激活虚拟环境
echo 激活标准虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 激活虚拟环境失败！
    goto end
)

echo 标准虚拟环境激活成功！
goto venv_ready

:conda_env
REM 安装依赖 (Conda)
echo 使用Conda安装依赖库...
conda install -y pyinstaller pillow requests
if %errorlevel% neq 0 (
    echo 使用Conda安装部分依赖失败！尝试使用pip安装剩余依赖...
)

pip install ttkbootstrap ntplib
if %errorlevel% neq 0 (
    echo 安装依赖失败！请检查网络连接或手动安装。
    goto deactivate_conda
)

goto start_packaging

:venv_ready
REM 安装依赖 (pip)
echo 使用pip安装依赖库...
pip install pyinstaller pillow ttkbootstrap ntplib requests
if %errorlevel% neq 0 (
    echo 安装依赖失败！请检查网络连接或手动安装。
    goto deactivate_venv
)

goto start_packaging

:using_system_python
REM 警告用户在使用系统Python
echo 警告: 不建议使用系统Python直接打包，可能会导致环境污染。
set /p confirm=是否确认继续? (y/n): 
if /i "%confirm%" NEQ "y" goto end

REM 安装依赖 (系统Python)
echo 使用系统Python安装依赖库...
pip install pyinstaller pillow ttkbootstrap ntplib requests
if %errorlevel% neq 0 (
    echo 安装依赖失败！请检查网络连接或手动安装。
    goto end
)

:start_packaging
echo.
echo 开始打包SyncTime应用...
echo 注意: ntp_servers.json 将不会被打包，会在首次运行时自动生成。
echo.

REM 执行PyInstaller命令
pyinstaller --noconfirm ^
    --windowed ^
    --icon=app.ico ^
    --uac-admin ^
    --add-data="app.ico;." ^
    --exclude-module=numpy ^
    main.py

set PACKAGE_RESULT=%errorlevel%

if %PACKAGE_RESULT% neq 0 (
    echo.
    echo 打包失败！请检查错误信息。
) else (
    echo.
    echo 打包成功！执行文件位于 dist\main 目录。
    
    REM 创建启动器批处理文件
    echo @echo off > dist\main\启动SyncTime.bat
    echo cd /d "%%~dp0" >> dist\main\启动SyncTime.bat
    echo start "" "main.exe" >> dist\main\启动SyncTime.bat
    echo 已创建启动器批处理文件。
)

REM 根据虚拟环境类型选择退出方式
if "%CONDA_PREFIX%" NEQ "" goto deactivate_conda
if "%VIRTUAL_ENV%" NEQ "" goto deactivate_venv
goto end

:deactivate_conda
REM 退出Conda环境
call conda deactivate
goto end

:deactivate_venv
REM 退出标准虚拟环境
call venv\Scripts\deactivate.bat
goto end

:end
echo.
echo 按任意键退出...
pause > nul 