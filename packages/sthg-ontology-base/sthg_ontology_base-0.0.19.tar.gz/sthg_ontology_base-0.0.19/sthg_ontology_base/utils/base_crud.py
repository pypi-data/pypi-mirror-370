from typing import TypeVar, Generic, Type, Any, List, Optional, Union

from sqlalchemy import (Column, and_,
                        select, union_all, inspect, null
                        )
from sqlalchemy.orm import declarative_base, aliased
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError, InvalidRequestError

from sqlalchemy import func
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy import or_
from sqlalchemy.sql import operators, text
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, TextClause

from sthg_ontology_base.utils.snowflake_generator import SnowflakeIdGenerator

# 类型变量
T = TypeVar('T', bound='BaseModel')

small_types = ['int','tinyint','smallint', 'mediumint']

Base = declarative_base()


class BaseModel(Base):
    """所有模型基类(不自动创建表)"""
    __abstract__ = True
    _source_model = None  # 存储源表模型类
    _session_factory = None  # [新增] 存储会话工厂
    _patched_sa_field = False  # 控制只补丁一次

    @classmethod
    def _patch_sa_fields(cls):
        if cls._patched_sa_field:
            return

        def starts_with(self, prefix: str):
            return self.ilike(f"{prefix}%")

        def contains_any_term(self, terms, fuzzy=False):
            """
            拓展方法：匹配任意一个词（空格分隔）
            terms: str | List[str]
            fuzzy: 暂不实现模糊匹配，仅保留参数用于兼容
            """
            if isinstance(terms, list):
                terms_str = " ".join(terms)
            else:
                terms_str = terms

            words = [word.strip() for word in terms_str.split() if word.strip()]
            return or_(*[self.ilike(f"%{word}%") for word in words])

        def contains_all_terms(self, terms, fuzzy=False):
            """匹配所有词（空格分隔）"""
            if isinstance(terms, list):
                terms_str = " ".join(terms)
            else:
                terms_str = terms

            words = [word.strip() for word in terms_str.split() if word.strip()]
            return and_(*[self.ilike(f"%{word}%") for word in words])

        def contains_all_terms_in_order(self, terms, fuzzy=False):
            """
            匹配所有词，按顺序，中间可以有其他字符。
            用 ILIKE + 拼接通配符方式完成，不再 Python 层判断。
            """
            if isinstance(terms, list):
                terms_str = " ".join(terms)
            else:
                terms_str = terms

            words = [word.strip().lower() for word in terms_str.split() if word.strip()]
            if not words:
                return True  # 空条件默认返回True（不筛选）

            # 形如 %foo%bar%baz%
            pattern = "%" + "%".join(words) + "%"
            return self.ilike(pattern)

        def is_null(self, value: bool = True):
            return self.is_(None) if value else self.isnot(None)

        InstrumentedAttribute.starts_with = starts_with
        InstrumentedAttribute.contains_any_term = contains_any_term
        InstrumentedAttribute.contains_all_terms = contains_all_terms
        InstrumentedAttribute.contains_all_terms_in_order = contains_all_terms_in_order
        InstrumentedAttribute.is_null = is_null

        cls._patched_sa_field = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._patch_sa_fields()

    @classmethod
    def set_session_factory(cls, session_factory):
        """设置会话工厂"""
        cls._session_factory = session_factory

    @classmethod
    def get_session(cls):
        """获取数据库会话"""
        if cls._session_factory is None:
            raise ValueError("Session factory not set. Please call set_session_factory() first.")
        return cls._session_factory()

    @classmethod
    def set_source_model(cls, source_model):
        """设置源表模型类"""
        cls._source_model = source_model

    @classmethod
    def get_source_model(cls) -> Optional[Type['BaseModel']]:
        """获取关联的源表模型类"""
        return cls._source_model

    @classmethod
    def get_primary_key(cls) -> Column:
        """获取模型的主键列"""
        pk_columns = inspect(cls).primary_key
        if len(pk_columns) != 1:
            raise ValueError(f"模型 {cls.__name__} 必须要有且只有一个主键")
        return pk_columns[0]

    @classmethod
    def where(cls, *conditions):
        """查询条件"""
        return QuerySet(cls, conditions)

    @classmethod
    def create(cls, **kwargs):
        """创建新记录"""
        # if 'is_delete' not in kwargs:
        #     if hasattr(cls, "is_delete"):
        #         kwargs['is_delete'] = False
        # 检查是否需要生成ID
        increment = {}
        pk_col = cls.get_primary_key()
        if cls._should_generate_id(kwargs):
            obj_type = str(pk_col.type.__visit_name__).lower()
            if pk_col.name not in kwargs:
                if obj_type in small_types:
                    raise ValueError("创建记录失败: 'int','tinyint','smallint', 'mediumint'类型的主键不支持自动生成主键值，数值类型的主键请使用BIGINT或自行传入主键")
                kwargs[pk_col.name] = cls._generate_id()

        obj = cls(**kwargs)
        db = cls.get_session()
        try:
            db.add(obj)
            db.commit()

            try:
                db.refresh(obj)
            except InvalidRequestError as e:
                db.rollback()
                types = small_types
                types.append('integer')
                if pk_col.type.__visit_name__.lower() in types:
                    raise RuntimeError(f"创建记录失败: 有可能主键值超出范围或者未传入主键: {str(e)}") from e
                raise RuntimeError(f"创建记录失败: {str(e)}") from e
            return obj
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"创建记录失败: 违反数据完整性约束 - {str(e)}") from e
        except OperationalError as e:
            db.rollback()
            if "Insert has filtered data in strict mode" in str(e):  # 检查是否是严格模式错误
                raise ValueError(f"数据校验失败（严格模式）: {str(e)}") from e
            else:
                raise ConnectionError(f"数据库连接问题: {str(e)}") from e
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"创建记录时发生数据库错误: {str(e)}") from e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"创建记录时发生未知错误: {str(e)}") from e
        finally:
            db.close()

    @classmethod
    def bulk_create(cls, data_list):
        """批量创建新记录
        Args:
            data_list (list[dict]): 包含多个记录属性的字典列表
        Returns:
            list: 成功创建的记录对象列表
        Raises:
            ValueError: 数据校验失败或违反完整性约束
            ConnectionError: 数据库连接问题
            RuntimeError: 其他数据库错误
        """
        if not isinstance(data_list, list):
            raise ValueError("输入数据必须是字典列表")

        if not data_list:
            return []

        # 处理默认值
        # for data in data_list:
        #     if 'is_delete' not in data and hasattr(cls, "is_delete"):
        #         data['is_delete'] = False

        pk_col = cls.get_primary_key()
        pk_name = pk_col.name

        obj_type = str(pk_col.type.__visit_name__).lower()  # 移到循环外，只计算一次

        have_pk_list = []
        not_pk_list = []
        for data in data_list:
            if pk_name in data.keys():
                have_pk_list.append(data)
            else:
                not_pk_list.append(data)
        if have_pk_list:
            if len(have_pk_list) != len(data_list):
                raise ValueError("批量创建记录失败: 主键必须都传或者都不传")
            else:
                if obj_type in small_types:
                    raise ValueError(
                        "创建记录失败: 'int','tinyint','smallint','mediumint'类型的主键不支持自动生成主键值，数值类型的主键请使用BIGINT或自行传入主键")
        if not_pk_list:
            if len(not_pk_list) != len(data_list):
                raise ValueError("批量创建记录失败: 主键必须都传或者都不传")
            else:
                if obj_type in small_types:
                    raise ValueError(
                        "创建记录失败: 'int','tinyint','smallint','mediumint'类型的主键不支持自动生成主键值，数值类型的主键请使用BIGINT或自行传入主键")


        # 为需要的记录生成主键
        for data in data_list:
            if cls._should_generate_id(data):
                data[pk_col.name] = cls._generate_id()

        db = cls.get_session()
        try:
            objects = [cls(**data) for data in data_list]
            db.bulk_save_objects(objects)
            db.commit()

            inserted_pks = [getattr(obj, pk_name) for obj in objects]
            if not inserted_pks:
                raise RuntimeError("未获取到任何主键值，可能插入失败")
            pk_attr = getattr(cls, pk_name)
            existing_objects = db.query(cls).filter(pk_attr.in_(inserted_pks)).all()

            # 3. 验证查询结果与插入数量一致
            if len(existing_objects) != len(inserted_pks):
                types = small_types
                types.append('integer')
                if pk_col.type.__visit_name__.lower() in types:
                    raise RuntimeError(f"创建记录失败: 有可能主键值超出范围或者未传入主键")
            # 如果需要获取带有ID的对象，可以改为使用returning（如果数据库支持）
            # 或者分批插入（根据数据库限制）
            return objects
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"批量创建记录失败: 违反数据完整性约束 - {str(e)}") from e
        except OperationalError as e:
            db.rollback()
            if "Insert has filtered data in strict mode" in str(e):
                raise ValueError(f"数据校验失败（严格模式）: {str(e)}") from e
            else:
                raise ConnectionError(f"数据库连接问题: {str(e)}") from e
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"批量创建记录时发生数据库错误: {str(e)}") from e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"批量创建记录时发生未知错误: {str(e)}") from e
        finally:
            db.close()


    @classmethod
    def _should_generate_id(cls, data: dict) -> bool:
        """检查是否需要生成ID"""
        pk_col = cls.get_primary_key()
        return pk_col.name not in data and not data.get(pk_col.name)

    @classmethod
    def _generate_id(cls):
        """生成雪花ID"""
        generator = SnowflakeIdGenerator()
        return generator.generate_id()


