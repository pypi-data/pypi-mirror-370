import os
import random
import time
from multiprocessing import current_process, Process

from sthg_ontology_base.example.test_utils import session_factory,TGClient
from sthg_ontology_base import BaseModel
from sqlalchemy import or_

from sthg_ontology_base.utils.snowflake_generator import  SnowflakeIdGenerator


def test_group_by_common_query():
    """测试基础分组查询功能"""
    api_name = 'business_events'
    ontology_api_name = 'ApiName.ontology.7a4569fa-cbfb-4cbf-ae8f-f343560a65c5'
    client = TGClient(api_name, ontology_api_name)
    agg = client.ontology.objects._model_classes.get(api_name)
    obj_name = getattr(client.ontology.objects, api_name)
    result = obj_name.where(or_(agg.id==164,agg.id==160)).group_by(agg.event_type,agg.id).sum(agg.id).compute()
    print(result)


def test_common_count_query():
    """
    测试基础count查询
    """
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg = client.ontology.objects._model_classes.get(api_name)
    results = client.ontology.objects.agg.where().limit(10).offset(2).count_all()
    #results = client.ontology.objects.eq_vessel.where(eq_vessel.id<10).group_by(eq_vessel.ship_type).count("ship_type").sum("ship_type").having("count >2 and sum > 17").compute()
    print(results)

def test_common_join_count_query():
    """
    测试基础join的count查询
    """
    api_name = 'agg,aggt,aggr'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg,aggt,aggr = client.models
    results = client.ontology.objects.join([agg, aggt,aggr,agg], on_fields_list=[("ad_id", "ad_id"),("ad_id", "ad_id")], join_types=["right","left"]).where().limit(2).offset(0).count_all()
    #results = client.ontology.objects.eq_vessel.where(eq_vessel.id<10).group_by(eq_vessel.ship_type).count("ship_type").sum("ship_type").having("count >2 and sum > 17").compute()
    print(results)

def test_common_compute_query():
    """
    普通聚合查询-无分组
    """
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    results = client.ontology.objects.agg.where(agg.ad_id).count().compute()
    print(results)

def test_join_common_query():
    """
    普通join查询
    """
    api_name = 'eq_vessel, eq_vessel_model, sit_ship_deployment_del'
    ontology_api_name = 'ApiName.ontology.a71d3e1a-30fc-42fb-830f-24d364641c44'
    client = TGClient(api_name, ontology_api_name)
    eq_vessel, eq_vessel_model, sit_ship_deployment_del = client.models
    results = client.ontology.objects.join([eq_vessel, eq_vessel_model, sit_ship_deployment_del], on_fields_list=[("sys_code", "sys_code"),("id", "ship_id")], join_types=["right","left"]).where(eq_vessel.id==5).all()
    #results = client.ontology.objects.sit_ship_deployment_del.where().all()
    print(results)

def test_join_compute_query():
    """
    join分组查询
    """
    api_name = 'agg,aggt,aggr'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg,aggt,aggr = client.models
    results = client.ontology.objects.join([agg, aggt,agg], on_fields_list=[("ad_id", "ad_id"),("ad_id", "ad_id")], join_types=["right",'left']).where().group_by(aggt.clicks).count(agg.ad_id).having("clicks > 0").order_by(aggt.clicks.desc()).compute()
    print(results)


def test_having_compute_query():
    api_name = 'eq_vessel'
    ontology_api_name = 'ApiName.ontology.a71d3e1a-30fc-42fb-830f-24d364641c44'
    client = TGClient(api_name, ontology_api_name)
    eq_vessel = client.ontology.objects._model_classes.get(api_name)
    results = client.ontology.objects.eq_vessel.where(eq_vessel.id<10).count("ship_type").compute()
    print(results)

def test_create():

    """测试创建功能"""
    print("\n测试创建记录:")
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)

    new_item = client.ontology.objects.agg.create(
        ad_id=101,
        clicks = 101
    )
    print(f"创建成功: RID={new_item.ad_id}")

#
def test_update():
    """测试更新功能"""
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg = client.ontology.objects._model_classes.get(api_name)
    print("\n测试更新操作:")

    # 先创建测试数据
    # test_item = client.ontology.objects.agg.create(
    #             clicks = 1
    # )
    # print(test_item)

    # 执行更新
    updated_count = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).update(clicks=103)

    # print(f"更新了 {updated_count} 条记录")

    # 验证更新
    result = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).first()
    print(f"更新后数据: {result.__dict__}")
#
#
def test_delete():
    """测试删除功能"""
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg = client.ontology.objects._model_classes.get(api_name)
    print("\n测试删除操作:")

    # 执行删除
    deleted_count = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).delete()

    print(f"删除了 {deleted_count} 条记录")

    # 验证删除
    result = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).first()
    print(f"删除后查询结果: {'存在' if result else '不存在'}")


