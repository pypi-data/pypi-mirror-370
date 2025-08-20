# hook-dmPython.py
import os

import dmPython

# 找到 `dmPython` 的 `dpi` 目录
dpi_path = os.path.join(os.path.dirname(dmPython.__file__), 'dpi')

# 将 `dpi` 目录中的所有 DLL 文件添加到 binaries
binaries = [(os.path.join(dpi_path, dll), '.') for dll in os.listdir(dpi_path) if dll.endswith('.dll')]