class QuerySet(Generic[T]):
    """查询集合，支持从回写表自动合并源表数据"""

    def __init__(self, model_class: Type[T], conditions=None):
        self.model_class = model_class
        self._conditions = conditions or []
        self._limit = None
        self._offset = None
        self._order_by = []
        self._disable_union = False
        self._group_by = []
        self._having_conditions = []
        self._aggregates = []

    def group_by(self, *columns):
        self._group_by = list(columns)
        return self

    def having(self, *conditions):
        for cond in conditions:
            if isinstance(cond, str):
                self._having_conditions.append(text(cond))  # 字符串自动转 text
            elif isinstance(cond, TextClause):
                self._having_conditions.append(cond)
            else:
                self._having_conditions.append(cond)  # 表达式直接加
        return self

    def count(self, column: Optional[Union[str, Column]] = None, label="count"):
        """默认 count(*) 或 count(column)"""
        if column is None:
            expr = func.count().label(label)
        else:
            expr = func.count(column if isinstance(column, Column) else getattr(self.model_class, column)).label(label)
        self._aggregates.append(expr)
        return self

    def avg(self, column: Union[str, Column], label="avg"):
        expr = func.avg(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def sum(self, column: Union[str, Column], label="sum"):
        expr = func.sum(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def max(self, column: Union[str, Column], label="max"):
        expr = func.max(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def min(self, column: Union[str, Column], label="min"):
        expr = func.min(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def _resolve_column(self, col):
        if isinstance(col, str):
            return getattr(self.model_class, col)
        elif isinstance(col, (Column, InstrumentedAttribute)):
            return col
        else:
            raise TypeError(f"不支持的列类型: {type(col)}，必须是 str 或 Column")

    def where(self, *conditions):
        """添加查询条件"""
        new_qs = QuerySet(self.model_class, self._conditions + list(conditions))
        new_qs._limit = self._limit
        new_qs._offset = self._offset
        new_qs._order_by = self._order_by.copy()
        new_qs._disable_union = self._disable_union
        return new_qs

    def limit(self, count: int):
        """限制结果数量"""
        self._limit = count
        return self

    def offset(self, offset: int):
        """设置结果偏移量"""
        self._offset = offset
        return self

    def get(self, pk_value):
        """
        根据主键值查询单条记录，支持合并表，返回字典。
        找不到返回 None，找到多条抛异常。
        """
        db = self.model_class.get_session()
        try:
            pk_cols = self.model_class.__mapper__.primary_key
            if not pk_cols:
                raise RuntimeError("模型未定义主键")

            if len(pk_cols) > 1:
                pk_col = pk_cols[0]  # 简化，只支持单主键
            else:
                pk_col = pk_cols[0]

            if self._get_source_model():
                # 合并表，走union子查询
                union_subq = self._build_union_query(db).subquery()
                alias = union_subq.alias("union_subq")
                subq_pk_col = getattr(alias.c, pk_col.key)
                stmt = select(alias).where(subq_pk_col == pk_value)
                result = db.execute(stmt).first()
                if not result:
                    return None
                return dict(result._mapping)  # Row对象转dict
            else:
                # 单表查询
                query = db.query(self.model_class).filter(pk_col == pk_value)
                # if hasattr(self.model_class, "is_delete"):
                #     query = query.filter(self.model_class.is_delete == False)
                result = query.first()
                if not result:
                    return None
                # 转换 ORM 对象为 dict，假设模型有 to_dict 方法
                if hasattr(result, "to_dict"):
                    return result.to_dict()
                else:
                    # 简单用__dict__过滤私有属性
                    return {k: v for k, v in vars(result).items() if not k.startswith('_')}
        finally:
            db.close()

    def order_by(self, *columns: Union[str, Column]):
        """设置排序字段"""
        self._order_by.extend(columns)
        return self

    def no_union(self):
        """禁用自动合并查询"""
        self._disable_union = True
        return self

    def _build_base_query(self, db):
        """构建基础查询"""
        try:
            query = db.query(self.model_class)
            # if hasattr(self.model_class, "is_delete"):
            #     self._conditions.append(or_(
            #     getattr(self.model_class, "is_delete") == False,
            #     getattr(self.model_class, "is_delete") == None
            # ))
            if self._conditions:
                query = query.filter(and_(*self._conditions))
            if self._order_by:
                order_clauses = []
                for order in self._order_by:
                    if isinstance(order, str):
                        order = getattr(self.model_class, order)
                    order_clauses.append(order)
                query = query.order_by(*order_clauses)
            if self._limit is not None:
                query = query.limit(self._limit)
            if self._offset is not None:
                query = query.offset(self._offset)
            return query
        except AttributeError as e:
            raise AttributeError(f"查询构建失败: 无效的属性引用 - {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"构建基础查询时发生错误: {str(e)}") from e

    def _get_source_model(self) -> Optional[Type[T]]:
        """获取关联的源表模型"""
        if self._disable_union:
            return None
        return self.model_class.get_source_model()

    def _map_main_to_writeback(self, source_model):
        """精确的字段映射，确保顺序和类型一致"""
        # 获取回写表的所有列，按原始顺序
        try:
            writeback_columns = [c for c in self.model_class.__table__.columns]

            mapping = []
            for wb_col in writeback_columns:
                # 检查主表是否有相同字段
                if hasattr(source_model, wb_col.name):
                    main_col = getattr(source_model, wb_col.name)
                    mapping.append(main_col.label(wb_col.name))
                else:
                    # 只有回写表特有的字段才填充NULL
                    mapping.append(null().label(wb_col.name))

            return mapping
        except Exception as e:
            raise RuntimeError(f"字段映射失败: {str(e)}") from e

    def _build_union_query(self, db):
        try:
            source_model = self._get_source_model()
            if not source_model:
                return self._build_base_query(db)

            # 获取主键
            main_pk = source_model.get_primary_key()
            writeback_pk = self.model_class.get_primary_key()
            # 构建字段映射（回写表 → 源表）
            main_select = self._map_main_to_writeback(source_model)
            # 回写表查询（未删除记录）
            writeback_query = select(*self.model_class.__table__.columns).where(
                self.model_class.is_delete == False
            )

            # 源表查询（不在回写表中的记录）
            ontology_query = select(*main_select).where(
                ~main_pk.in_(select(writeback_pk).where(self.model_class.is_delete == False))
            )

            # 先合并两个查询
            union_query = union_all(writeback_query, ontology_query)

            # 将合并查询作为子查询
            subquery = union_query.subquery()

            # 构建最终查询 - 从合并结果中筛选
            final_query = select(*subquery.c)

            # 应用过滤条件到合并后的结果
            if self._conditions:
                order_clauses = []
                for order in self._order_by:
                    if isinstance(order, str):
                        parts = order.strip().split()
                        col_name = parts[0].split('.')[-1]
                        direction = parts[1].upper() if len(parts) > 1 else None
                        col = subquery.c[col_name]
                        if direction == 'DESC':
                            col = col.desc()
                        elif direction == 'ASC':
                            col = col.asc()
                        order_clauses.append(col)
                    else:
                        # 可能是 UnaryExpression 或 Column
                        if hasattr(order, 'element'):
                            col_name = getattr(order.element, 'name', None)
                        else:
                            col_name = getattr(order, 'name', None)
                        if col_name and hasattr(subquery.c, col_name):
                            col = subquery.c[col_name]
                            # 判断排序方向
                            if hasattr(order, 'modifier'):
                                if order.modifier == operators.desc_op:
                                    col = col.desc()
                                elif order.modifier == operators.asc_op:
                                    col = col.asc()
                            order_clauses.append(col)
                        else:
                            order_clauses.append(order)

                    final_query = final_query.order_by(*order_clauses)

            # 添加分页
            if self._limit is not None:
                final_query = final_query.limit(self._limit)
            if self._offset is not None:
                final_query = final_query.offset(self._offset)
            print(final_query)
            return final_query
        except Exception as e:
            raise RuntimeError(f"构建联合查询失败: {str(e)}") from e

    def compute(self):
        db = self.model_class.get_session()

        if not self._aggregates:
            raise ValueError("未指定任何聚合函数")

        # 统一解析 group_by 列
        group_cols = []
        for col in self._group_by:
            if isinstance(col, (Column, InstrumentedAttribute)):
                group_cols.append(col)
            elif isinstance(col, str):
                group_cols.append(getattr(self.model_class, col))
            else:
                raise TypeError(f"group_by 参数无效，必须是 Column 或 字符串，但收到：{type(col)}")

        # 判断是否使用合并源表
        if self._get_source_model():
            source = self._build_union_query(db).subquery()
        else:
            source = self.model_class
            # #自动拼接 is_delete 条件（仅限未手动添加的情况）
            # if hasattr(self.model_class, "is_delete"):
            #     if not any(self._has_is_delete_condition(c) for c in self._conditions):
            #         self._conditions.append(
            #             or_(
            #                 getattr(self.model_class, "is_delete") == False,
            #                 getattr(self.model_class, "is_delete") == None
            #             )
            #         )

        # 统一处理聚合查询
        if not group_cols:
            # 无 group_by：select 聚合字段（如 count/sum/avg 等）
            agg_exprs = [
                self._resolve_column_from_subq(agg, source) if self._get_source_model() else agg
                for agg in self._aggregates
            ]
            stmt = select(*agg_exprs).select_from(source)
            if self._conditions:
                stmt = stmt.where(and_(*self._conditions))
        else:
            # 有 group_by：select group 字段 + 聚合字段
            if self._get_source_model():
                group_exprs = [getattr(source.c, col.key) for col in group_cols]
                agg_exprs = [self._resolve_column_from_subq(agg, source) for agg in self._aggregates]
            else:
                group_exprs = group_cols
                agg_exprs = self._aggregates

            stmt = select(*group_exprs, *agg_exprs).select_from(source)
            if self._conditions:
                stmt = stmt.where(and_(*self._conditions))
            stmt = stmt.group_by(*group_exprs)

            if self._having_conditions:
                if any(isinstance(h, TextClause) for h in self._having_conditions):
                    stmt = stmt.having(*self._having_conditions)
                else:
                    stmt = stmt.having(and_(*self._having_conditions))
            if self._order_by:
                stmt = stmt.order_by(*self._order_by)
            if self._limit is not None:
                stmt = stmt.limit(self._limit)
            if self._offset is not None:
                stmt = stmt.offset(self._offset)
        print(">> 聚合SQL:", str(stmt.compile(compile_kwargs={"literal_binds": True})))
        # 执行 SQL
        results = db.execute(stmt).fetchall()

        # 构造返回格式
        data = []
        for row in results:
            row = dict(row._mapping)  # 适配 SQLAlchemy 2.x
            group_data = {
                col.key if hasattr(col, 'key') else col.name: row.pop(col.key if hasattr(col, 'key') else col.name) for
                col in group_cols}
            metrics = [{"name": agg.name, "value": row.get(agg.name)} for agg in self._aggregates]
            data.append({
                "group": group_data,
                "metrics": metrics
            })

        return {
            "excludedItems": 0,
            "data": data
        }

    def _has_is_delete_condition(self, condition):
        """
        递归检查条件表达式中是否包含 is_delete 字段
        解决增加and和or条件报错的问题
        """
        if isinstance(condition, BooleanClauseList):
            # and_() or or_() 等产生的，递归进入
            return any(self._has_is_delete_condition(clause) for clause in condition.clauses)

        elif isinstance(condition, BinaryExpression):
            # 二元表达式，比如 Model.is_delete == False
            left = condition.left
            if hasattr(left, "key") and left.key == "is_delete":
                return True

        return False

    def _resolve_column_from_subq(self, agg_expr, subq):
        """
        将 func.xxx(model.column).label(...) 里的 column 替换为 subq.c.xxx
        """
        if hasattr(agg_expr, 'clauses'):
            args = list(agg_expr.clauses)
            if len(args) == 1 and hasattr(args[0], 'key'):
                col_key = args[0].key
                new_arg = getattr(subq.c, col_key)
                new_func = getattr(func, agg_expr.name)(new_arg)
                return new_func.label(agg_expr.name)
        return agg_expr

    def all(self) -> List[T]:
        """获取所有结果"""
        db = self.model_class.get_session()
        try:
            if self._get_source_model():
                result = db.execute(self._build_union_query(db))

                return [dict(row._mapping) for row in result]

            # 提取列字段，而不是 ORM 对象
            stmt = select(*[col for col in self.model_class.__table__.c])
            if self._conditions:
                stmt = stmt.where(and_(*self._conditions))
            if self._order_by:
                stmt = stmt.order_by(*self._order_by)
            if self._limit:
                stmt = stmt.limit(self._limit)
            if self._offset:
                stmt = stmt.offset(self._offset)
            print(">> SQL:", str(stmt.compile(compile_kwargs={"literal_binds": True})))

            result = db.execute(stmt)
            return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            raise RuntimeError(f"查询数据失败: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"获取所有结果时发生未知错误: {str(e)}") from e
        finally:
            db.close()

    def first(self) -> Optional[T]:
        """获取第一个结果"""
        db = self.model_class.get_session()
        try:
            if self._get_source_model():
                result = db.execute(self._build_union_query(db)).first()
                return self.model_class(**dict(result)) if result else None
            return self._build_base_query(db).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"查询第一条记录失败: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"获取第一条记录时发生未知错误: {str(e)}") from e
        finally:
            db.close()

    def count_all(self) -> int:
        """计数"""
        db = self.model_class.get_session()
        try:
            if self._get_source_model():
                union_query = self._build_union_query(db)

                count_query = select(func.count()).select_from(union_query.alias())
                return db.execute(count_query).scalar()
            # 计数去除分页和offset
            query = self._build_base_query(db)
            query = query.limit(None).offset(None)
            return query.count()
        except SQLAlchemyError as e:
            raise RuntimeError(f"计数操作失败: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"执行计数时发生未知错误: {str(e)}") from e
        finally:
            db.close()

    def update(self, **kwargs) -> int:
        """批量更新"""
        source_model = self._get_source_model()
        if not source_model:
            # 没有源表，直接更新
            db = self.model_class.get_session()
            try:
                query = db.query(self.model_class)
                if self._conditions:
                    query = query.filter(and_(*self._conditions))
                result = query.update(kwargs)
                db.commit()
                return result
            except IntegrityError as e:
                db.rollback()
                raise ValueError(f"更新记录失败: 违反数据完整性约束 - {str(e)}") from e
            except OperationalError as e:
                db.rollback()
                raise ConnectionError(f"数据库操作失败: 连接问题 - {str(e)}") from e
            except SQLAlchemyError as e:
                db.rollback()
                raise RuntimeError(f"更新记录时发生数据库错误: {str(e)}") from e
            except Exception as e:
                db.rollback()
                raise RuntimeError(f"更新记录时发生未知错误: {str(e)}") from e
            finally:
                db.close()

        # 处理有源表的情况
        db = self.model_class.get_session()
        try:
            # 1. 先查询符合条件的记录
            query = self._build_union_query(db)
            records = db.execute(query).fetchall()
            # 2. 对每条记录处理
            affected = 0
            pk_name = self.model_class.get_primary_key().name

            for record in records:
                # 获取主键值
                pk_value = getattr(record, pk_name)

                # 检查回写表是否已有记录
                existing = db.query(self.model_class).filter(
                    getattr(self.model_class, pk_name) == pk_value
                ).first()

                if existing:
                    # 更新现有记录
                    print(kwargs)
                    print(existing.new_filed)
                    for key, value in kwargs.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)

                    affected += 1
                else:
                    # 创建新记录
                    new_data = {**dict(record), **kwargs}
                    # if hasattr(self.model_class, "is_delete"):
                    #     new_data['is_delete'] = False
                    new_record = self.model_class(**new_data)
                    db.add(new_record)
                    affected += 1

            db.commit()
            return affected
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"批量更新失败: 违反数据完整性约束 - {str(e)}") from e
        except OperationalError as e:
            db.rollback()
            raise ConnectionError(f"数据库操作失败: 连接问题 - {str(e)}") from e
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"批量更新时发生数据库错误: {str(e)}") from e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"批量更新时发生未知错误: {str(e)}") from e
        finally:
            db.close()

    def delete(self) -> int:
        """批量删除"""
        source_model = self._get_source_model()
        if not source_model:
            # 没有源表，物理删除
            db = self.model_class.get_session()
            try:
                query = db.query(self.model_class)
                if self._conditions:
                    query = query.filter(and_(*self._conditions))
                result = query.delete()
                db.commit()
                return result
            except IntegrityError as e:
                db.rollback()
                raise ValueError(f"删除记录失败: 违反数据完整性约束 - {str(e)}") from e
            except OperationalError as e:
                db.rollback()
                raise ConnectionError(f"数据库操作失败: 连接问题 - {str(e)}") from e
            except SQLAlchemyError as e:
                db.rollback()
                raise RuntimeError(f"删除记录时发生数据库错误: {str(e)}") from e
            except Exception as e:
                db.rollback()
                raise RuntimeError(f"删除记录时发生未知错误: {str(e)}") from e
            finally:
                db.close()

        # 处理有源表的情况
        db = self.model_class.get_session()
        try:
            # 1. 先查询符合条件的记录
            query = self._build_union_query(db)
            records = db.execute(query).fetchall()

            # 2. 对每条记录处理
            affected = 0
            pk_name = self.model_class.get_primary_key().name

            for record in records:
                # 获取主键值
                pk_value = getattr(record, pk_name)

                # 检查回写表是否已有记录
                existing = db.query(self.model_class).filter(
                    getattr(self.model_class, pk_name) == pk_value
                ).first()

                if existing:
                    # 标记删除
                    existing.is_delete = True
                    affected += 1
                else:
                    # 创建删除记录
                    delete_data = {
                        pk_name: pk_value,
                    }
                    # 设置其他必要字段
                    for column in self.model_class.__table__.columns:
                        if column.name != pk_name and hasattr(record, column.name):
                            delete_data[column.name] = getattr(record, column.name)
                    delete_data['is_delete'] = True
                    delete_record = self.model_class(**delete_data)
                    db.add(delete_record)
                    affected += 1

            db.commit()
            return affected
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"批量删除失败: 违反数据完整性约束 - {str(e)}") from e
        except OperationalError as e:
            db.rollback()
            raise ConnectionError(f"数据库操作失败: 连接问题 - {str(e)}") from e
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"批量删除时发生数据库错误: {str(e)}") from e
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"批量删除时发生未知错误: {str(e)}") from e
        finally:
            db.close()

    def __iter__(self):
        return iter(self.all())

    def __repr__(self):
        return repr(self.all())