def test_create_dm():

        """测试创建功能"""
        print("\n测试创建记录:")
        api_name = 'agg'
        ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
        client = TGClient(api_name, ontology_api_name)

        st_data_list = []
        st_data_list.append({"clicks" : 101})
        st_data_list.append({"clicks" : 102})
        st_data_list.append({"clicks" : 103})
        st_data_list.append({"clicks" : 104})
        new_item = client.ontology.objects.agg.bulk_create(st_data_list)
        # test_item = client.ontology.objects.agg.create(
        #     ad_id=666,
        #     clicks=1234321
        # )
        # print(test_item)
        # new_item = client.ontology.objects.agg.create(
        #     ad_id=101,
        #     clicks = 101
        # )
        # print(f"创建成功: RID={new_item.ad_id}")


def test_create_generator_id():

        """测试创建功能"""
        print("\n测试创建记录:")
        api_name = 'xinjiana'
        ontology_api_name = 'ApiName.ontology.81b53fa5-d7f9-4a21-bb49-bcc078b1ccf8'
        client = TGClient(api_name,ontology_api_name)

        new_item = client.ontology.objects.xinjiana.create(
            age = "zhangsan"
        )
        print(new_item)
        l = [{
            "name":"mingzi",
            "age":"lisi"
        },
        {
            "age":"wangwu"
        }]
        new_item = client.ontology.objects.xinjiana.bulk_create(l)
        print(new_item)

def generator():
    # 只创建一个生成器实例
    # os.putenv("SEED", "0")
    os.environ['SEED'] = '0'
    g1 = SnowflakeIdGenerator()
    # os.putenv("SEED", "1")
    os.environ['SEED'] = '1'
    g2 = SnowflakeIdGenerator()
    print(os.getenv('SEED'))
    ids = set()
    for i in range(10000):
        if i % 2 == 0:
            print("使用生成器1",g1)
            generator = g1
        else:
            print("使用生成器2",g2)
            generator = g2
        # print("时间:", int(time.time() * 1000))
        # print("当前生成器:", generator.)
        print('process:',generator.process_id)
        print("worker:", generator.worker_id)
        snowflake_id1 = generator.generate_id()
        # print("sequence:", generator.sequence)
        ids.add(snowflake_id1)
        print(f" -- 生成的雪花ID: {snowflake_id1}")
        print("\n")
    print(f"生成的雪花ID数量: {len(ids)}")

    return ids




#
# def test_bulk_create(session_factory):
#     """测试批量插入功能"""
#     client = FoundryClient(session_factory)
#     print("\n测试批量插入功能:")
#
#
#
#     new_item = client.ontology.objects.OntologyModelWrite.create(
#         rid="test_009",
#         api_name="test_api9",
#         display_name="测试模型39",
#         create_uid="tester9"
#     )
#
#     data_list = []
#
#     for i in range(1, 5):
#         item_dict = {
#             "rid": "test_bulk_create"+str(i),
#             "api_name": "test_bulk_create_api"+str(i),
#             "display_name": "批量模型模型",
#             "create_uid": "tester"
#         }
#         data_list.append(item_dict)
#
#     # 测试批量插入
#     test_item = new_item.bulk_create(
#         data_list
#     )
#
#     print(test_item)
#
#
# def test_batch_delete(session_factory):
#     """测试批量删除功能"""
#     client = FoundryClient(session_factory)
#     print("\n测试删除操作:")
#
#
#
#     # 执行删除
#     deleted_count = client.ontology.objects.OntologyModelWrite.where(
#         OntologyModelWrite.display_name == "批量模型模型"
#     ).delete()
#
#     print(f"删除了 {deleted_count} 条记录")
#
#
#
# def test_batch_update(session_factory):
#     """测试批量更新功能"""
#     client = FoundryClient(session_factory)
#     print("\n测试批量更新功能:")
#
#
#
#     # 测试批量更新功能
#     update_count = client.ontology.objects.OntologyModelWrite.where(
#         OntologyModelWrite.display_name == "批量模型模型"
#     ).update(display_name="已更新模型", new_filed="新增字段值")
#
#     print(f"更新了 {update_count} 条记录")
#


if __name__ == "__main__":


    # 执行测试套件
    BaseModel.set_session_factory(session_factory)
    #test_common_compute_query()
    # test_join_common_query()
    #test_having_compute_query()
    # test_join_compute_query()
    # test_common_join_count_query()
    #test_common_count_query()
    #test_common_query()
    #test_query()
    #test_bulk_create(session_factory)
    # test_batch_delete(session_factory)
    # test_batch_update(session_factory)
    #test_create()
    # test_update()
    #test_delete()
    test_create_dm()
    # for i in range(10):
    # generator()
    # test_create_generator_id()
    # for j in range(10):
    #         # i = random.randint(0, 1)
    #         # print("i:",i)
    #         # random.seed(i)
    #         # p = random.randint(1, 100)
    #         # print(p)
    #         random.seed(1)
    #         p = random.randint(0, 1024)
    #         print(p)
    #         random.seed(0)
    #         p1 = random.randint(0, 1024)
    #         print(p1)
