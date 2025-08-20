import os
import yaml
import sys
import json
from typing import Any, Optional, List, Dict, ClassVar

# 配置文件管理类，使用get_instance()获取实例，不指定参数时，默认加载程序入口文件或打包exe所在目录下的配置文件。
# 可指定配置文件或目录：config_path="/path/to/config"或config_path="/path/to/config/config.yml"
# 可指定配置文件名：filename="log.yml"，不指定filename时，只会加载默认的config.yml、config.yaml、config.json文件，不会加载其他文件
# 可指定额外目录：extra_dir="extra"，在额外目录下查找配置文件。

# 支持多种配置文件格式，如yml、yaml、json。
# 支持嵌套访问，如config.get("database.host", "localhost")。
# 支持嵌套设置，如config.set("database.host", "localhost")。
# 支持保存配置文件，如config.save({"database": {"host": "localhost"}})。
# 支持获取配置文件所在目录，如config.get_config_dir()。
# 支持获取配置文件完整路径，如config.get_config_file()。

def get_app_base_path(specified_path: Optional[str] = None) -> str:
    """
    获取应用程序的基础路径。

    参数:
        specified_path (str, 可选): 指定路径。如果指定，返回该路径的目录。

    返回:
        str: 应用程序基础路径。
            - 打包环境：返回 exe 所在目录
            - 开发环境：返回主程序入口文件所在目录
    """
    # 打包环境强制使用exe目录
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    if specified_path:
        if os.path.isdir(specified_path):
            return specified_path
        return os.path.dirname(specified_path)
    import __main__
    return os.path.dirname(os.path.abspath(__main__.__file__))

def resolve_config_dir(specified_path: Optional[str] = None, extra_dir: Optional[str] = None) -> str:
    """
    解析并返回配置目录路径。

    参数:
        specified_path (str, 可选): 指定的配置路径（文件或目录）。
        extra_dir (str, 可选): 额外目录名，若指定则在该子目录下查找配置文件。

    返回:
        str: 最终使用的配置目录路径。

    规则:
        1. 打包环境下：始终返回 exe 所在目录；如指定 extra_dir，则返回 exe 目录下的 extra_dir 子目录。
        2. 指定了 specified_path 时：
           - 若为文件路径，返回其所在目录；
           - 若为目录路径，直接返回该目录。
        3. 未指定 specified_path 时，返回主程序入口文件所在目录；如指定 extra_dir，则返回该目录下的 extra_dir 子目录。
    """
    # 打包环境强制使用exe目录
    if getattr(sys, 'frozen', False):
        if extra_dir:
            return os.path.join(get_app_base_path(), extra_dir)
        return get_app_base_path()
    if specified_path:
        if os.path.isfile(specified_path):
            return os.path.dirname(specified_path)
        return specified_path
    if extra_dir:
        return os.path.join(get_app_base_path(), extra_dir)
    return get_app_base_path()

def load_config_file(file_path: str) -> dict:
    """
    加载指定的配置文件内容。

    参数:
        file_path (str): 配置文件的完整路径。

    返回:
        dict: 配置内容字典，若文件不存在或格式不支持则返回空字典。
    """
    try:
        if not os.path.exists(file_path):
            return {}
        file_ext = os.path.splitext(file_path)[1].lower()
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_ext in ['.yml', '.yaml']:
                config = yaml.safe_load(f)
            elif file_ext == '.json':
                config = json.load(f)
            else:
                print(f"不支持的配置文件格式: {file_ext}")
                return {}
        return config if config is not None else {}
    except Exception as e:
        print(f"加载配置文件时发生错误: {e}")
        return {}

