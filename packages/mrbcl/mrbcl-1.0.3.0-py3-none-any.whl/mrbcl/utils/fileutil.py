from typing import Union, Optional
import PyPDF2
import comtypes.client
import os
import time


def merge_pdf(input_files: list[str], output_file: str) -> None:
    """
    合并pdf
    :param input_files: 待合并文件路径列表（合并顺序依次排列）
    :param output_file: 保存文件路径
    :return:
    """
    merger = PyPDF2.PdfMerger()

    for pdf in input_files:
        with open(pdf, 'rb') as file:
            merger.append(file)

    with open(output_file, 'wb') as output:
        merger.write(output)

def save_file(binary_stream: bytes, output_file: str, mode: str) -> None:
    """
    文件流保存文件
    :param binary_stream: 数据流
    :param output_file: 保存文件路径
    :param mode: 文件操作方式 w|wb|a|ab
    :return:
    """
    with open(output_file, mode) as file:
        file.write(binary_stream)

def word_to_pdf(input_file: str, output_file: str, remove_header: bool = True, remove_footer: bool = True) -> None:
    """
    word文档转pdf
    :param input_file: word文档路径
    :param output_file: pdf保存路径
    :param remove_header: 是否移除word文档中的页眉
    :param remove_footer: 是否移除word文档中的页脚
    :return:
    """
    # 初始化 Word 应用程序
    word = comtypes.client.CreateObject("Word.Application")
    try:
        # 打开 Word 文档
        doc = word.Documents.Open(input_file, NoEncodingDialog=True)
        # 设置页面边距（单位为磅，1 英寸 = 72 磅）
        # doc.PageSetup.LeftMargin = 36
        # doc.PageSetup.RightMargin = 36
        # doc.PageSetup.TopMargin = 36
        # doc.PageSetup.BottomMargin = 36

        if remove_header is True:
            # 清空所有节（Sections）的页眉内容
            for section in doc.Sections:
                section.Headers(1).Range.Text = ""

        if remove_footer is True:
            # 清空所有节（Sections）的页脚内容
            for section in doc.Sections:
                section.Footers(1).Range.Text = ""

        # 将文档保存为 PDF
        doc.SaveAs(output_file, FileFormat=17)  # 17 表示 PDF 格式

        # 关闭文档和 Word 应用程序
        doc.Close()
        # word.Quit()
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(e)
    finally:
        word.Quit()

def copy_files(src_path: str, dst_path: str, include_patterns: Optional[list[str]] = None, exclude_patterns: Optional[list[str]] = None) -> None:
    """
    复制文件或目录
    :param src_path: 源路径（文件或目录）
    :param dst_path: 目标路径
    :param include_patterns: 包含的文件或目录模式列表，支持以下格式：
                          - 指定目录：'docs', 'src/components'
                          - 文件扩展名：'*.txt', '*.py'
                          - 目录下所有文件：'docs/*'
                          - 目录及子目录：'docs/**'
    :param exclude_patterns: 排除的文件或目录模式列表，格式同include_patterns
    :return: None
    """
    import shutil
    import fnmatch
    
    def should_copy(path: str, is_dir: bool = False) -> bool:
        # 如果没有指定包含和排除模式，则复制所有文件
        if not include_patterns and not exclude_patterns:
            return True
            
        # 获取相对路径
        rel_path = os.path.relpath(path, src_path)
        if is_dir:
            rel_path = os.path.join(rel_path, '')
        
        # 检查排除模式
        if exclude_patterns:
            for pattern in exclude_patterns:
                # 确保目录模式以/结尾
                if is_dir and not pattern.endswith('/'):
                    pattern = pattern + '/'
                if fnmatch.fnmatch(rel_path, pattern):
                    return False
        
        # 检查包含模式
        if include_patterns:
            for pattern in include_patterns:
                # 确保目录模式以/结尾
                if is_dir and not pattern.endswith('/'):
                    pattern = pattern + '/'
                if fnmatch.fnmatch(rel_path, pattern):
                    return True
                # 如果是目录，还需要检查是否有子模式匹配
                if is_dir:
                    # 检查是否有模式以此目录开头
                    for p in include_patterns:
                        if p.startswith(rel_path.replace('\\', '/')):
                            return True
            return False
        
        return True
    
    # 确保源路径存在
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"源路径不存在：{src_path}")

    # 如果源路径是文件
    if os.path.isfile(src_path):
        if should_copy(src_path, False):
            # 确保目标目录存在
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"文件复制成功：{src_path} -> {dst_path}")
    
    # 如果源路径是目录
    elif os.path.isdir(src_path):
        # 创建目标根目录
        os.makedirs(dst_path, exist_ok=True)
        
        # 遍历源目录
        for root, dirs, files in os.walk(src_path):
            # 过滤不需要遍历的目录
            dirs[:] = [d for d in dirs if should_copy(os.path.join(root, d), True)]
            
            # 检查当前目录是否应该被复制
            if not should_copy(root, True):
                continue
            
            # 创建当前层级的目标目录
            rel_path = os.path.relpath(root, src_path)
            current_dst = os.path.join(dst_path, rel_path) if rel_path != '.' else dst_path
            
            # 复制文件
            for file in files:
                src_file = os.path.join(root, file)
                if should_copy(src_file, False):
                    dst_file = os.path.join(current_dst, file)
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    # 复制文件
                    shutil.copy2(src_file, dst_file)
        print(f"目录复制成功：{src_path} -> {dst_path}")
    
    else:
        raise ValueError(f"无效的源路径类型：{src_path}")

