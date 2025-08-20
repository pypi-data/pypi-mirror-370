from __future__ import annotations
from typing import List, TYPE_CHECKING, Any

import psycopg2
from rdflib import Namespace

if TYPE_CHECKING:
    from .NonTopLevel import NonTopLevel
    from .Attribute import Attribute

EG = Namespace("http://example.org/")
QB4O = Namespace("http://purl.org/qb4olap/cubes/")


def remove_underscore_prefix(item):
    return item[1::]


def remove_uri_prefix(uri):
    return uri.rsplit("/")[-1]


def _construct_query(select_stmt: str, from_stmt: str, join: str, eq: str, order: str) -> str:
    return f"SELECT {select_stmt} FROM {from_stmt} WHERE {join} AND {eq} {order};"


class LevelMember:
    def __init__(self,
                 name: str | int | float,
                 attribute: Attribute,
                 parent: LevelMember = None,
                 key: str = ""):
        self._name: str | int | float = name
        self._children: list[LevelMember] = []
        self._attribute: Attribute = attribute
        self._parent: LevelMember | None = parent
        self._key: str = key

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def attribute(self):
        return self._attribute

    @property
    def parent(self) -> LevelMember:
        return self._parent

    @parent.setter
    def parent(self, value: LevelMember):
        self._parent = value

    @property
    def key(self):
        return self._key

    def children(self) -> List[LevelMember]:
        if self._children:
            return self._children
        else:
            children = self._fetch_children_from_db()
            if children:
                for key, name in children:
                    lm_name = name
                    lm = LevelMember(lm_name, self.attribute.level.child.level_member_attr, self, key=key)
                    # setattr(self.attribute.level.child.level_member_attr, str(lm_name), lm)
                    self.attribute.level.child.level_member_attr.add_level_member(lm)
                    self._children.append(lm)
                return self._children
            else:
                raise AttributeError(f"{self.name} does not have any children")

    def __getattr__(self, item) -> list[LevelMember] | LevelMember:
        return self._get_attribute(item)

    def __getitem__(self, item) -> list[LevelMember] | LevelMember:
        return self._get_attribute(item)

    def __repr__(self) -> str:
        return f"{self.name}"

    def __hash__(self) -> int:
        return hash((self.key, self.name))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, LevelMember) and self.key == other.key and self.name == other.name

    def _get_attribute(self, item: str) -> list[LevelMember] | LevelMember:
        # Need to look for item in dict because otherwise the Attribute's __getattribute__ method will start searching
        # the database for the item I am looking for (if the item is not contained in the Attribute instance).
        if item in self.attribute.level.child.level_member_attr.__dict__:
            children: list[LevelMember] | LevelMember = getattr(self.attribute.level.child.level_member_attr, item)
            if type(children) == list:
                result = next((x for x in children if x.parent == self), None)
                if result:
                    return result
            else:
                if children.parent == self:
                    return children
        children: list[LevelMember] = self._get_child_level_member(item)
        for child in children:
            self.attribute.level.child.level_member_attr.add_level_member(child)
        return children[0] if len(children) == 1 else children

    def _get_child_level_member(self, item: str) -> list[LevelMember]:
        select_clause: str = self._get_select_clause()
        from_clause: str = self._get_from_clause()
        where_clause: str = self._get_where_clause(item)

        query: str = " ".join([select_clause, from_clause, where_clause]) + ";"
        with self._get_db_conn() as conn:
            with conn.cursor() as curs:
                curs.execute(query)
                result = curs.fetchall()

        if result:
            child_lvl_member_attr: Attribute = self.attribute.level.child.level_member_attr
            return list(map(lambda x: LevelMember(x[1], child_lvl_member_attr, self, key=x[0]), result))
        else:
            raise AttributeError(f"Level Member {self.name} does not contain child LevelMember {item}")

    def _get_select_clause(self) -> str:
        child_lvl: NonTopLevel = self.attribute.level.child
        return f"SELECT {child_lvl.name}.{child_lvl.key}, {child_lvl.name}.{child_lvl.level_member_attr.name}"

    def _get_from_clause(self) -> str:
        current_lvl: NonTopLevel = self.attribute.level
        child_lvl: NonTopLevel = self.attribute.level.child
        return f"FROM {child_lvl.name} JOIN {current_lvl.name} ON {child_lvl.name}.{child_lvl.fk_name} = {current_lvl.name}.{current_lvl.key}"

    def _get_where_clause(self, item: str) -> str:
        current_lvl: NonTopLevel = self.attribute.level
        child_lvl: NonTopLevel = self.attribute.level.child
        try:
            int(item)
            where_clause: str = f"WHERE {current_lvl.name}.{current_lvl.key} = {self.key} AND {child_lvl.name}.{child_lvl.level_member_attr.name} = {item}"
        except ValueError:
            where_clause: str = f"WHERE {current_lvl.name}.{current_lvl.key} = {self.key} AND {child_lvl.name}.{child_lvl.level_member_attr.name} = '{item}'"
        return where_clause

    def _fetch_children_from_db(self):
        select_stmt = self._get_select_stmt_for_children()
        from_stmt = self._get_from_stmt_for_children()
        join_condition = self._get_join_condition_where_stmt_for_children()
        equality_condition = self._get_equality_condition_where_stmt_for_children()
        order_by_clause: str = self._get_order_by_clause_for_children()
        query = _construct_query(select_stmt, from_stmt, join_condition, equality_condition, order_by_clause)

        conn = self._get_db_conn()
        with conn.cursor() as curs:
            curs.execute(query)
            result = curs.fetchall()
        conn.close()

        return result

    def _get_order_by_clause_for_children(self) -> str:
        order_by: Attribute = self.attribute.level.child.level_member_attr.order_by
        return f"ORDER BY {order_by.name}" if order_by is not None else ""

    def _get_equality_condition_where_stmt_for_children(self) -> str:
        if type(self.name) is int:
            join_condition: str = f"{self.attribute.level.name}.{self.attribute.name} = {self.name}"
        else:
            join_condition: str = f"{self.attribute.level.name}.{self.attribute.name} = '{self.name}'"
        if type(self.key) is int:
            key_eq: str = f"{self.attribute.level.name}.{self.attribute.level.key} = {self.key}"
        else:
            key_eq: str = f"{self.attribute.level.name}.{self.attribute.level.key} = '{self.key}'"
        return join_condition + " AND " + key_eq

    def _get_join_condition_where_stmt_for_children(self) -> str:
        return f"{self.attribute.level.name}.{self.attribute.level.key} = {self.attribute.level.child.name}.{self.attribute.level.child.fk_name}"

    def _get_from_stmt_for_children(self) -> str:
        return f"{self.attribute.level.name}, {self.attribute.level.child.name}"

    def _get_select_stmt_for_children(self) -> str:
        return f"{self.attribute.level.child.name}.{self.attribute.level.child.key}, {self.attribute.level.child.name}.{self.attribute.level.child.level_member_attr.name}"

    def _get_db_conn(self):
        return psycopg2.connect(user=self.attribute._engine.user,
                                password=self.attribute._engine.password,
                                host=self.attribute._engine.host,
                                port=self.attribute._engine.port,
                                database=self.attribute._engine.dbname)

