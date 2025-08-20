from __future__ import annotations

import re
import uuid
from typing import TypeVar, Type, Generic, Optional, List, Dict, Literal, Union, Sequence, Any, Iterable, Callable
from sqlalchemy import select, delete, update, and_, func, desc, inspect, or_, asc, true
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, selectinload, RelationshipProperty, Load
from rb_commons.http.exceptions import NotFoundException
from rb_commons.orm.exceptions import DatabaseException, InternalException
from functools import lru_cache, wraps
from rb_commons.orm.querysets import Q, QJSON

ModelType = TypeVar('ModelType', bound=declarative_base())

def with_transaction_error_handling(func):
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except IntegrityError as e:
            await self.session.rollback()
            raise InternalException(f"Constraint violation: {str(e)}") from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseException(f"Database error: {str(e)}") from e
        except Exception as e:
            await self.session.rollback()
            raise InternalException(f"Unexpected error: {str(e)}") from e
    return wrapper

F = TypeVar("F", bound=Callable[..., Any])

def query_mutator(func: F) -> F:
    """
    Make a query‑builder method clone‑on‑write without touching its body.
    """
    @wraps(func)
    def wrapper(self: "BaseManager[Any]", *args, **kwargs):
        clone = self._clone()
        result = func(clone, *args, **kwargs)
        return result if result is not None else clone
    return wrapper