def get_files_in_dir(directory: str, extensions: Optional[Union[list[str], str]] = None, sort_by: Optional[str] = None, reverse: bool = True, modify_date: Optional[str] = None, file_names: Optional[Union[list[str], str]] = None) -> list[str]:
    """
    获取指定目录下的文件，支持按文件属性排序和过滤
    :param directory: 目录路径
    :param extensions: 文件扩展名列表或单个扩展名字符串，如果为None则获取所有文件
    :param sort_by: 排序方式，可选值：
                  - 'size': 按文件大小排序
                  - 'name': 按文件名排序
                  - 'mtime': 按修改时间排序
                  - None: 不排序
    :param reverse: 是否降序排列，默认为True
    :param modify_date: 指定修改日期，格式为'YYYYMMDD'，如果指定则只返回该日期修改的文件
    :param file_names: 指定文件/目录列表，如果指定则优先返回这些文件或目录下的文件，支持通配符,以!开头表示不允许匹配
    :return: 文件路径列表
    """ 
    def get_file_attr(file_path: str, attr: str) -> Union[int, float, str]:
        try:
            if attr == 'size':
                return os.path.getsize(file_path)
            elif attr == 'name':
                return os.path.basename(file_path).lower()
            elif attr == 'mtime':
                return os.path.getmtime(file_path)
            return 0
        except OSError:
            return 0
    
    def is_file_modified_on_date(file_path: str, date_str: str) -> bool:
        try:
            mtime = os.path.getmtime(file_path)
            file_date = time.strftime('%Y%m%d', time.localtime(mtime))
            return file_date == date_str
        except OSError:
            return False
    
    # 允许匹配的文件/目录列表，不以!开头
    allow_match_file_names = []
    # 不允许匹配的文件/目录列表，以!开头
    disallow_match_file_names = []

    if file_names:
        # 标准化文件名列表，支持通配符
        if isinstance(file_names, str):
            file_names = [file_names]
        allow_match_file_names = [file_name.strip() for file_name in file_names if not file_name.strip().startswith('!')]
        disallow_match_file_names = [file_name.strip().replace('!', '') for file_name in file_names if file_name.strip().startswith('!')]

    # 收集文件
    files = []
    matched_files = set()  # 用于存储已匹配的文件     
    import fnmatch
    for root, dirs, filenames in os.walk(directory):
        # 如果指定了允许匹配的文件名列表，优先处理匹配的文件和目录
        if allow_match_file_names:
            # 检查子目录是否在允许匹配的文件名列表中
            for dir_name in dirs:
                if dir_name in allow_match_file_names:
                    # 如果子目录名匹配，添加该目录下的所有文件
                    dir_path = os.path.join(root, dir_name)
                    for sub_root, _, sub_files in os.walk(dir_path):
                        for filename in sub_files:
                            file_path = os.path.join(sub_root, filename)
                            matched_files.add(file_path)
                            files.append(file_path)
            
            # 检查文件名是否匹配
            for filename in filenames:
                # 支持通配符匹配，若pattern为完整文件名也能匹配
                if any(fnmatch.fnmatch(filename, pattern) or filename == pattern for pattern in allow_match_file_names):
                    file_path = os.path.join(root, filename)
                    if file_path in matched_files:
                        continue  # 跳过已匹配的文件
                    matched_files.add(file_path)
                    files.append(file_path)
        
        # 处理未匹配的文件
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if file_path in matched_files:
                continue  # 跳过已匹配的文件
            
            # 检查修改日期
            if modify_date and not is_file_modified_on_date(file_path, modify_date):
                continue
                    
            # 检查文件扩展名
            if extensions:
                if isinstance(extensions, str):
                    extensions = [extensions]
                if not any(filename.endswith(ext) for ext in extensions):
                    continue
            
            files.append(file_path)
    
    # 过滤不允许匹配的文件名
    if disallow_match_file_names:
        files = [file for file in files if not any(fnmatch.fnmatch(os.path.basename(file), pattern) for pattern in disallow_match_file_names)]
    # 根据指定的属性排序
    if sort_by in ['size', 'name', 'mtime']:
        return sorted(files, key=lambda x: get_file_attr(x, sort_by), reverse=reverse)
    
    return files

