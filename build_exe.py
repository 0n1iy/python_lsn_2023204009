"""一键打包脚本 - PyInstaller"""

import os
import sys
import PyInstaller.__main__


def build():
    """构建单文件EXE"""
    root_dir = os.path.dirname(os.path.abspath(__file__))

    pyinstaller_args = [
        os.path.join(root_dir, "src", "main.py"),
        "--name=PID温度控制仿真系统",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--distpath={os.path.join(root_dir, 'dist')}",
        f"--workpath={os.path.join(root_dir, 'build')}",
        f"--specpath={os.path.join(root_dir)}",
        "--add-data",
        f"assets{os.pathsep}assets",
        "--add-data",
        f"data{os.pathsep}data",
        "--hidden-import=pyqtgraph",
        "--hidden-import=openpyxl",
        "--hidden-import=numpy",
        "--collect-submodules=pyqtgraph",
    ]

    print("=" * 60)
    print("PID温度控制仿真系统 - 打包脚本")
    print("=" * 60)
    print(f"项目目录: {root_dir}")
    print("开始打包...")

    PyInstaller.__main__.run(pyinstaller_args)

    print("\n" + "=" * 60)
    print(f"打包完成！")
    print(f"输出文件: {os.path.join(root_dir, 'dist', 'PID温度控制仿真系统.exe')}")
    print("=" * 60)


if __name__ == "__main__":
    build()
