from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple, Any

from .PredicateOperator import PredicateOperator
from .Predicate import Predicate
from .TopLevel import TopLevel

if TYPE_CHECKING:
    from .NonTopLevel import NonTopLevel

import psycopg2
from .LevelMember import LevelMember
from ..engines.postgres import Postgres


class Attribute:
    def __init__(self,
                 name: str,
                 engine: Postgres,
                 level: NonTopLevel):
        self.name: str = name
        self._engine: Postgres = engine
        self.level: NonTopLevel = level
        self.level_members: List[LevelMember] = []
        self._unique_lm: set[LevelMember] = set()
        self.all_lms_loaded: bool = False
        self.order_by: Attribute | None = None
        self.order_asc: bool | None = None

    def members(self) -> list[LevelMember]:
        with self._get_db_conn() as conn:
            with conn.cursor() as curs:
                curs.execute(f"""
                    SELECT {self.name}, {self.level.key}
                    FROM {self.level.name}
                """)
                db_result: List[Tuple[str, ...]] = curs.fetchall()
        if db_result:
            self.all_lms_loaded = True
            result: list[LevelMember] = list(map(lambda x: LevelMember(x[0], self, key=x[1]), db_result))
            list(map(lambda x: self.add_level_member(x), result))
            return result
        else:
            raise AttributeError(f"The '{self.name}' Attribute does not contain any Level Members")

    def add_level_member(self, level: LevelMember) -> None:
        if level in self._unique_lm:
            return
        else:
            self.level_members.append(level)
            self._unique_lm.add(level)
            setattr(self, str(level.name), level)

    @property
    def get_sort_key(self) -> Attribute:
        return self.order_by

    def set_sort_key(self, key: Attribute, asc: bool = True) -> None:
        self.order_by = key
        self.order_asc = asc
        self.all_lms_loaded = False
        if type(self.level.parent) is not TopLevel:
            for lm in self.level.parent.level_member_attr.level_members:
                lm._children = []

    def __getattribute__(self, name: str) -> Any:
        try:
            if name == "__class__" or name == "shape":
                return super().__getattribute__(name)
            result = super().__getattribute__(name)
            if type(result) == LevelMember:
                return [x for x in self.level_members if x.name == result.name]
            return result
        except AttributeError:
            pass
        return self._fetch_lm_from_db_and_save(name)

    def __getitem__(self, item: str | int):
        for lm in self.level_members:
            if lm.name == item:
                return lm
        return self._fetch_lm_from_db_and_save(str(item))

    def __eq__(self, other) -> Predicate:
        return self._create_pred(other, PredicateOperator.EQ)

    def __gt__(self, other) -> Predicate:
        return self._create_pred(other, PredicateOperator.GT)

    def __lt__(self, other) -> Predicate:
        return self._create_pred(other, PredicateOperator.LT)

    def __ge__(self, other) -> Predicate:
        return self._create_pred(other, PredicateOperator.GEQ)

    def __le__(self, other) -> Predicate:
        return self._create_pred(other, PredicateOperator.LEQ)

    def _create_pred(self, other, comparison_operator: PredicateOperator) -> Predicate:
        left_child: Predicate = Predicate(None, self, None)
        right_child: Predicate = Predicate(None, other, None)
        return Predicate(left_child, comparison_operator, right_child)

    def _fetch_lm_from_db_and_save(self, item: str) -> LevelMember | list[LevelMember]:
        with self._get_db_conn() as conn:
            with conn.cursor() as curs:
                curs.execute(f"""
                    SELECT {self.level.key}, {self.name}
                    FROM {self.level.name}
                    WHERE {self.name} = '{item}'
                """)
                db_result = curs.fetchall()

        if db_result:
            result = []
            for key, name in db_result:
                level_member = LevelMember(name, self, key=key)
                setattr(self, str(item), level_member)
                if level_member not in self._unique_lm:
                    self.level_members.append(level_member)
                    self._unique_lm.add(level_member)
                result.append(level_member)
            return result[0] if len(result) == 1 else result
        else:
            raise AttributeError(f"'Unable to find the '{item}' Level Member on the {self.name} Attribute")

    def _get_db_conn(self):
        return psycopg2.connect(user=self._engine.user,
                                password=self._engine.password,
                                host=self._engine.host,
                                port=self._engine.port,
                                database=self._engine.dbname)

    def __repr__(self):
        return f"{self.name}"
