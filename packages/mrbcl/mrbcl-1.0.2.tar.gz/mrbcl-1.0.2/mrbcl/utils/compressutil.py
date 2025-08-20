import os
import zipfile
import tarfile
import gzip
import bz2
import shutil
from typing import Union, List, Literal

def zip_files(source_paths: Union[str, List[str]], output_path: str, relative_to: str = None, base_dir: str = None) -> None:
    """压缩文件/文件夹到zip
    
    Args:
        source_paths: 要压缩的源文件/文件夹路径，可以是单个字符串或字符串列表
        output_path: 输出的zip文件路径
        relative_to: 计算相对路径时的基准目录，默认为None表示使用source_path的父目录
        base_dir: 压缩包内的基础目录名，默认为None表示不添加基础目录
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if isinstance(source_paths, str):
            source_paths = [source_paths]
            
        for source_path in source_paths:
            if os.path.isfile(source_path):
                # 如果指定了relative_to，计算相对于relative_to的路径
                if relative_to is not None:
                    arcname = os.path.relpath(source_path, relative_to)
                else:
                    arcname = os.path.basename(source_path)
                # 如果指定了base_dir，将其添加到路径前面
                if base_dir is not None:
                    arcname = os.path.join(base_dir, arcname)
                zf.write(source_path, arcname)
            elif os.path.isdir(source_path):
                for root, _, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 如果指定了relative_to，计算相对于relative_to的路径
                        if relative_to is not None:
                            arcname = os.path.relpath(file_path, relative_to)
                        else:
                            arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                        # 如果指定了base_dir，将其添加到路径前面
                        if base_dir is not None:
                            arcname = os.path.join(base_dir, arcname)
                        zf.write(file_path, arcname)


def unzip_file(zip_path: str, extract_path: str) -> None:
    """解压zip文件到指定目录
    
    Args:
        zip_path: 要解压的zip文件路径
        extract_path: 解压目标目录路径
    """
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_path)


def rar_files(source_paths: Union[str, List[str]], output_path: str, relative_to: str = None) -> None:
    """压缩文件/文件夹到rar

    Args:
        source_paths: 要压缩的源文件/文件夹路径，可以是单个字符串或字符串列表
        output_path: 输出的rar文件路径
        relative_to: 计算相对路径时的基准目录，默认为None表示使用output_path文件所在目录
    """
    from mrbcl.command import run_command_silently
    # 检测环境变量中是否有rar命令
    if not shutil.which("rar"):
        raise Exception("rar command not found. Please install rar first.")
    # 如果输出路径存在，则先删除它
    if os.path.exists(output_path):
        os.remove(output_path)
    if isinstance(source_paths, str):
        source_paths = [source_paths]
    # 如果未指定relative_to，则使用output_path文件所在目录
    if relative_to is None:
        relative_to = os.path.dirname(output_path)
    # 计算相对于relative_to的路径
    rel_file_path = os.path.relpath(output_path, relative_to)
    command = ["rar", "a", "-r", "-o+", rel_file_path]
    filelist_path = os.path.join(os.path.dirname(output_path), "filelist.txt")
    # 使用默认编码，如果指定utf-8会出现中文路径无法压缩的问题
    with open(filelist_path, "w") as f:
        for source_path in source_paths:
            if os.path.isfile(source_path):
                # 计算文件的相对路径
                arcname = os.path.relpath(source_path, relative_to)
                # command.append(arcname)
                f.write(arcname + "\n")
            elif os.path.isdir(source_path):
                # 计算文件夹的相对路径
                arcname = os.path.relpath(source_path, relative_to)
                # command.append(arcname)
                f.write(arcname + "\n")
    # 添加文件列表到命令,处理扩展名太长错误
    command.append(f"@{filelist_path}")
    # 设置创建进程的标志以隐藏窗口
    import subprocess
    creationflags = subprocess.CREATE_NO_WINDOW
    # 执行rar命令
    run_command_silently(command, relative_to, creationflags=creationflags)
    # 删除临时文件列表
    if os.path.exists(filelist_path):
        os.remove(filelist_path)


def unrar_file(rar_path: str, extract_path: str) -> None:
    """解压rar文件到指定目录

    Args:
        rar_path: 要解压的rar文件路径
        extract_path: 解压目标目录路径
    """
    from mrbcl.command import run_command_silently
    import subprocess
    # 设置创建进程的标志以隐藏窗口
    creationflags = subprocess.CREATE_NO_WINDOW
    # 执行rar命令进行解压
    run_command_silently(["rar", "x", rar_path, extract_path], creationflags=creationflags)


def tar_files(source_paths: Union[str, List[str]], output_path: str, relative_to: str = None, base_dir: str = None, compression: Literal[None, 'gz', 'bz2'] = None) -> None:
    """压缩文件/文件夹到tar（可选gz或bz2压缩）
    
    Args:
        source_paths: 要压缩的源文件/文件夹路径，可以是单个字符串或字符串列表
        output_path: 输出的tar文件路径
        relative_to: 计算相对路径时的基准目录，默认为None表示使用source_path的父目录
        base_dir: 压缩包内的基础目录名，默认为None表示不添加基础目录
        compression: 压缩方式，可选值为"gz"(gzip压缩)或"bz2"(bzip2压缩)，默认为None表示不压缩
    """
    # 如果未指定压缩方式，则默认为tar格式
    mode = f"w:{compression}" if compression else "w"
    with tarfile.open(output_path, mode) as tf:
        if isinstance(source_paths, str):
            source_paths = [source_paths]
            
        for source_path in source_paths:
            if os.path.isfile(source_path):
                # 计算文件的相对路径
                if relative_to is not None:
                    arcname = os.path.relpath(source_path, relative_to)
                else:
                    arcname = os.path.basename(source_path)
                # 如果指定了base_dir，将其添加到路径前面
                if base_dir is not None:
                    arcname = os.path.join(base_dir, arcname)
                tf.add(source_path, arcname=arcname)
            elif os.path.isdir(source_path):
                # 遍历目录下的所有文件
                for root, _, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 计算相对路径
                        if relative_to is not None:
                            arcname = os.path.relpath(file_path, relative_to)
                        else:
                            arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                        # 如果指定了base_dir，将其添加到路径前面
                        if base_dir is not None:
                            arcname = os.path.join(base_dir, arcname)
                        tf.add(file_path, arcname=arcname)


def untar_file(tar_path: str, extract_path: str) -> None:
    """解压tar文件（包括tar.gz和tar.bz2）到指定目录
    
    Args:
        tar_path: 要解压的tar文件路径（支持.tar、.tar.gz、.tar.bz2格式）
        extract_path: 解压目标目录路径
    """
    with tarfile.open(tar_path, 'r:*') as tf:
        tf.extractall(path=extract_path)


def single_file_compress(file_path: str, compression_type: Literal['gz', 'bz2'] = 'gz', output_path: str = None) -> None:
    """将单个文件压缩为指定格式（gz或bz2）
    
    Args:
        file_path: 要压缩的源文件路径
        compression_type: 压缩类型，'gz'表示gzip压缩（默认），'bz2'表示bzip2压缩
        output_path: 输出的压缩文件路径，默认为源文件路径加上对应的后缀（.gz或.bz2）
    """
    if output_path is None:
        output_path = file_path + '.' + compression_type
    
    compressor = gzip if compression_type == 'gz' else bz2
    with open(file_path, 'rb') as f_in:
        with compressor.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def single_file_decompress(compressed_path: str, compression_type: Literal['gz', 'bz2'] = 'gz', output_path: str = None) -> None:
    """解压指定格式（gz或bz2）的压缩文件
    
    Args:
        compressed_path: 要解压的压缩文件路径
        compression_type: 压缩类型，'gz'表示gzip压缩文件（默认），'bz2'表示bzip2压缩文件
        output_path: 解压后的文件路径，默认为去掉对应后缀的原文件名
    """
    if output_path is None:
        output_path = compressed_path.rsplit('.' + compression_type, 1)[0]
    
    decompressor = gzip if compression_type == 'gz' else bz2
    with decompressor.open(compressed_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def compress_files(source_paths: Union[str, List[str]], output_path: str, archive_type: Literal['zip', 'rar', 'tar', 'tgz', 'tar.gz', 'tbz', 'tar.bz2'] = 'zip', relative_to: str = None, base_dir: str = None) -> None:
    """通用压缩方法，支持多种压缩格式
    
    Args:
        source_paths: 要压缩的源文件/文件夹路径，可以是单个字符串或字符串列表
        output_path: 输出的压缩文件路径
        archive_type: 压缩格式，可选值为：
            - 'zip': ZIP格式（默认）
            - 'rar': RAR格式
            - 'tar': TAR格式（不压缩）
            - 'tgz/tar.gz': TAR.GZ格式（使用gzip压缩）
            - 'tbz/tar.bz2': TAR.BZ2格式（使用bzip2压缩）
        relative_to: 计算相对路径时的基准目录，默认为None表示使用source_path的父目录
        base_dir: 压缩包内的基础目录名，默认为None表示不添加基础目录
    """
    if archive_type == 'zip':
        zip_files(source_paths, output_path, relative_to, base_dir)
    elif archive_type == 'rar':
        rar_files(source_paths, output_path, relative_to)
    else:
        compression = None
        if archive_type == 'tgz' or archive_type == 'tar.gz':
            compression = 'gz'
        elif archive_type == 'tbz' or archive_type == 'tar.bz2':
            compression = 'bz2'
        tar_files(source_paths, output_path, relative_to, base_dir, compression)


def decompress_files(archive_path: str, extract_path: str, archive_type: Literal['zip', 'rar', 'tar', 'tgz', 'tar.gz', 'tbz', 'tar.bz2'] ='zip') -> None:
    """通用解压方法，支持多种压缩格式
    
    Args:
        archive_path: 要解压的压缩文件路径
        extract_path: 解压目标目录路径
        archive_type: 压缩格式，可选值为：
            - 'zip': ZIP格式（默认）
            - 'rar': RAR格式
            - 'tar': TAR格式（不压缩）
            - 'tgz/tar.gz': TAR.GZ格式（使用gzip压缩）
            - 'tbz/tar.bz2': TAR.BZ2格式（使用bzip2压缩）
    """
    if archive_type == 'zip':
        unzip_file(archive_path, extract_path)
    elif archive_type == 'rar':
        unrar_file(archive_path, extract_path)
    else:
        untar_file(archive_path, extract_path)

