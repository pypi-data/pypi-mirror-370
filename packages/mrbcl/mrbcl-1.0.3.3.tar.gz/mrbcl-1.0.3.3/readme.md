## 使用说明
### 数据库操作模块 mrbcl.database.db
依赖于pony包实现，以oracle连接串演示。目前支持（mysql/oracle）    
oracle应用：pyinstaller打包需要添加`pyinstaller --hidden-import pony.orm.dbproviders.oracle xx.py`  
mysql应用：应该也需要，自行尝试
```python
from mrbcl.database.db import *
# 依靠config.yml配置文件获取连接参数，可查看下方配置文件区域
# 创建连接 此方式可用可不用
# db_con = Database("oracle", user="user", password="pwd", dsn='host:port/sid')
# 现已支持oracle、mysql自动生成实体


# 获取连接 目前支持oracle/mysql
db_con = get_orm_con()
# 定义实体（不指定_table_则默认类名为表名，oracle模式名和表名需大写）
# max_len属性针对单个字段设置最大值，目前默认为1000，当字段值太长时，执行修改会报错
class Test(db_con.Entity):
    _table_ = ("模式名", "表名")
    id = PrimaryKey(int)
    name = Optional(str, max_len=2000)
    age = Optional(int)

# 自动生成实体类
# 1.oracle/mysql通用：直接传入当前用户的表名
entity1 = generate_pony_entity("demo", db_con)
# 2.指定模式+表名（目前仅oracle）
entity2 = generate_pony_entity("schema.demo", db_con)

# 获取封装操作实例 方式1
db = Db(db_con, is_create_table=False, show_sql=True)
# 查询
data = db.query(Test, id=1)

# 初始化Db方式操作 方式2
init_db(db_con)
# 根据主键查询
result = entity1[1]
# 自定义条件查询 具体用法可参照pony官网文档
r1 = entity1.select(id=1).get()
```
### 达梦数据库操作模块 mrbcl.database.dmdb
依赖dmPython2.0实现，支持语句，自动生成实体，上下文管理器  
程序打包需要执行钩子文件，在包安装目录的hooks目录下hook-dmPython.py，可复制到应用所在目录   
执行命令：`pyinstaller --additional-hooks-dir=. xx.py` `.`标识当前目录，也可以指定其他目录
```python
from mrbcl.database.dmdb import *

# 依靠config.yml配置文件获取连接参数，可查看下方配置文件区域
# 添加自动生成实体，便捷使用增删查改
# 获取数据库连接1
# db = DmDatabase('ip:port', 'user', 'password')
# 获取数据库连接2
db = get_dm_con()
# 控制台显示执行sql
init_dm_db(db)

# 1.语句方式使用
# 查询
sql = "select * from test where id=1"
data = db.query(sql)
sql1 = "select * from test where id=?"
data1 = db.query(sql1, 1)
sql2 = "select * from test where id=:id"
data2 = db.query(sql2, id=1)
# 查询列表
data_list = db.query_list(sql)
...
# 执行语句
up_sql = "update test set name=2"
db.execute(up_sql)

# 2.自动生成实体使用
entity = generate_dm_entity("table_name", db)
# 查询单条
d1 = entity.query(id=1)
# 查询多条
d2 = entity.query_list(name='22')
# 分页查询
d3 = entity.query_page_list(1, 10, name="22")
# 修改
d1.name = '222'
entity.update(d1)
entity.update_dict(id=1, name='222')  # 参数需提供主键值
# 新增
entity.insert(id=3, name='555')
# 删除
entity.delete(id=2)
# 事务控制
try:
    db.begin()
    entity.update(d1)
    entity.update(d2)
    db.commit()
except RuntimeError as e:
    db.rollback()
# 上下文管理器方式操作，无需手动调用事务提交，回滚
with dm_session as db2:
    entity = generate_dm_entity("table_name", db2)
    d5 = entity.query(id=3)
    d5.name = '666'
    entity.update(d5)
...
```
### AES/SM4加密模块 mrbcl.utils.encipher  
- AES  
```python
from mrbcl.utils.encipher import AesUtil
from mrbcl.utils.common import base64_encode, base64_decode, hex_encode, hex_decode

aes_key = "aes_key"
aes_iv = "aes_iv"
plaintext = "123"
# 返回Base64
# 密文
aes_base64_ciphertext = base64_encode(AesUtil.encrypt_cbc(aes_key, aes_iv, plaintext))
# 明文
aes_base64_plaintext = AesUtil.decrypt_cbc(aes_key, aes_iv, base64_decode(aes_base64_ciphertext, True))
# 返回Hex
# 密文
aes_hex_ciphertext = hex_encode(AesUtil.encrypt_cbc(aes_key, aes_iv, plaintext))
# 明文
aes_hex_plaintext = AesUtil.decrypt_cbc(aes_key, aes_iv, hex_decode(aes_hex_ciphertext, True))
```
- SM4
```python
from mrbcl.utils.encipher import Sm4Util

sm4_key = "sm4_key"
plaintext = "123"
# 返回Base64
# 密文
sm4_base64_ciphertext = base64_encode(Sm4Util.encrypt_ecb(sm4_key, plaintext))
# 明文
sm4_base64_plaintext = Sm4Util.decrypt_ecb(sm4_key, base64_decode(sm4_base64_ciphertext, True))
# 返回Hex
# 密文
sm4_hex_ciphertext = hex_encode(Sm4Util.encrypt_ecb(sm4_key, plaintext))
# 明文
sm4_hex_plaintext = Sm4Util.decrypt_ecb(sm4_key, hex_decode(sm4_hex_ciphertext, True))
```
### 日志操作模块 lbTool.Logging
默认在程序所在目录新建 logs/app_yyyymmdd.log 日志文件
```python
from lbTool.Logging import get_logger

# 依靠log.yml配置文件获取参数
# 获取日志处理器 默认root文件,控制台、文件输出,可单独指定
logger = get_logger()
logger.info("xxx")
```