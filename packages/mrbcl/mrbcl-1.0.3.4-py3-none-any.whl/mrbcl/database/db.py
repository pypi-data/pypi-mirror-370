import datetime

from mrbcl.config import Config
from pony.orm import *
from pony.orm.core import EntityMeta
import os

config_path = os.path.join(os.getcwd(), "config", "config.yml")

def get_orm_con():
    """
    获取数据库连接
    :return:
    """
    db_config = Config.get_instance(config_path, extra_dir="config").get("database")
    if db_config['driver'] == "oracle":
        db_con = Database("oracle", user=f"{db_config['user']}", password=f"{db_config['password']}",
                          dsn=f"{db_config['host']}:{db_config['port']}/{db_config['db_name']}")
    elif db_config['driver'] == "mysql":
        db_con = Database("mysql", host=f"{db_config['host']}", port=db_config['port'], user=f"{db_config['user']}",
                          password=f"{db_config['password']}",
                          db=f"{db_config['db_name']}")
    else:
        raise RuntimeError("不支持的数据库连接！")
    return db_con


def init_db(db_con, show_sql=True, is_create_table=False):
    """
    初始化db
    :param db_con: db对象
    :param show_sql: 是否在控制台显示语句
    :param is_create_table: 是否创建表
    :return:
    """
    if show_sql:
        # 控制台显示语句
        sql_debug(True)
    create_table = True if is_create_table is True else False
    # 根据实体关联表
    db_con.generate_mapping(create_tables=create_table)


def generate_pony_entity(table_name, db_obj):
    """
    生成实体类
    :param table_name: 表名（oracle可使用"模式.表名"）
    :param db_obj: 数据库连接对象
    :return:
    """
    db_config = Config.get_instance(config_path, extra_dir="config").get("database")
    if db_config['driver'] == "oracle":
        return __generate_oracle_entity(table_name, db_obj)
    elif db_config['driver'] == "mysql":
        return __generate_mysql_entity(table_name, db_obj)
    else:
        raise TypeError("暂未配置此数据库的实体生成规则")


def __generate_oracle_entity(table_name, db_obj):
    # 表名大写
    table_name = table_name.upper()
    attrs = {}
    # oracle 模式.表名 只获取表名为类名
    table_info = [word for word in table_name.split('.')]
    if len(table_info) == 2:
        class_name = table_info[1]
        schema = table_info[0]
        attrs['_table_'] = (schema, class_name)
        query_field_sql = f"SELECT COLUMN_NAME, DATA_TYPE,DATA_LENGTH,NULLABLE FROM ALL_TAB_COLUMNS WHERE OWNER = '{schema}' AND TABLE_NAME = '{class_name}'"
    else:
        class_name = table_info[0]
        query_field_sql = f"SELECT COLUMN_NAME, DATA_TYPE,DATA_LENGTH,NULLABLE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = '{class_name}'"
        attrs['_table_'] = class_name
    # 查询表主键
    query_key_sql = f"""
                    SELECT
                    cols.column_name
                FROM
                    all_cons_columns cols
                    JOIN all_constraints cons ON cols.constraint_name = cons.constraint_name
                WHERE
                    cons.constraint_type = 'P'
                    AND cols.table_name = '{class_name}'
                    """
    primary_key = db_obj.execute(query_key_sql).fetchone()

    # 查询表所有字段
    columns_info = db_obj.execute(query_field_sql).fetchall()
    if len(columns_info) == 0:
        raise RuntimeError(f"未查询到表【{table_name}】的字段信息，核对当前用户下是否有此表。可以设置[模式名.表名]解决")

    # 根据字段类型设置字段属性
    for column_name, data_type, data_length, nullable in columns_info:
        # 表字段类型转为Python对应的类型
        column_type = __oracle_to_python_type(data_type)

        if primary_key and column_name == primary_key[0]:
            attrs[column_name.lower()] = PrimaryKey(column_type)
        else:
            if nullable == 'Y':
                attrs[column_name.lower()] = Optional(column_type)
            else:
                attrs[column_name.lower()] = Required(column_type)
    # 动态创建实体类
    dynamic_oracle_entity = type(class_name.capitalize(), (db_obj.Entity,), attrs)
    return dynamic_oracle_entity


def __generate_mysql_entity(table_name, db_obj):
    # 表名小写
    table_name = table_name.lower()
    class_name = table_name.capitalize()
    attrs = {'_table_': class_name}
    query_field_sql = f"show columns from {table_name}"
    # 查询表所有字段
    columns_info = db_obj.execute(query_field_sql).fetchall()
    if len(columns_info) == 0:
        raise RuntimeError(f"未查询到表【{table_name}】的字段信息，核对数据表是否存在")

    # 根据字段类型设置字段属性
    for column_name, data_type, nullable, key_type, default, ext in columns_info:
        # 表字段类型转为Python对应的类型
        column_type = __mysql_to_python_type(data_type)
        if key_type == 'PRI':
            attrs[column_name.lower()] = PrimaryKey(column_type)
        else:
            if nullable == 'YES':
                attrs[column_name.lower()] = Optional(column_type)
            else:
                attrs[column_name.lower()] = Required(column_type)
    # 动态创建实体类
    # dynamic_mysql_entity = type(class_name.capitalize(), (db_obj.Entity,), attrs)
    # 这种方式创建可以得到实体方法提示
    dynamic_mysql_entity = EntityMeta(class_name.capitalize(), (db_obj.Entity,), attrs)
    return dynamic_mysql_entity