def split_files_by_size(files: list[str], max_size: int) -> list[list[str]]:
    """
    根据最大大小分批文件
    :param files: 文件路径列表
    :param max_size: 最大大小（字节）
    :return: 分批后的文件列表
    """
    batches = []
    current_batch = []
    current_size = 0

    for file in files:
        file_size = os.path.getsize(file)
        if current_size + file_size > max_size:
            batches.append(current_batch)
            current_batch = []
            current_size = 0
        current_batch.append(file)
        current_size += file_size

    if current_batch:
        batches.append(current_batch)

    return batches

def calculate_md5(file_path: str) -> Optional[str]:
    """
    计算文件的MD5哈希值
    :param file_path: 文件路径
    :return: MD5哈希值
    """
    import hashlib
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:  # 以二进制模式打开文件
            for chunk in iter(lambda: f.read(4096), b""):  # 每次读取4096字节
                hash_md5.update(chunk)  # 更新哈希对象
        return hash_md5.hexdigest()  # 返回16进制的哈希值
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return None
    except Exception as e:
        print(f"计算MD5时发生错误: {e}")
        return None

def get_file_md5_list(path: str, include_patterns: Optional[Union[list[str], str]] = None, exclude_patterns: Optional[Union[list[str], str]] = None) -> list[tuple[str, str]]:
    """
    文件/目录文件md5加密
    :param path: 路径（可以是文件或目录）
    :param include_patterns: 文件匹配模式字符串/列表，支持通配符，如 *.txt/['*.txt', '*_src_*']
    :param exclude_patterns: 文件排除模式字符串/列表，支持通配符，同include_pattern
    :return: MD5值列表
    """
    import fnmatch
    md5_entries = []
    if isinstance(include_patterns, str):
        include_patterns = [include_patterns]
    if isinstance(exclude_patterns, str):
        exclude_patterns = [exclude_patterns]
    if os.path.isfile(path):
        # 处理单个文件
        # 判断文件是否匹配排除模式
        if exclude_patterns and any(fnmatch.fnmatch(os.path.basename(path), pattern) for pattern in exclude_patterns):
            # print(f"文件 {path} 不在加密范围中")
            return []
        # 判断文件是否匹配指定模式
        if include_patterns and not any(fnmatch.fnmatch(os.path.basename(path), pattern) for pattern in include_patterns):
            # print(f"文件 {path} 不在加密范围中")
            return []
        md5_value = calculate_md5(path)
        if md5_value:
            filename = os.path.basename(path)
            md5_entries.append((md5_value, filename))
            print(f"文件 {path} 的MD5值为: {md5_value}")
    elif os.path.isdir(path):
        # 处理目录中的所有文件
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                # 判断文件是否匹配排除模式
                if exclude_patterns and any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                    # print(f"文件 {file_path} 不在加密范围中")
                    continue
                # 判断文件是否匹配指定模式
                if include_patterns and not any(fnmatch.fnmatch(file, pattern) for pattern in include_patterns):
                    # print(f"文件 {file_path} 不在加密范围中")
                    continue
                md5_value = calculate_md5(file_path)
                if md5_value:
                    filename = os.path.basename(file_path)
                    md5_entries.append((md5_value, filename))
                    print(f"文件 {file_path} 的MD5值为: {md5_value}")
    else:
        print(f"路径 {path} 无效")
    
    return md5_entries

def remove_files(paths: Union[list[str], str]) -> None:
    """
    删除文件或目录
    :param paths: 文件或目录路径列表，也可以是单个路径字符串
    :return: None
    """
    import shutil
    # 将单个路径转换为列表
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        if not os.path.exists(path):
            continue
        try:
            if os.path.isfile(path):
                # 删除文件
                os.remove(path)
            elif os.path.isdir(path):
                # 遍历目录下的所有文件和子目录
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        # 如果是子目录，递归删除
                        shutil.rmtree(item_path)
                    elif os.path.isfile(item_path):
                        # 如果是文件，直接删除
                        os.remove(item_path)

        except (OSError, shutil.Error) as e:
            print(f"删除文件/目录失败 {path}: {str(e)}")

def make_dir(dir_path: str) -> None:
    """
    创建目录
    :param dir_path: 目录路径
    :return: None
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"目录 {dir_path} 创建成功")
    else:
        # print(f"目录 {dir_path} 已存在")
        pass