class BaseManager(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session
        self.filters: List[Any] = []
        self._filtered: bool = False
        self._limit: Optional[int] = None
        self._order_by: List[Any] = []
        self._joins: set[str] = set()

        mapper = inspect(self.model)
        self._column_keys = [c.key for c in mapper.mapper.column_attrs]

    def _clone(self) -> "BaseManager[ModelType]":
        """
        Shallow‑copy all mutable query state into a new manager instance.
        """
        clone = self.__class__(self.session)
        clone.filters = list(self.filters)
        clone._order_by = list(self._order_by)
        clone._limit = self._limit
        clone._joins = set(self._joins)
        clone._filtered = self._filtered
        return clone

    async def _smart_commit(self, instance: Optional[ModelType] = None) -> Optional[ModelType]:
        if not self.session.in_transaction():
            await self.session.commit()
        if instance is not None:
            await self.session.refresh(instance)
            return instance
        return None

    def _build_comparison(self, col, operator: str, value: Any):
        if operator == "eq":
            return col == value
        if operator == "ne":
            return col != value
        if operator == "gt":
            return col > value
        if operator == "lt":
            return col < value
        if operator == "gte":
            return col >= value
        if operator == "lte":
            return col <= value
        if operator == "in":
            return col.in_(value)
        if operator == "contains":
            return col.ilike(f"%{value}%")
        if operator == "null":
            return col.is_(None) if value else col.isnot(None)
        raise ValueError(f"Unsupported operator: {operator}")

    @lru_cache(maxsize=None)
    def _parse_lookup_meta(self, lookup: str):
        """
            One-time parse of "foo__bar__lt" into:
            - parts = ["foo","bar"]
            - operator="lt"
            - relationship_attr, column_attr pointers
        """

        parts = lookup.split("__")
        operator = "eq"
        if parts[-1] in {"eq", "ne", "gt", "lt", "gte", "lte", "in", "contains", "null"}:
            operator = parts.pop()

        current = self.model
        rel = None
        col = None
        for p in parts:
            a = getattr(current, p)
            if hasattr(a, "property") and isinstance(a.property, RelationshipProperty):
                rel = a
                current = a.property.mapper.class_
            else:
                col = a
        return parts, operator, rel, col

    def _parse_lookup(self, lookup: str, value: Any):
        parts, operator, rel_attr, col_attr = self._parse_lookup_meta(lookup)
        expr = self._build_comparison(col_attr, operator, value)

        if rel_attr:
            if rel_attr.property.uselist:
                return rel_attr.any(expr)
            else:
                return rel_attr.has(expr)

        return expr

    def _q_to_expr(self, q: Union[Q, QJSON]):
        if isinstance(q, QJSON):
            return self._parse_qjson(q)

        clauses: List[Any] = [self._parse_lookup(k, v) for k, v in q.lookups.items()]
        for child in q.children:
            clauses.append(self._q_to_expr(child))

        if not clauses:
            combined = true()
        elif q._operator == "OR":
            combined = or_(*clauses)
        else:
            combined = and_(*clauses)

        return ~combined if q.negated else combined

    def _parse_qjson(self, qjson: QJSON):
        col = getattr(self.model, qjson.field, None)
        if col is None:
            raise ValueError(f"Invalid JSON field: {qjson.field}")

        json_expr = col[qjson.key].astext

        if qjson.operator == "eq":
            return json_expr == str(qjson.value)
        if qjson.operator == "ne":
            return json_expr != str(qjson.value)
        if qjson.operator == "contains":
            return json_expr.ilike(f"%{qjson.value}%")
        if qjson.operator == "startswith":
            return json_expr.ilike(f"{qjson.value}%")
        if qjson.operator == "endswith":
            return json_expr.ilike(f"%{qjson.value}")
        if qjson.operator == "in":
            if not isinstance(qjson.value, (list, tuple, set)):
                raise ValueError(f"{qjson.field}[{qjson.key}]__in requires an iterable")
            return json_expr.in_(qjson.value)
        raise ValueError(f"Unsupported QJSON operator: {qjson.operator}")

    def _build_relation_loaders(
            self,
            model: Any,
            relations: Sequence[str] | None = None
    ) -> List[Load]:
        """
        Given e.g. ["media", "properties.property", "properties__property"],
        returns [
            selectinload(Product.media),
            selectinload(Product.properties).selectinload(Property.property)
        ].

        If `relations` is None or empty, recurse *all* relationships once (cycle-safe).
        """
        loaders: List[Load] = []

        if relations:
            for path in relations:
                parts = re.split(r"\.|\_\_", path)
                current_model = model
                loader: Load | None = None

                for part in parts:
                    attr = getattr(current_model, part, None)
                    if attr is None or not hasattr(attr, "property"):
                        raise ValueError(f"Invalid relationship path: {path!r}")
                    loader = selectinload(attr) if loader is None else loader.selectinload(attr)
                    current_model = attr.property.mapper.class_

                loaders.append(loader)

            return loaders

        visited = set()

        def recurse(curr_model: Any, curr_loader: Load | None = None):
            mapper = inspect(curr_model)
            if mapper in visited:
                return
            visited.add(mapper)

            for rel in mapper.relationships:
                attr = getattr(curr_model, rel.key)
                loader = (
                    selectinload(attr)
                    if curr_loader is None
                    else curr_loader.selectinload(attr)
                )
                loaders.append(loader)
                recurse(rel.mapper.class_, loader)

        recurse(model)
        return loaders

    async def _execute_query(self, stmt):
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return list({obj.id: obj for obj in rows}.values())

    @query_mutator
    def order_by(self, *columns: Any):
        """Collect ORDER BY clauses.
        """
        for col in columns:
            if isinstance(col, str):
                descending = col.startswith("-")
                field_name = col.lstrip("+-")
                sa_col = getattr(self.model, field_name, None)
                if sa_col is None:
                    raise ValueError(f"Invalid order_by field '{field_name}' for {self.model.__name__}")
                self._order_by.append(sa_col.desc() if descending else sa_col.asc())
            else:
                self._order_by.append(col)

        return self

    @query_mutator
    def filter(self, *expressions: Any, **lookups: Any) -> "BaseManager":
        self._filtered = True

        for k, v in lookups.items():
            root = k.split("__", 1)[0]
            if hasattr(self.model, root):
                attr = getattr(self.model, root)
                if hasattr(attr, "property") and isinstance(attr.property, RelationshipProperty):
                    self._joins.add(root)

            self.filters.append(self._parse_lookup(k, v))

        for expr in expressions:
            if isinstance(expr, Q) or isinstance(expr, QJSON):
                self.filters.append(self._q_to_expr(expr))
            else:
                self.filters.append(expr)

        return self

    @query_mutator
    def or_filter(self, *expressions: Any, **lookups: Any) -> "BaseManager[ModelType]":
        """Add one OR group (shortcut for `filter(Q() | Q())`)."""

        or_clauses: List[Any] = []
        for expr in expressions:
            if isinstance(expr, Q) or isinstance(expr, QJSON):
                or_clauses.append(self._q_to_expr(expr))
            else:
                or_clauses.append(expr)

        for k, v in lookups.items():
            or_clauses.append(self._parse_lookup(k, v))

        if or_clauses:
            self._filtered = True
            self.filters.append(or_(*or_clauses))
        return self

    @query_mutator
    def exclude(self, *expressions: Any, **lookups: Any) -> "BaseManager[ModelType]":
        """
        Exclude records that match the given conditions.
        This is the opposite of filter() - it adds NOT conditions.

        Args:
            *expressions: Q objects, QJSON objects, or SQLAlchemy expressions
            **lookups: Field lookups (same format as filter())

        Returns:
            BaseManager instance for method chaining

        Example:
            # Exclude users with specific names
            manager.exclude(name="John", email__contains="test")

            # Exclude using Q objects
            manager.exclude(Q(age__lt=18) | Q(status="inactive"))

            # Exclude using QJSON
            manager.exclude(QJSON("metadata", "type", "eq", "archived"))
        """
        self._filtered = True

        for k, v in lookups.items():
            root = k.split("__", 1)[0]
            if hasattr(self.model, root):
                attr = getattr(self.model, root)
                if hasattr(attr, "property") and isinstance(attr.property, RelationshipProperty):
                    self._joins.add(root)

            lookup_expr = self._parse_lookup(k, v)
            self.filters.append(~lookup_expr)

        for expr in expressions:
            if isinstance(expr, Q) or isinstance(expr, QJSON):
                q_expr = self._q_to_expr(expr)
                self.filters.append(~q_expr)
            else:
                self.filters.append(~expr)

        return self

    @query_mutator
    def limit(self, value: int) -> "BaseManager[ModelType]":
        self._limit = value
        return self

    async def all(self, relations: Optional[List[str]] = None):
        stmt = select(self.model)

        if relations:
            opts = self._build_relation_loaders(self.model, relations)
            stmt = stmt.options(*opts)

        if self.filters:
            stmt = stmt.filter(and_(*self.filters))
        if self._order_by:
            stmt = stmt.order_by(*self._order_by)
        if self._limit:
            stmt = stmt.limit(self._limit)

        return await self._execute_query(stmt)

    async def first(self, relations: Optional[Sequence[str]] = None):
        self._ensure_filtered()
        stmt = select(self.model).filter(and_(*self.filters))

        if self._order_by:
            stmt = stmt.order_by(*self._order_by)

        if relations:
            opts = self._build_relation_loaders(self.model, relations)
            stmt = stmt.options(*opts)

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def last(self, relations: Optional[Sequence[str]] = None):
        self._ensure_filtered()
        stmt = select(self.model).filter(and_(*self.filters))
        order = self._order_by or [self.model.id.desc()]
        stmt = stmt.order_by(*order[::-1])

        if relations:
            opts = self._build_relation_loaders(self.model, relations)
            stmt = stmt.options(*opts)

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def count(self) -> int | None:
        self._ensure_filtered()

        stmt = select(func.count(self.model.id)).select_from(self.model)
        if self.filters:
            stmt = stmt.where(and_(*self.filters))

        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def paginate(self, limit: int = 10, offset: int = 0, relations: Optional[Sequence[str]] = None):
        self._ensure_filtered()
        stmt = select(self.model).filter(and_(*self.filters))

        if relations:
            opts = self._build_relation_loaders(self.model, relations)
            stmt = stmt.options(*opts)

        if self._order_by:
            stmt = stmt.order_by(*self._order_by)
        stmt = stmt.limit(limit).offset(offset)
        return await self._execute_query(stmt)

    @with_transaction_error_handling
    async def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return await self._smart_commit(obj)

    @with_transaction_error_handling
    async def save(self, instance: ModelType):
        self.session.add(instance)
        await self.session.flush()
        return await self._smart_commit(instance)

    @with_transaction_error_handling
    async def lazy_save(self, instance: ModelType, relations: list[str] | None = None) -> ModelType:
        self.session.add(instance)
        await self.session.commit()

        if relations is None:
            from sqlalchemy.inspection import inspect
            mapper = inspect(self.model)
            relations = [r.key for r in mapper.relationships]

        if not relations:
            return instance

        stmt = select(self.model).filter_by(id=instance.id)
        stmt = stmt.options(*self._build_relation_loaders(self.model, relations))
        result = await self.session.execute(stmt)
        loaded = result.scalar_one_or_none()
        if loaded is None:
            raise NotFoundException("Could not reload after save", 404, "0001")
        return loaded

    @with_transaction_error_handling
    async def update(self, instance: ModelType, **fields):
        if not fields:
            raise InternalException("No fields provided for update")
        for k, v in fields.items():
            setattr(instance, k, v)
        self.session.add(instance)
        await self._smart_commit()
        return instance

    @with_transaction_error_handling
    async def update_by_filters(self, filters: Dict[str, Any], **fields):
        if not fields:
            raise InternalException("No fields provided for update")
        stmt = update(self.model).filter_by(**filters).values(**fields)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get(**filters)

    @with_transaction_error_handling
    async def delete(self, instance: Optional[ModelType] = None):
        if instance is not None:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        self._ensure_filtered()
        stmt = delete(self.model).where(and_(*self.filters))
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    @with_transaction_error_handling
    async def bulk_save(self, instances: Iterable[ModelType]):
        if not instances:
            return
        self.session.add_all(list(instances))
        await self.session.flush()
        if not self.session.in_transaction():
            await self.session.commit()

    @with_transaction_error_handling
    async def bulk_delete(self):
        self._ensure_filtered()
        stmt = delete(self.model).where(and_(*self.filters))
        result = await self.session.execute(stmt)
        await self._smart_commit()
        return result.rowcount

    async def get(self, pk: Union[str, int, uuid.UUID], relations: Optional[Sequence[str]] = None) -> Any:
        stmt = select(self.model).filter_by(id=pk)
        if relations:
            opts = self._build_relation_loaders(self.model, relations)
            stmt = stmt.options(*opts)

        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            raise NotFoundException("Object does not exist", 404, "0001")
        return instance

    async def is_exists(self):
        self._ensure_filtered()

        stmt = (
            select(self.model)
            .filter(and_(*self.filters))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    @query_mutator
    def has_relation(self, relation_name: str):
        relationship = getattr(self.model, relation_name)
        subquery = (
            select(1)
            .select_from(relationship.property.mapper.class_)
            .where(relationship.property.primaryjoin)
            .exists()
        )
        self.filters.append(subquery)
        self._filtered = True
        return self

    @query_mutator
    def sort_by(self, tokens: Sequence[str]) -> "BaseManager[ModelType]":
        """
        Dynamically apply ORDER BY clauses based on a list of "field" or "-field" tokens.
        Unknown fields are collected for Python-side sorting later.
        """
        self._invalid_sort_tokens = []
        self._order_by = []
        model = self.model

        for tok in tokens:
            if not tok:
                continue
            direction = desc if tok.startswith("-") else asc
            name = tok.lstrip("-")
            col = getattr(model, name, None)
            if col is None:
                self._invalid_sort_tokens.append(tok)
                continue
            self._order_by.append(direction(col))

        return self

    def model_to_dict(self, instance: ModelType, exclude: set[str] = None) -> dict:
        exclude = exclude or set()
        return {k: getattr(instance, k) for k in self._column_keys if k not in exclude}

    def _ensure_filtered(self):
        if not self._filtered:
            raise RuntimeError("You must call `filter()` before this operation.")

