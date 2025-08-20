from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mrbcl',  # 包的名称
    version='1.0.1',  # 版本号
    author='mrbee',  # 作者名
    author_email='lcoolb@163.com',
    description='Multifunctional Toolset',  # 包的描述信息
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(),  # 包含的所有包 find_packages()会自动找到所有包,但模块必须有__init__.py文件
    package_data={
        'mrbcl': ['config/*', 'hooks/*'],
    },
    include_package_data=True,  # 包含数据文件
    install_requires=[  # 依赖的其他包
        'requests',  # http请求
        'gmSsl==3.2.2',  # SM4加解密
        'pycryptodome==3.18.0',  # AES加解密
        'pypdf2==3.0.1',  # pdf合并
        'pony==0.7.17',  # orm框架
        'cx-Oracle==8.3.0',  # oracle数据库连接
        'pymysql>=1.1.0',  # mysql数据库连接
        "dmPython>=2.5.5",  # dm数据库连接
        'comtypes==1.2.0',  # 将word转pdf
        'pyyaml==6.0.1'  # 解析yaml文件
    ],
    python_requires=">=3.6, <3.11"  # 项目依赖的Python版本
)
