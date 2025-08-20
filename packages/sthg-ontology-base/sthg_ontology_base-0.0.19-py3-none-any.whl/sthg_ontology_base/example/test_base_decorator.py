from sthg_ontology_base.utils.base_decorator import edit, create, delete, function



class PermissionCheckerA:
    def __init__(self):
        self.is_edit = True
        self.is_create = True
        self.is_delete = False


class PermissionCheckerB:
    def __init__(self):
        self.is_edit = False
        self.is_create = True
        self.is_delete = True


# 使用装饰器，可以传入类名或实例
@edit(PermissionCheckerA, PermissionCheckerB)  # 传入类名，自动实例化
def edit_operation():
    print("执行编辑操作")
    return "编辑成功"


@create(PermissionCheckerA, PermissionCheckerB)
def create_operation():
    print("执行创建操作")
    return "创建成功"


# 也可以传入实例
@delete(PermissionCheckerA, PermissionCheckerB)
def delete_operation():
    print("执行删除操作")
    return "删除成功"

@function
def func_test():
    print("执行函数")
    return "执行成功"

# 测试
print("函数操作结果:", func_test())  # "执行成功"
print("编辑操作结果:", edit_operation())  # PermissionCheckerB 没有编辑权限 → None
print("创建操作结果:", create_operation())  # 两个都有创建权限 → "创建成功"
print("删除操作结果:", delete_operation())  # PermissionCheckerA 没有删除权限 → None