class Config:
    """
    配置文件管理类，支持多种格式和嵌套访问。

    用法示例:
        1. 加载默认配置文件:
            config = Config.get_instance()
        2. 加载指定配置文件:
            config = Config.get_instance("/path/to/config.yml")
            # 或
            config = Config.get_instance(filename="log.yml")
        3. 加载指定目录下的指定文件:
            config = Config.get_instance("/path/to/config", "log.yml")

    注意:
        打包环境下，始终使用 exe 所在目录。
    """
    _instances: ClassVar[Dict[str, 'Config']] = {} # 用于存储不同配置文件的实例
    DEFAULT_CONFIG_FILES: ClassVar[List[str]] = ['config.yml', 'config.yaml', 'config.json']

    def __init__(self, config_path: Optional[str] = None, filename: Optional[str] = None) -> None:
        """
        初始化 Config 实例。

        参数:
            config_path (str, 可选): 配置文件路径或包含配置文件的目录路径。
            filename (str, 可选): 配置文件名，未指定时按默认顺序查找。
        """
        self.data: Dict[str, Any] = {}
        self.__config_dir: Optional[str] = None
        self.__config_file: Optional[str] = None
        self.load_config(config_path, filename)

    @classmethod
    def get_instance(cls, config_path: Optional[str] = None, filename: Optional[str] = None, extra_dir: Optional[str] = None) -> 'Config':
        """
        获取 Config 单例实例，不指定参数时，默认加载程序入口文件或打包exe所在目录下的配置文件。

        参数:
            config_path (str, 可选): 配置文件或目录路径。
            filename (str, 可选): 配置文件名，未指定时按默认顺序查找。
            extra_dir (str, 可选): 在当前配置目录的基础上，额外指定的子目录。

        返回:
            Config: 配置实例。

        示例:
            config = Config.get_instance()  # 加载默认配置
            log_config = Config.get_instance(filename="log.yml")  # 加载日志配置
            custom_config = Config.get_instance("/path/to/config", "custom.yml")  # 加载指定配置
        """
        instance_key = filename if filename else 'default'
        if instance_key not in cls._instances:
            cls._instances[instance_key] = cls(config_path, filename)
        elif config_path:
            cls._instances[instance_key].load_config(config_path, filename, extra_dir)
        return cls._instances[instance_key]

    def load_config(self, config_path: Optional[str] = None, filename: Optional[str] = None, extra_dir: Optional[str] = None) -> None:
        """
        加载配置文件内容。

        参数:
            config_path (str, 可选): 配置文件或目录的路径。
            filename (str, 可选): 要加载的配置文件名。
            extra_dir (str, 可选): 额外目录，若指定则在该目录下查找配置文件。

        示例:
            config = Config()
            config.load_config("/path/to/config", "config.yml")
        """
        self.__config_dir = resolve_config_dir(config_path, extra_dir)
        if config_path and os.path.isfile(config_path):
            self.__config_file = config_path
            self.data = load_config_file(config_path)
            return
        if filename:
            file_path = os.path.join(self.__config_dir, filename)
            if os.path.exists(file_path):
                self.__config_file = file_path
                self.data = load_config_file(file_path)
                return
            else:
                print(f"指定的配置文件不存在: {file_path}")
                return
        for default_file in self.DEFAULT_CONFIG_FILES:
            file_path = os.path.join(self.__config_dir, default_file)
            if os.path.exists(file_path):
                self.__config_file = file_path
                self.data = load_config_file(file_path)
                return
        print(f"在目录 {self.__config_dir} 中未找到任何可用的配置文件")

    def save(self, config_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存配置内容到文件。

        参数:
            config_data (dict, 可选): 要保存的配置数据，若为 None 则保存当前 self.data。

        返回:
            bool: 是否保存成功。

        示例:
            config = Config.get_instance()
            config.save({"database": {"host": "localhost"}})
        """
        if not self.__config_file:
            self.__config_file = os.path.join(self.__config_dir, self.DEFAULT_CONFIG_FILES[0])
        try:
            if config_data is not None:
                self.data = config_data
            file_ext = os.path.splitext(self.__config_file)[1].lower()
            with open(self.__config_file, 'w', encoding='utf-8') as f:
                if file_ext in ['.yml', '.yaml']:
                    yaml.dump(self.data, f, allow_unicode=True, sort_keys=False)
                elif file_ext == '.json':
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                else:
                    print(f"不支持的配置文件格式: {file_ext}")
                    return False
            return True
        except Exception as e:
            print(f"保存配置文件时发生错误: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套访问。

        参数:
            key (str): 配置键，支持点号分隔，如 "database.host"。
            default (Any, 可选): 默认值，未找到时返回。

        返回:
            Any: 配置值或默认值。

        示例:
            config = Config.get_instance()
            host = config.get("database.host", "localhost")
            port = config.get("database.port", 5432)
        """
        if not key:
            return default
        try:
            keys = key.split('.')
            value = self.data
            for k in keys:
                if not isinstance(value, dict):
                    return default
                value = value.get(k)
                if value is None:
                    return default
            return value
        except Exception:
            return default

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值，支持点号分隔的嵌套设置。

        参数:
            key (str): 配置键，支持点号分隔，如 "database.host"。
            value (Any): 要设置的值。

        示例:
            config = Config.get_instance()
            config.set("database.host", "localhost")
            config.set("app.debug", True)
        """
        if not key:
            return
        keys = key.split('.')
        current = self.data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def get_config_dir(self) -> str:
        """
        获取当前配置文件所在的目录路径。

        返回:
            str: 配置文件所在目录路径，若不存在则返回空字符串。

        示例:
            config = Config.get_instance()
            config_dir = config.get_config_dir()
            print(f"配置目录: {config_dir}")
        """
        return self.__config_dir if self.__config_dir else ""

    def get_config_file(self) -> str:
        """
        获取当前配置文件的完整路径。

        返回:
            str: 配置文件完整路径，若不存在则返回空字符串。

        示例:
            config = Config.get_instance()
            config_file = config.get_config_file()
            print(f"配置文件: {config_file}")
        """
        return self.__config_file if self.__config_file else ""