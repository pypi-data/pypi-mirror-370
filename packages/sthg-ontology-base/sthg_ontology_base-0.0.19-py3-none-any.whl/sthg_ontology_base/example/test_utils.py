import time

import aiohttp

from contextlib import contextmanager

from sqlalchemy import MetaData
from sqlalchemy.engine import reflection
from sqlalchemy.ext.automap import automap_base
from sthg_ontology_base import BaseModel,OntologyNamespace
import json
import requests
from sqlalchemy.orm import sessionmaker,scoped_session
from urllib.parse import quote_plus
from sqlalchemy import (
    create_engine, Column
)


# password = "chenduomei"
# encoded_password = quote_plus(password)
# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://chenduomei:{encoded_password}@192.168.1.244:9030/ontology_data_source"
password = "Dev@02891"
encoded_password = quote_plus(password)
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://dev_user:{encoded_password}@192.168.1.171:9030/ontology_data_source_test"


class DatabaseManager:
    engine = None
    SessionLocal = None
    metadata = None
    Base = None
    db_schema = None

    def __init__(self, table_name=None):
        if DatabaseManager.engine is None:
            try:
                DatabaseManager.engine = create_engine(SQLALCHEMY_DATABASE_URL)
                DatabaseManager.SessionLocal = scoped_session(sessionmaker(
                    autocommit=False, autoflush=False, bind=DatabaseManager.engine))
                inspector = reflection.Inspector.from_engine(DatabaseManager.engine)
                DatabaseManager.db_schema = inspector.get_schema_names()
                DatabaseManager.metadata = MetaData()
                print("连接引擎：", DatabaseManager.engine)
            except Exception as e:
                raise ValueError(f"创建数据源失败，错误原因为: {e}")

        # 这里每次初始化时刷新表结构（如果指定表名只刷新对应表）
        self.refresh_metadata(table_name)

    def refresh_metadata(self, table_name=None):
        # 清空 MetaData 缓存
        DatabaseManager.metadata.clear()
        if table_name:
            DatabaseManager.metadata.reflect(bind=DatabaseManager.engine, only=[table_name], quote=True)
        else:
            DatabaseManager.metadata.reflect(bind=DatabaseManager.engine, quote=True)

        # 重新映射模型
        DatabaseManager.Base = automap_base(metadata=DatabaseManager.metadata)
        DatabaseManager.Base.prepare(engine=DatabaseManager.engine, reflect=False)
        print("元数据刷新完成")

    def get_session(self):
        return DatabaseManager.SessionLocal()

    @contextmanager
    def session(self):
        db = self.get_session()
        try:
            yield db
        finally:
            db.close()

    def get_model(self, table_name):
        if not table_name:
            return None

        if DatabaseManager.Base:
            table_model = DatabaseManager.Base.classes.get(table_name)
            if table_model:
                return table_model

        # 备用获取方式
        if DatabaseManager.db_schema and len(DatabaseManager.db_schema) == 1:
            model = DatabaseManager.metadata.tables.get(f"{DatabaseManager.db_schema[0]}.{table_name}", None)
        else:
            model = DatabaseManager.metadata.tables.get(table_name, None)
        return model

    def get_table_column(self, table_name):
        model = self.get_model(table_name)
        if hasattr(model, "columns"):
            return model.columns
        return None

    def table_is_exist(self, table_name):
        return table_name in DatabaseManager.metadata.tables


