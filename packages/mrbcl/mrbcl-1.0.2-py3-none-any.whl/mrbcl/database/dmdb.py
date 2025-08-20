import dmPython

from mrbcl.config import Config
import os

config_path = os.path.join(os.getcwd(), "config", "config.yml")

def get_dm_con(contextmanager=False):
    """
    获取数据库连接
    :param contextmanager: 是否使用上下文管理器 默认False
    :return:
    """
    db_config = Config.get_instance(config_path, extra_dir="config").get("database")
    if db_config['driver'] == "dm":
        db_con = DmDatabase(contextmanager, f"{db_config['host']}:{db_config['port']}", f"{db_config['user']}",
                            f"{db_config['password']}")
    else:
        raise TypeError("driver must be 'dm'")
    return db_con


def init_dm_db(db_con, show_sql=True):
    """
    初始化db
    :param db_con: db对象
    :param show_sql: 是否在控制台显示语句
    :return:
    """
    db_con.show_sql = show_sql


def generate_dm_entity(table_name, db_obj):
    """
    生成达梦实体
    :param table_name: 表名（模式。表名）
    :param db_obj: 数据库连接对象
    :return:
    """
    # 表名大写
    table_name = table_name.upper()
    attrs = {}
    # 模式.表名 只获取表名为类名
    table_info = [word for word in table_name.split('.')]
    if len(table_info) == 2:
        class_name = table_info[1]
        schema = table_info[0]
        attrs['_table_'] = (schema, class_name)  # 设置模式 表名
        attrs['_class_name_'] = class_name.capitalize()  # 设置类名
        query_field_sql = f"SELECT COLUMN_NAME, DATA_TYPE,DATA_LENGTH,NULLABLE FROM ALL_TAB_COLUMNS WHERE OWNER = '{schema}' AND TABLE_NAME = '{class_name}'"
        query_key_sql = f"SELECT WM_CONCAT(B.COLUMN_NAME) PK_COLUMNS FROM ALL_CONSTRAINTS A,ALL_CONS_COLUMNS B WHERE A.CONSTRAINT_type='P' AND A.OWNER='{schema}' AND A.TABLE_NAME='{class_name}' AND B.OWNER=A.OWNER AND A.TABLE_NAME=B.TABLE_NAME GROUP BY A.OWNER,A.TABLE_NAME"
    else:
        class_name = table_info[0]
        query_field_sql = f"SELECT COLUMN_NAME, DATA_TYPE,DATA_LENGTH,NULLABLE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = '{class_name}'"
        query_key_sql = f"SELECT WM_CONCAT(B.COLUMN_NAME) PK_COLUMNS FROM ALL_CONSTRAINTS A,ALL_CONS_COLUMNS B WHERE A.CONSTRAINT_type='P' AND A.OWNER='{db_obj.user}' AND A.TABLE_NAME='{class_name}' AND B.OWNER=A.OWNER AND A.TABLE_NAME=B.TABLE_NAME GROUP BY A.OWNER,A.TABLE_NAME"
        attrs['_table_'] = class_name  # 设置表名
        attrs['_class_name_'] = class_name.capitalize()  # 设置类名
    attrs["_database_"] = db_obj  # 设置数据库对象
    # 查询表主键
    primary_dm_key = db_obj.query_sql(query_key_sql)

    # 查询表所有字段
    columns_info = db_obj.query_sql_list(query_field_sql)
    if len(columns_info) == 0:
        raise RuntimeError(f"未查询到表【{table_name}】的字段信息，核对当前用户下是否有此表。可以设置”模式名.表名“解决")

    # 根据字段类型设置字段属性
    for column in columns_info:
        if primary_dm_key and column['COLUMN_NAME'] == primary_dm_key['PK_COLUMNS']:
            attrs["_pk_column_"] = column['COLUMN_NAME'].lower()
            attrs["_pk_"] = None
            attrs[column['COLUMN_NAME'].lower()] = None
        else:
            attrs[column['COLUMN_NAME'].lower()] = None
    # 记录所有字段
    all_columns = [column['COLUMN_NAME'].lower() for column in columns_info]
    attrs["_columns_"] = all_columns
    # 记录除了主键以外的所有字段
    attrs["_columns_without_pk_"] = all_columns
    if primary_dm_key:
        attrs["_columns_without_pk_"] = [column['COLUMN_NAME'].lower() for column in columns_info if
                                         column['COLUMN_NAME'] != primary_dm_key['PK_COLUMNS']]

    # 动态创建实体类
    # dynamic_dm_entity = type(class_name.capitalize(), (EntityMeta,), attrs)
    # 这种方式创建可以得到实体方法提示
    dynamic_dm_entity = EntityMeta(class_name.capitalize(), (), attrs)
    return dynamic_dm_entity