def __oracle_to_python_type(oracle_data_type):
    """
    Oracle字段类型转为Pyton类型
    :param oracle_data_type: 字段类型
    :return:
    """
    if oracle_data_type in ['VARCHAR2', 'NVARCHAR2', 'CHAR', 'CLOB']:
        return str
    elif oracle_data_type == 'NUMBER':
        from decimal import Decimal
        return Decimal
    elif oracle_data_type.startswith('DATE') or oracle_data_type.startswith('TIMESTAMP'):
        import datetime
        return datetime.datetime
    elif oracle_data_type == 'BLOB':
        return bytes
    elif oracle_data_type == 'FLOAT':
        return float
    elif oracle_data_type == 'INT':
        return int
    else:
        raise TypeError("Unrecognized oracle data type: " + oracle_data_type)


def __mysql_to_python_type(mysql_data_type):
    """
    Mysql字段类型转为Pyton类型
    :param mysql_data_type: 字段类型
    :return:
    """
    if mysql_data_type.startswith('varchar') or mysql_data_type.startswith('char'):
        return str
    elif mysql_data_type.startswith('int'):
        return int
    elif mysql_data_type.startswith('float') or mysql_data_type.startswith('double'):
        return float
    elif mysql_data_type.startswith('decimal'):
        from decimal import Decimal
        return Decimal
    elif mysql_data_type.startswith('blob'):
        return bytes
    elif mysql_data_type.startswith('date'):
        return datetime.date
    elif mysql_data_type.startswith('time'):
        return datetime.time
    elif mysql_data_type.startswith('datetime'):
        return datetime.datetime
    # 其他数据类型的映射可以根据需要进行扩展
    else:
        raise TypeError("Unrecognized mysql data type: " + mysql_data_type)


class Db:
    def __init__(self, db_con, is_create_table=False, show_sql=True):
        """
        获取数据库操作对象
        :param db_con: 数据库连接对象
        :param is_create_table: 是否创建数据表
        :param show_sql: 是否在控制台显示语句
        """
        self.db = db_con
        if show_sql:
            # 控制台显示语句
            sql_debug(True)
        create_table = True if is_create_table is True else False
        # 根据实体关联表
        self.db.generate_mapping(create_tables=create_table)

    @db_session
    def query(self, entity_cls, **filters):
        """
        查询单条
        :param entity_cls: 实体类
        :param filters: 查询条件
        :return:
        """
        return entity_cls.select(**filters).first()

    @db_session
    def query_list(self, entity_cls, **filters):
        """
        查询列表
        :param entity_cls: 实体类
        :param filters: 查询条件
        :return:
        """
        return entity_cls.select(**filters).fetch()[:]

    @db_session
    def query_page_list(self, entity_cls, page_num=1, page_size=10, **filters):
        """
        查询列表
        :param entity_cls: 实体类
        :param page_num: 页码
        :param page_size: 每页数量
        :param filters: 查询条件
        :return:
        """
        return entity_cls.select(**filters).page(page_num, page_size)[:]

    @db_session
    def query_count(self, entity_cls, **filters):
        """
        查询总数
        :param entity_cls: 实体类
        :param filters: 查询条件
        :return:
        """
        return entity_cls.select(**filters).count()

    @db_session
    def insert(self, entity_cls, **kwargs):
        """
        新增
        :param entity_cls: 实体类
        :param kwargs: 字段信息
        :return:
        """
        return entity_cls(**kwargs)

    @db_session
    def update(self, entity, **kwargs):
        """
        修改（需要使用`with db_session`语句块）
        :param entity: 实体
        :param kwargs: 需更新的数据
        :return:
        """
        for attr, value in kwargs.items():
            setattr(entity, attr, value)

    @db_session
    def remove(self, entity):
        """
        删除
        （执行查询后调用删除需要使用`with db_session`语句块，否则会提示会话中断）
        :param entity: 实体
        :return:
        """
        entity.delete()

    @db_session
    def remove_batch(self, entity_cls, **kwargs):
        """
        批量删除
        :param entity_cls: 实体类
        :param kwargs: 删除条件
        :return:
        """
        entity_cls.select(**kwargs).delete(bulk=True)

    @db_session
    def execute(self, sql, params=None, local_params=None):
        """
        执行语句
        :param sql: 原始语句
        :param params: 全局变量
        :param local_params: 可选参数
        :return:
        """
        return self.db.execute(sql, params, local_params)