class JoinedQuerySet:
    """
    支持多表 join 查询，并保持每一步 join 的基准正确。
    """

    def __init__(self, models, on_fields_list=None, on_list=None, join_types=None):
        """
        :param models: 需要 join 的模型列表，比如 [ModelA, ModelB, ModelC]
        :param on_conditions: 每次 join 的 ON 条件列表，长度应为 len(models) - 1
        :param join_types: 每次 join 类型列表 (left, right, inner)，长度也应为 len(models) - 1
        """

        self.join_types = join_types
        self.filters = []
        self._limit = None
        self._offset = None
        self._order_by = None
        self._group_bys = []
        self._aggregates = []
        self._having_conditions = []
        # 自动为重复模型生成别名，避免表名冲突
        self.models = []
        self.model_aliases = []  # 保存别名字符串
        self.model_columns = []  # 保存每个模型的字段信息

        self.model_columns = []
        model_counter = {}
        for m in models:
            name = m.__name__
            # 先检查是否已存在，不存在则初始化为0
            if name not in model_counter:
                model_counter[name] = 0


            # 如果是第一个实例，直接使用原名
            # if model_counter.get(name):
            if model_counter[name] == 0:
                self.models.append(m)
                self.model_aliases.append(name.lower())
            else:
                # 从2开始的实例使用别名，从_2开始
                alias_name = f"{name.lower()}_{model_counter[name]}"
                alias = aliased(m, name=alias_name)
                self.models.append(alias)
                self.model_aliases.append(alias_name)
            # 递增计数
            model_counter[name] += 1

            # 收集字段信息，包含原始表名和字段名
            table_name = m.__table__.name
            columns = [
                {
                    'name': col.name,
                    'full_name': f"{table_name}-{col.name}"
                }
                for col in m.__table__.columns
            ]
            self.model_columns.append(columns)

        n_joins = len(models) - 1
        if on_fields_list:
            if len(on_fields_list) != n_joins:
                raise ValueError("on_fields_list 长度必须是模型数量减一")
            self.on_conditions = []
            left_model = self.models[0]
            for idx, right_model in enumerate(self.models[1:]):
                field_a, field_b = on_fields_list[idx]
                # 用 ORM 模型属性构造条件，支持别名
                left_col = getattr(left_model, field_a)
                right_col = getattr(right_model, field_b)
                join_type = self.join_types[idx]
                if join_type == "left":
                    on = left_col == right_col
                elif join_type == "right":
                    on = right_col == left_col
                    left_model = right_model  # 右连接后更新左模型
                else:  # inner join
                    on = left_col == right_col
                    left_model = right_model  # 内连接后更新左模型
                self.on_conditions.append(on)
        elif on_list:
            if len(on_list) != n_joins:
                raise ValueError("on_list 长度必须是模型数量减一")
            self.on_conditions = on_list
        else:
            raise ValueError("必须提供 on_fields_list 或 on_list")

    def where(self, *conditions):
        self.filters.extend(conditions)
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def offset(self, offset):
        self._offset = offset
        return self

    def order_by(self, *order_clauses):
        self._order_by = order_clauses
        return self

    def group_by(self, *columns):
        for col in columns:
            self._group_bys.append(self._resolve_column(col))
        return self

    def having(self, *conditions):
        for cond in conditions:
            if isinstance(cond, str):
                self._having_conditions.append(text(cond))  # 字符串自动转 text
            elif isinstance(cond, TextClause):
                self._having_conditions.append(cond)
            else:
                self._having_conditions.append(cond)  # 表达式直接加
        return self

    def count(self, column: Optional[Union[str, Column]] = None, label="count"):
        if column is None:
            expr = func.count().label(label)
        else:
            expr = func.count(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def sum(self, column: Union[str, Column], label="sum"):
        expr = func.sum(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def avg(self, column: Union[str, Column], label="avg"):
        expr = func.avg(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def min(self, column: Union[str, Column], label="min"):
        expr = func.min(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def max(self, column: Union[str, Column], label="max"):
        expr = func.max(self._resolve_column(column)).label(label)
        self._aggregates.append(expr)
        return self

    def _resolve_column(self, col):
        """解析列，支持字符串和Column对象，考虑别名"""
        if isinstance(col, str):
            # 支持"表别名_字段名"格式的字符串解析
            if '-' in col:
                alias_part, field_part = col.split('-', 1)
                for model, alias in zip(self.models, self.model_aliases):
                    if alias == alias_part and hasattr(model, field_part):
                        return getattr(model, field_part)

            # 如果不是"别名_字段"格式，尝试直接查找
            for model in self.models:
                if hasattr(model, col):
                    return getattr(model, col)
            raise AttributeError(f"找不到字段: {col}")
        elif isinstance(col, (Column, InstrumentedAttribute)):
            return col
        else:
            raise TypeError(f"不支持的列类型: {type(col)}，必须是 str 或 Column")


    def compute(self):
        with BaseModel.get_session() as db:
            if not self._aggregates:
                raise ValueError("未指定任何聚合函数")

            query = self._build_agg_query(db)
            print(">> 聚合SQL:", str(query.statement.compile(compile_kwargs={"literal_binds": True})))
            results = db.execute(query.statement).fetchall()

            data = []
            for row in results:
                row = dict(row._mapping)
                group_data = {
                    col.key if hasattr(col, 'key') else col.name: row.pop(col.key if hasattr(col, 'key') else col.name)
                    for col in self._group_bys
                }
                metrics = [{"name": agg.name, "value": row.get(agg.name)} for agg in self._aggregates]
                data.append({
                    "group": group_data,
                    "metrics": metrics
                })

            return {
                "excludedItems": 0,
                "data": data
            }

    def _build_agg_query(self, db):

        current_from = inspect(self.models[0]).selectable

        for i in range(len(self.on_conditions)):
            join_type = self.join_types[i]
            on = self.on_conditions[i]

            next_table = inspect(self.models[i + 1]).selectable

            if join_type == "left":
                current_from = current_from.outerjoin(next_table, on)
            elif join_type == "right":
                current_from = next_table.outerjoin(current_from, on)
            else:
                current_from = current_from.join(next_table, on)

        # ⬇ 先初始化 query 并绑定 from
        if self._group_bys:
            query = db.query(*self._group_bys, *self._aggregates).select_from(current_from)
            query = query.group_by(*self._group_bys)
        elif self._aggregates:
            query = db.query(*self._aggregates).select_from(current_from)
        else:
            query = db.query(*self.models).select_from(current_from)

        # ⬇ 再添加其他子句
        if self.filters:
            query = query.filter(*self.filters)
        if self._having_conditions:
            if any(isinstance(h, TextClause) for h in self._having_conditions):
                query = query.having(*self._having_conditions)
            else:
                query = query.having(and_(*self._having_conditions))
        if self._order_by:
            query = query.order_by(*self._order_by)
        if self._limit is not None:
            query = query.limit(self._limit)
        if self._offset is not None:
            query = query.offset(self._offset)

        return query

    def all(self):
        with BaseModel.get_session() as db:
            query = self._build_query(db)
            rows = query.all()
            return [self._row_to_dict(row) for row in rows]

    def count_all(self):
        with BaseModel.get_session() as db:
            query = self._build_query(db)
            query = query.limit(None).offset(None)
            return query.count()

    def first(self):
        with BaseModel.get_session() as db:
            query = self._build_query(db)
            row = query.first()
            return self._row_to_dict(row) if row else None

    def _build_query(self, db):
        # 先用 SQL Expression API 构造 from_clauses

        current_from = inspect(self.models[0]).selectable

        for i in range(len(self.on_conditions)):
            join_type = self.join_types[i]
            on = self.on_conditions[i]

            next_table = inspect(self.models[i + 1]).selectable

            if join_type == "left":
                current_from = current_from.outerjoin(next_table, on)
            elif join_type == "right":
                # 右连接只能用 next_table 做基表，模拟右连接
                current_from = next_table.outerjoin(current_from, on)
            else:
                current_from = current_from.join(next_table, on)

        # 创建 ORM 查询，注意用 query(*models) 返回 ORM 实例
        query = db.query(*self.models).select_from(current_from)

        if self.filters:
            query = query.filter(*self.filters)
        if self._order_by:
            query = query.order_by(*self._order_by)
        if self._limit is not None:
            query = query.limit(self._limit)
        if self._offset is not None:
            query = query.offset(self._offset)
        return query

    def _row_to_dict(self, row):
        """
        将查询结果转换为字典，确保字段格式为"别名_字段名"
        即使表中没有数据，也会返回所有字段（值为None）
        """
        result = {}

        for i, (obj, alias) in enumerate(zip(row, self.model_aliases)):
            # 获取当前模型的所有字段信息
            columns_info = self.model_columns[i]

            if obj is None:
                # 处理关联表无数据的情况
                for col_info in columns_info:
                    result_key = f"{alias}-{col_info['name']}"
                    result[result_key] = None
            else:
                # 处理有数据的情况
                for col_info in columns_info:
                    col_name = col_info['name']
                    result_key = f"{alias}-{col_name}"
                    # 获取字段值
                    result[result_key] = getattr(obj, col_name, None)

        return result

    def get_field_alias(self, model_index: int, field_name: str) -> str:
        """获取指定模型和字段的别名格式（别名_字段名）"""
        if model_index < 0 or model_index >= len(self.model_aliases):
            raise IndexError("模型索引超出范围")

        alias = self.model_aliases[model_index]
        return f"{alias}-{field_name}"

    def get_original_field_name(self, aliased_field: str) -> tuple:
        """
        将"别名_字段名"格式转换为原始模型索引和字段名
        返回 (model_index, field_name)
        """
        if '-' not in aliased_field:
            raise ValueError(f"字段名 {aliased_field} 不是'别名_字段名'格式")

        alias_part, field_part = aliased_field.split('-', 1)
        for idx, alias in enumerate(self.model_aliases):
            if alias == alias_part:
                return (idx, field_part)
        raise ValueError(f"找不到与别名 {alias_part} 匹配的模型")



class TGClient:
    """操作客户端"""

    def __init__(self):
        self.ontology = OntologyNamespace()



class OntologyNamespace:
    def __init__(self):
        self.objects = ObjectNamespace()


class ObjectNamespace:
    """动态模型查询集命名空间"""

    def __init__(self):
        self._model_classes = {
            cls.__name__: cls
            for cls in BaseModel.__subclasses__()
        }
        # for model_class in self._model_classes.values():
        #     model_class.set_session_factory(session_factory)

    def __getattr__(self, name):
        if name in self._model_classes:
            model_class = self._model_classes[name]

            class HybridQuerySet(QuerySet):
                @classmethod
                def create(cls, **kwargs):
                    return model_class.create(**kwargs)
                @classmethod
                def bulk_create(cls, data_list):
                    return model_class.bulk_create(data_list)

            return HybridQuerySet(model_class)
        raise AttributeError(f"Model '{name}' not found")

    def join(self, model_names, on_fields_list=None, on_list=None, join_types=None):
        if not isinstance(model_names, (list, tuple)) or len(model_names) < 2:
            raise ValueError("至少传入两个模型名组成列表")

        models = []
        for name in model_names:
            model = self._model_classes.get(name) if isinstance(name, str) else name
            if not model:
                raise ValueError(f"模型 {name} 不存在")
            models.append(model)

        n_joins = len(models) - 1
        if on_fields_list is None and on_list is None:
            raise ValueError("必须提供 on_fields_list 或 on_list")
        if on_fields_list and len(on_fields_list) != n_joins:
            raise ValueError("on_fields_list 长度必须是模型数量减一")
        if on_list and len(on_list) != n_joins:
            raise ValueError("on_list 长度必须是模型数量减一")

        if join_types is None:
            join_types = ["inner"] * n_joins
        elif len(join_types) != n_joins:
            raise ValueError("join_types 长度必须是模型数量减一")

        return JoinedQuerySet(models, on_fields_list=on_fields_list, on_list=on_list, join_types=join_types)