class EntityMeta(type):
    """
    实体元类
    """

    def __get_table_name(cls):
        """
        获取数据库表名
        :return:
        """
        table_name = cls._table_
        if isinstance(cls._table_, tuple):
            table_name = '.'.join(str(x) for x in cls._table_)
        return table_name

    def query(cls, **kwargs):
        """
        查询单条数据
        :param kwargs: 查询参数
        :return:
        """
        table_name = cls.__get_table_name()
        sql = f"SELECT * FROM {table_name} where "
        where_condition = []
        for key, value in kwargs.items():
            if key.lower() not in cls._columns_:
                raise KeyError(key)
            where_condition.append(f"{key.upper()}=:{key}")
        sql += " AND ".join(where_condition)
        result = cls._database_.query_sql(sql, **kwargs)
        if result is None:
            return None
        for key, value in result.items():
            if key.lower() == cls._pk_column_:
                setattr(cls, "_pk_", value)  # 设置主键值
            setattr(cls, key.lower(), value)
        return cls

    def query_list(cls, **kwargs):
        """
        查询数据列表
        :param kwargs: 查询参数
        :return:
        """
        table_name = cls.__get_table_name()
        sql = f"SELECT * FROM {table_name} where "
        where_condition = []
        for key, value in kwargs.items():
            if key.lower() not in cls._columns_:
                raise KeyError(key)
            where_condition.append(f"{key.upper()}=:{key}")
        sql += " AND ".join(where_condition)
        result = cls._database_.query_sql_list(sql, **kwargs)
        if len(result) == 0:
            return result
        end_data = []
        for item in result:
            new_entity = type(cls._class_name_, (cls,), {})  # 生成对象新实例
            for key, value in item.items():
                if key.lower() == cls._pk_column_:
                    setattr(new_entity, "_pk_", value)  # 设置主键值
                setattr(new_entity, key.lower(), value)
            end_data.append(new_entity)
        return end_data

    def query_page_list(cls, page_num, page_size, **kwargs):
        """
        查询数据列表
        :param page_num: 页码
        :param page_size: 每页数量
        :param kwargs: 查询参数
        :return:
        """
        table_name = cls.__get_table_name()
        sql = f"SELECT * FROM {table_name} where "
        where_condition = []
        for key, value in kwargs.items():
            if key.lower() not in cls._columns_:
                raise KeyError(key)
            where_condition.append(f"{key.upper()}=:{key}")
        sql += " AND ".join(where_condition)
        # 拼接分页sql
        page_sql = f"SELECT * FROM (SELECT TMP_PAGE.*, ROWNUM AS RN FROM ({sql}) TMP_PAGE WHERE ROWNUM <= {page_num * page_size}) WHERE RN > {(page_num - 1) * page_size}"
        result = cls._database_.query_sql_list(page_sql, **kwargs)
        if len(result) == 0:
            return result
        end_data = []
        for item in result:
            new_entity = type(cls._class_name_, (cls,), {})  # 生成对象新实例
            for key, value in item.items():
                if key != "RN":  # 行号不赋值
                    if key.lower() == cls._pk_column_:
                        setattr(new_entity, "_pk_", value)  # 设置主键值
                    setattr(new_entity, key.lower(), value)
            end_data.append(new_entity)
        return end_data

    def query_count(cls, **kwargs):
        """
        查询总数
        :param kwargs: 查询参数
        :return:
        """
        table_name = cls.__get_table_name()
        sql = f"SELECT count(*) AS TOTAL_COUNT FROM {table_name} where "
        where_condition = []
        for key, value in kwargs.items():
            if key.lower() not in cls._columns_:
                raise KeyError(key)
            where_condition.append(f"{key.upper()}=:{key}")
        sql += " AND ".join(where_condition)
        result = cls._database_.query_sql(sql, **kwargs)
        return result['TOTAL_COUNT']

    def insert(cls, **kwargs):
        """
        新增数据
        :param kwargs: 参数字典
        :return:
        """
        table_name = cls.__get_table_name()
        for key, value in kwargs.items():
            if key.lower() not in cls._columns_:
                raise KeyError(key)
        fields = ",".join(item.upper() for item in kwargs.keys())
        values = ",".join(f":{item}" for item in kwargs.keys())
        sql = f"INSERT INTO {table_name}({fields}) VALUES ({values})"
        affect_rows = cls._database_.execute(sql, **kwargs)
        return affect_rows

    def update_dict(cls, **kwargs):
        """
        修改数据
        :param kwargs: 参数字典
        :return:
        """
        table_name = cls.__get_table_name()
        update_data = []
        key_str = ""
        all_keys = [key.lower() for key in kwargs.keys()]
        for key, value in kwargs.items():
            if key.lower() not in cls._columns_:
                raise KeyError(key)
            if cls._pk_column_ is None or cls._pk_column_ not in all_keys:
                raise RuntimeError(f"数据表{table_name}主键为空或未传入主键参数！")
            if key == cls._pk_column_:
                key_str = key.upper() + f"=:{key}"
            else:
                update_data.append(f"{key.upper()}=:{key}")
        update_str = ",".join(update_data)
        sql = f"UPDATE {table_name} SET {update_str} WHERE {key_str}"
        affect_rows = cls._database_.execute(sql, **kwargs)
        return affect_rows

    def update(cls, entity_data):
        """
        修改数据
        :param entity_data: 实体
        :return:
        """
        table_name = cls.__get_table_name()
        dict_data = dict([item for item in vars(entity_data).items() if not item[0].startswith('_')])
        if cls._pk_column_ is None or dict_data[cls._pk_column_] is None:
            raise RuntimeError(f"数据表{table_name}主键为空或不存在主键！")
        update_data = []
        key_str = ""
        for key, value in dict_data.items():
            if key == cls._pk_column_:
                key_str = key.upper() + f"=:{key}"
            else:
                update_data.append(f"{key.upper()}=:{key}")
        update_str = ",".join(update_data)
        sql = f"UPDATE {table_name} SET {update_str} WHERE {key_str}"
        affect_rows = cls._database_.execute(sql, **dict_data)
        return affect_rows

    def delete(cls, **kwargs):
        """
        删除数据
        :param kwargs: 参数字典
        :return:
        """
        table_name = cls.__get_table_name()
        delete_condition = []
        for key, value in kwargs.items():
            if key.lower() not in cls._columns_:
                raise KeyError(key)
            delete_condition.append(f"{key.upper()}=:{key}")
        delete_str = " AND ".join(delete_condition)
        sql = f"DELETE FROM {table_name} where {delete_str}"
        affect_rows = cls._database_.execute(sql, **kwargs)
        return affect_rows