async def http_get(url: str, headers=None, params=None, encoding=None, timeout=10):
    """
    异步get
    :param url: 请求的URL
    :param headers: 请求头
    :param timeout: 超时时间，默认为10秒
    :param params: URL参数
    :param encoding: 编码方式
    :return: 解析后的JSON响应
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, timeout=timeout) as resp:
            text = await resp.text(encoding=encoding)
            return json.loads(text)


def http_post(*, url: str, headers=None, json_data=None, encoding=None, timeout=10):
    """
    同步post
    :param url: 请求的URL
    :param headers: 请求头
    :param timeout: 超时时间，默认为10秒
    :param json_data: 要发送的JSON数据
    :param encoding: 编码方式
    :return: 解析后的JSON响应
    """
    response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
    if encoding:
        response.encoding = encoding
    text = response.text
    return json.loads(text)


def getHtml(url, **kwargs):
    i = 0
    while i < 3:
        try:
            html = requests.get(url, timeout=10, **kwargs)
            if html.status_code == 200:
                return html
            else:
                return None
        except:
            print(i)
            print(url)
            i += 1


# 初始化数据库
class TGClient:
    """操作客户端"""

    def __init__(self, api_names, ontology_api_name):
        self.ontology = OntologyNamespace()
        if isinstance(api_names, str):
            api_names = api_names.split(",")  # 支持用逗号分隔
        self.models = []
        for api_name in api_names:
            api_name = api_name.strip()
            model = self.build_database_manager(api_name, ontology_api_name)
            self.models.append(model)  # 把注册好的模型收集到列表
        print(f"-----模型注册完成时间--------------{time.time()}")
        # self.build_database_manager(api_name, ontology_api_name)

    def create_and_register_model(self, primary_key, columns, class_name, table_name):
        """
        动态创建模型类并注册到全局命名空间
        :param class_name: 模型类名（如 "OntologyModelWrite"）
        :param table_name: 数据库表名（如 "om_ontology_wirtecall"）
        :return: 返回动态创建的类
        """
        # 定义模型属性（字段）
        #  清除特定表的元数据
        # 1. 清理旧注册
        # 从全局命名空间移除
        if class_name in globals():
            del globals()[class_name]

        # 从ObjectNamespace移除
        if hasattr(self.ontology.objects, '_model_classes') and class_name in self.ontology.objects._model_classes:
            del self.ontology.objects._model_classes[class_name]

        # 2. 清理SQLAlchemy元数据
        if table_name in BaseModel.metadata.tables:
            BaseModel.metadata.remove(BaseModel.metadata.tables[table_name])
        # 定义模型属性（字段）
        attrs = {
            '__tablename__': table_name,
            '__table_args__': {'extend_existing': True, 'autoload_replace': True}
        }
        for atr in columns:
            if primary_key == atr.name:
                attrs[atr.name] = Column(atr.type, primary_key=True)
            else:
                attrs[atr.name] = Column(atr.type)

        # 动态创建类（继承 BaseModel）
        dynamic_class = type(class_name, (BaseModel,), attrs)
        # 关键步骤：注入全局命名空间
        globals()[class_name] = dynamic_class  # 例如 bayesianontology

        # 关键步骤：手动添加到ObjectNamespace
        if not hasattr(self.ontology.objects, '_model_classes'):
            # 如果ObjectNamespace没有_model_classes属性，先创建
            self.ontology.objects._model_classes = {}

        # 添加到模型字典
        self.ontology.objects._model_classes[class_name] = dynamic_class

        return dynamic_class

    def build_ontology_model(self, api_name, ontology_api_name):
        """传入对象api名称构建对象类，包含回写类和原始数据类"""
        # 根据api_name查询model字段
        params = {
            'api_name': api_name,
            "ontology_api_name": ontology_api_name
        }
        return getHtml(url=f"http://192.168.1.245:31176/api/ontologyManager/v1/objectType/byname/info",
                       params=params)

        # return getHtml(url=f"http://192.168.1.245:31175/api/ontologyManager/v1/objectType/byname/info",
        #                params=params)

    # 动态创建并注册模型
    def build_database_manager(self, obj_apiname, ontology_api_name):
        data = self.build_ontology_model(obj_apiname, ontology_api_name)
        table_name = data.json().get("data",{}).get("properties",{}).get("obj_data_source",{}).get("use_data_source",{}).get(
            "table_name")
        if not table_name:
            table_name = data.json().get("data", {}).get('primitive_table_name')
        obj_writeback = data.json().get("data").get("properties").get("obj_writeback")
        # 创建 DatabaseManager 实例（首次调用会初始化连接引擎）
        db_manager = DatabaseManager()

        # 如果想针对某个表刷新元数据
        db_manager.refresh_metadata(table_name)

        # 获取该表的模型字段信息
        new_om_ontology_table_attrs = db_manager.get_table_column(table_name)
        # om_ontology_table_attrs = DatabaseManager(
        #     table_name=table_name)
        # new_om_ontology_table_attrs = om_ontology_table_attrs.get_table_column(table_name=table_name)
        primary_key = data.json().get("data").get('primary_key')
        # try:
        #     om_ontology_wirtecall_attrs = DatabaseManager(
        #         table_name=obj_writeback).get_table_column(table_name=obj_writeback)
        # except ValueError as e:
        #     print(e)
        #     om_ontology_wirtecall_attrs = None
        # except Exception as e:
        #     print(e)
        #     raise ValueError(str(e))

        model_cls = self.create_and_register_model(
            primary_key=primary_key,
            columns=new_om_ontology_table_attrs,
            class_name=obj_apiname,
            table_name=table_name
        )

        return model_cls  # 返回动态模型类




engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)