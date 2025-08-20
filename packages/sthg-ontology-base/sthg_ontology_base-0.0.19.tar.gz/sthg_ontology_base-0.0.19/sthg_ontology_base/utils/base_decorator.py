import inspect


def function(func):
    """返回被装饰函数的源代码"""

    def wrapper(*args, **kwargs):
        # 获取函数的源代码
        source = inspect.getsource(func)
        return source

    return wrapper


def edit(*permission_checkers):
    """权限验证"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for checker in permission_checkers:
                # 如果是类（未实例化），自动实例化
                if isinstance(checker, type):
                    checker = checker()
                # 检查权限
                if not hasattr(checker, 'is_edit') or not checker.is_edit:
                    print(f"{checker.__class__.__name__} 没有编辑权限")
                    return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def create(*permission_checkers):
    """权限验证"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for checker in permission_checkers:
                if isinstance(checker, type):
                    checker = checker()
                if not hasattr(checker, 'is_create') or not checker.is_create:
                    print(f"{checker.__class__.__name__} 没有创建权限")
                    return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def delete(*permission_checkers):
    """权限验证"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for checker in permission_checkers:
                if isinstance(checker, type):
                    checker = checker()
                if not hasattr(checker, 'is_delete') or not checker.is_delete:
                    print(f"{checker.__class__.__name__} 没有删除权限")
                    return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