class DmDatabase:
    """
    达梦操作类
    """

    def __init__(self, contextmanager, dsn=None, user=None, password=None):
        """
        初始化
        :param dsn: 连接描述
        :param user: 用户名
        :param password: 密码
        :param contextmanager: 是否使用上下文管理器标识
        """
        self.show_sql = False  # 是否展示语句，默认为False
        self.conn = None
        self.dsn = dsn
        self.user = user
        self.password = password
        self.contextmanager = contextmanager
        if not self.contextmanager:
            # 不使用上下文管理器时直接连接
            try:
                self.conn = dmPython.connect(dsn=self.dsn, user=self.user, password=self.password)
                print("\nConnection successful!\n")
            except dmPython.Error as ex:
                sqlstate = ex.args[0]
                print(f"Connection failed. SQLState: {sqlstate}")
                print(f"Error message: {ex}")

    def __del__(self):
        """
        析构函数，不使用上下文管理器时调用关闭连接方法
        :return:
        """
        if not self.contextmanager:
            self.close()

    def __enter__(self):
        """
        用于上下文管理器 with语句块进入时
        :return:
        """
        if self.dsn is None or self.user is None or self.password is None:
            db_config_global = Config.get_instance(config_path, extra_dir="config").get("database")
            if db_config_global['driver'] != "dm":
                raise TypeError("driver must be 'dm'")
            self.dsn = f"{db_config_global['host']}:{db_config_global['port']}"
            self.user = db_config_global['user']
            self.password = db_config_global['password']
        self.connect()
        self.conn.autoCommit = False  # 使用with语句时 事务改成手动模式
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        用于上下文管理器 with语句块退出时
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return:
        """
        # 目前一旦有错误就执行事务回滚
        if exc_type is None:
            self.commit()
            print("\nCommit")
        else:
            self.rollback()
            print("\nRollback")
        self.close()

    def connect(self):
        """
        连接数据库
        :return:
        """
        try:
            self.conn = dmPython.connect(dsn=self.dsn, user=self.user, password=self.password)
            print("\nConnection successful!\n")
        except dmPython.Error as ex:
            sqlstate = ex.args[0]
            print(f"Connection failed. SQLState: {sqlstate}")
            print(f"Error message: {ex}")

    def close(self):
        """
        关闭连接
        :return:
        """
        try:
            if self.conn is not None:
                self.conn.close()
                print("\nConnection closed.")
            else:
                print("\nConnection is already closed Or Connection error.")
        except AttributeError as e:
            raise e  # 如果连接过程中发生异常，self.conn 可能未定义

    def begin(self):
        """
        开启事务
        :return:
        """
        try:
            self.conn.autoCommit = False  # 关闭自动提交，即开启事务
        except dmPython.Error as ex:
            print(f"Failed to begin transaction. Error message: {ex}")
            raise ex

    def commit(self):
        """
        提交事务
        :return:
        """
        try:
            self.conn.commit()
        except dmPython.Error as ex:
            print(f"Failed to commit transaction. Error message: {ex}")
            raise ex

    def rollback(self):
        """
        回滚事务
        :return:
        """
        try:
            self.conn.rollback()
        except dmPython.Error as ex:
            print(f"Failed to roll back transaction. Error message: {ex}")
            raise ex

    def query_sql(self, sql, *args, **kwargs):
        try:
            cursor = self.conn.cursor()
            if args:
                cursor.execute(sql, *args)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
                    print(args)
            elif kwargs:
                cursor.execute(sql, **kwargs)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
                    print(kwargs)
            else:
                cursor.execute(sql)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
            result = cursor.fetchone()
            if result is None:
                return None
            # 查出当前查询的列名，保存到columns
            columns = [column[0] for column in cursor.description]
            # 组合字典形式{"name":"test","age":18}
            res_data = dict(zip(columns, result))
            cursor.close()
            return res_data
        except dmPython.Error as ex:
            print(f"Query execution failed. Error message: {ex}")
            return None

    def query_sql_list(self, sql, *args, **kwargs):
        try:
            cursor = self.conn.cursor()
            if args:
                cursor.execute(sql, *args)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
                    print(args)
            elif kwargs:
                cursor.execute(sql, **kwargs)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
                    print(kwargs)
            else:
                cursor.execute(sql)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
            result = cursor.fetchall()
            # 查出当前查询的列名，保存到columns
            columns = [column[0] for column in cursor.description]
            # 定义一个数组，用来保存每一组的数组，格式为字典形式{"name":"test","age":18}
            sub_resdata = []
            for row in result:
                # 循环遍历查询出来的结果，然后生成字典
                res_data = dict(zip(columns, row))
                sub_resdata.append(res_data)
            cursor.close()
            return sub_resdata
        except dmPython.Error as ex:
            print(f"Query execution failed. Error message: {ex}")
            return None

    def execute(self, sql, *args, **kwargs):
        try:
            cursor = self.conn.cursor()
            if args:
                cursor.execute(sql, *args)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
                    print(args)
            elif kwargs:
                cursor.execute(sql, **kwargs)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
                    print(kwargs)
            else:
                cursor.execute(sql)
                # 打印语句和参数
                if self.show_sql:
                    print(sql)
            result = cursor.rowcount  # 返回影响行数
            cursor.close()
            return result
        except dmPython.Error as ex:
            raise RuntimeError(ex)


# 上下文管理器使用对象 with dm_session as db:
dm_session = DmDatabase(True)
