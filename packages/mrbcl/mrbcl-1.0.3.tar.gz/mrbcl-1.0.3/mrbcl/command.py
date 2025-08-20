from typing import List, Union
import subprocess
from threading import Thread, Event
import time

def run_command_with_realtime_output(
    command: Union[str, List[str]], 
    working_directory: str = None,
    encoding: str = None,
    creationflags: int = 0
):
    """
    执行命令并实时输出结果
    :param command: 要执行的命令，可以是字符串或列表
    :param working_directory: 命令执行的工作目录，None表示当前目录
    :param encoding: 输出编码，默认None不设置
    :param creationflags: 创建进程的标志，默认0
    """
    shell = True if isinstance(command, str) else False
    # 启动子进程，实时输出 stdout 和 stderr
    process = subprocess.Popen(
        command,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding=encoding,  # 明确指定编码,这种方式可能会导致部分命令输出中文乱码，可以设置环境变量PYTHONIOENCODING控制
        errors='replace',  # 替换无法解码的字符
        cwd=working_directory,
        bufsize=1,  # 行缓冲
        universal_newlines=True,
        creationflags=creationflags
    )

    error_event = Event()
    error_message = []

    # 定义一个函数来实时读取并打印输出
    def print_output(stream, prefix=""):
        for line in stream:
            keywords = ["[error]", "npm error", "失败"]
            if any(kw in line.lower() for kw in keywords):
                error_message.append(line.strip())
                error_event.set()
            print(prefix + line.strip())

    # 启动两个线程分别读取 stdout 和 stderr
    stdout_thread = Thread(target=print_output, args=(process.stdout,))
    stderr_thread = Thread(target=print_output, args=(process.stderr,))

    stdout_thread.start()
    stderr_thread.start()

    # 主线程循环等待，检查 error_event
    while process.poll() is None:
        if error_event.is_set():
            process.terminate()
            stdout_thread.join()
            stderr_thread.join()
            raise RuntimeError(f"命令执行失败，检测到输出: {error_message[0]}")
        time.sleep(0.1)

    stdout_thread.join()
    stderr_thread.join()

    # 检查返回码
    if process.returncode == 0 and not error_event.is_set():
        pass
    elif error_event.is_set():
        raise RuntimeError(f"命令执行失败，检测到输出: {error_message[0]}")
    else:
        raise RuntimeError(f"命令执行失败，返回码：{process.returncode}")


def run_command_and_capture_output(
    command: Union[str, List[str]],
    working_directory: str = None,
    encoding: str = None,
    timeout: int = None,
    creationflags: int = 0
):
    """
    执行命令并捕获输出
    :param command: 要执行的命令，可以是字符串或列表
    :param working_directory: 命令执行的工作目录，None表示当前目录
    :param encoding: 输出编码，默认None不设置
    :param timeout: 超时时间(秒)，None表示不限制
    :param creationflags: 创建进程的标志，默认0
    """
    try:
        shell = True if isinstance(command, str) else False
        # 执行命令并捕获输出
        result = subprocess.run(
            command,
            shell=shell,
            cwd=working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True,
            encoding=encoding,  # 明确指定编码,这种方式可能会导致部分命令输出中文乱码，可以设置环境变量PYTHONIOENCODING控制
            errors='replace',
            creationflags=creationflags
        )

        # 打印所有输出（执行完成后）
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        # 检查返回码
        if result.returncode == 0:
            # print("命令执行成功")
            pass
        else:
            raise RuntimeError(f"命令执行失败，返回码：{result.returncode}")
    except Exception as e:
        raise e


def run_command_silently(
    command: Union[str, List[str]],
    working_directory: str = None,
    encoding: str = 'utf-8',
    timeout: int = None,
    startupinfo: subprocess.STARTUPINFO = None,
    creationflags: int = 0
):
    """
    静默执行命令，不关心输出
    :param command: 要执行的命令，可以是字符串或列表
    :param working_directory: 命令执行的工作目录，None表示当前目录
    :param encoding: 输出编码，默认utf-8
    :param timeout: 超时时间(秒)，None表示不限制
    :param startupinfo: 启动信息，None表示不设置
    :param creationflags: 创建进程的标志，默认0
    """
    shell = True if isinstance(command, str) else False
    try:
        # 执行命令
        result = subprocess.run(
            command,
            shell=shell,
            cwd=working_directory,
            stdout=subprocess.DEVNULL,  # 忽略标准输出
            stderr=subprocess.DEVNULL,  # 忽略标准错误
            timeout=timeout,
            encoding=encoding,  # 明确指定编码,这种方式可能会导致部分命令输出中文乱码，可以设置环境变量PYTHONIOENCODING控制
            errors='replace',  # 替换无法解码的字符
            check=True,  # 如果命令失败，会抛出异常
            startupinfo=startupinfo,
            creationflags=creationflags
        )
        # print("命令执行成功")
    except subprocess.CalledProcessError as e:
        raise e
    except Exception as e:
        raise e